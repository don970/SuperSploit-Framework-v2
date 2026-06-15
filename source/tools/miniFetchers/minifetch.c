#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h>
#include <arpa/inet.h>

void error(const char *msg) {
    perror(msg);
    exit(1);
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Usage: %s <url>\n", argv[0]);
        exit(1);
    }

    char *url = argv[1];
    char host[256];
    char path[1024] = "/";
    int port = 80;

    // Simple URL parser
    char *p = strstr(url, "://");
    if (p) {
        if (strncmp(url, "https", 5) == 0) port = 443;
        p += 3;
    } else {
        p = url;
    }
    
    char *s = strchr(p, '/');
    if (s) {
        size_t host_len = s - p;
        if (host_len >= sizeof(host)) host_len = sizeof(host) - 1;
        strncpy(host, p, host_len);
        host[host_len] = '\0';
        strncpy(path, s, sizeof(path) - 1);
    } else {
        strncpy(host, p, sizeof(host) - 1);
    }

    char *colon = strchr(host, ':');
    if (colon) {
        *colon = '\0';
        port = atoi(colon + 1);
    }

    if (port == 443) {
        char check_openssl[128];
        snprintf(check_openssl, sizeof(check_openssl), "which openssl > /dev/null 2>&1");
        if (system(check_openssl) != 0) {
            fprintf(stderr, "[-] Error: HTTPS requested but 'openssl' not found.\n");
            fprintf(stderr, "[*] Install 'openssl' or use curl/wget.\n");
            exit(1);
        }

        // Use openssl s_client as a fallback for HTTPS
        char cmd[2048];
        snprintf(cmd, sizeof(cmd), 
                 "printf \"GET %s HTTP/1.1\\r\\nHost: %s\\r\\nUser-Agent: SuperSploit-Minifetch/1.0\\r\\nConnection: close\\r\\n\\r\\n\" | "
                 "openssl s_client -connect %s:%d -quiet 2>/dev/null", 
                 path, host, host, port);

        FILE* fp = popen(cmd, "r");
        if (!fp) {
            fprintf(stderr, "[-] Error: Failed to execute openssl.\n");
            exit(1);
        }

        char response[4096];
        int body_started = 0;
        while (fgets(response, sizeof(response), fp)) {
            if (!body_started) {
                // Basic logic to skip headers in openssl output
                // Check for empty line marking end of HTTP headers
                if (strcmp(response, "\r\n") == 0 || strcmp(response, "\n") == 0) {
                    body_started = 1;
                }
            } else {
                printf("%s", response);
            }
        }
        pclose(fp);
        return 0;
    }

    struct hostent *server = gethostbyname(host);
    if (!server) {
        fprintf(stderr, "[-] Error: Could not resolve host '%s'\n", host);
        exit(1);
    }

    int sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd < 0) error("Error opening socket");

    struct sockaddr_in serv_addr;
    memset(&serv_addr, 0, sizeof(serv_addr));
    serv_addr.sin_family = AF_INET;
    memcpy(&serv_addr.sin_addr.s_addr, server->h_addr, server->h_length);
    serv_addr.sin_port = htons(port);

    if (connect(sockfd, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) < 0)
        error("Error connecting");

    char request[2048];
    snprintf(request, sizeof(request),
             "GET %s HTTP/1.1\r\n"
             "Host: %s\r\n"
             "User-Agent: SuperSploit-Minifetch/1.0\r\n"
             "Accept: */*\r\n"
             "Connection: close\r\n"
             "\r\n", path, host);

    if (write(sockfd, request, strlen(request)) < 0) error("Error writing to socket");

    char response[4096];
    int n;
    int body_started = 0;
    while ((n = read(sockfd, response, sizeof(response) - 1)) > 0) {
        response[n] = '\0';
        if (!body_started) {
            char *p = strstr(response, "\r\n\r\n");
            if (p) {
                printf("%s", p + 4);
                body_started = 1;
            }
        } else {
            printf("%s", response);
        }
    }

    close(sockfd);
    return 0;
}
