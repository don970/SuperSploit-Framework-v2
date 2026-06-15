#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <dlfcn.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h>
#include <arpa/inet.h>

// OpenSSL/BoringSSL Function Pointers
typedef void* (*f_SSL_CTX_new)(void* meth);
typedef void (*f_SSL_CTX_free)(void* ctx);
typedef void* (*f_TLS_client_method)(void);
typedef void* (*f_SSLv23_client_method)(void);
typedef void* (*f_SSL_new)(void* ctx);
typedef void (*f_SSL_free)(void* ssl);
typedef int (*f_SSL_set_fd)(void* ssl, int fd);
typedef int (*f_SSL_connect)(void* ssl);
typedef int (*f_SSL_write)(void* ssl, const void* buf, int num);
typedef int (*f_SSL_read)(void* ssl, void* buf, int num);
typedef int (*f_SSL_ctrl)(void* ssl, int cmd, long larg, void* parg);
typedef int (*f_SSL_set_tlsext_host_name)(void* s, const char* name);
typedef void (*f_SSL_CTX_set_verify)(void* ctx, int mode, void* callback);
typedef int (*f_SSL_CTX_set_cipher_list)(void* ctx, const char* str);
typedef unsigned long (*f_ERR_get_error)(void);
typedef void (*f_ERR_error_string_n)(unsigned long e, char* buf, size_t len);
typedef void (*f_SSL_library_init)(void);
typedef void (*f_SSL_load_error_strings)(void);

void* libssl = NULL;
void* libcrypto = NULL;

f_SSL_CTX_new p_SSL_CTX_new;
f_SSL_CTX_free p_SSL_CTX_free;
f_TLS_client_method p_TLS_client_method;
f_SSLv23_client_method p_SSLv23_client_method;
f_SSL_new p_SSL_new;
f_SSL_free p_SSL_free;
f_SSL_set_fd p_SSL_set_fd;
f_SSL_connect p_SSL_connect;
f_SSL_write p_SSL_write;
f_SSL_read p_SSL_read;
f_SSL_ctrl p_SSL_ctrl;
f_SSL_set_tlsext_host_name p_SSL_set_tlsext_host_name;
f_SSL_CTX_set_verify p_SSL_CTX_set_verify;
f_SSL_CTX_set_cipher_list p_SSL_CTX_set_cipher_list;
f_ERR_get_error p_ERR_get_error;
f_ERR_error_string_n p_ERR_error_string_n;
f_SSL_library_init p_SSL_library_init;
f_SSL_load_error_strings p_SSL_load_error_strings;

int load_libs() {
    libcrypto = dlopen("libcrypto.so", RTLD_NOW);
    libssl = dlopen("libssl.so", RTLD_NOW);
    
    if (!libssl || !libcrypto) {
        libcrypto = dlopen("/system/lib/libcrypto.so", RTLD_NOW);
        libssl = dlopen("/system/lib/libssl.so", RTLD_NOW);
    }

    if (!libssl || !libcrypto) return 0;

    p_SSL_CTX_new = (f_SSL_CTX_new)dlsym(libssl, "SSL_CTX_new");
    p_SSL_CTX_free = (f_SSL_CTX_free)dlsym(libssl, "SSL_CTX_free");
    p_TLS_client_method = (f_TLS_client_method)dlsym(libssl, "TLS_client_method");
    p_SSLv23_client_method = (f_SSLv23_client_method)dlsym(libssl, "SSLv23_client_method");
    p_SSL_new = (f_SSL_new)dlsym(libssl, "SSL_new");
    p_SSL_free = (f_SSL_free)dlsym(libssl, "SSL_free");
    p_SSL_set_fd = (f_SSL_set_fd)dlsym(libssl, "SSL_set_fd");
    p_SSL_connect = (f_SSL_connect)dlsym(libssl, "SSL_connect");
    p_SSL_write = (f_SSL_write)dlsym(libssl, "SSL_write");
    p_SSL_read = (f_SSL_read)dlsym(libssl, "SSL_read");
    p_SSL_ctrl = (f_SSL_ctrl)dlsym(libssl, "SSL_ctrl");
    p_SSL_set_tlsext_host_name = (f_SSL_set_tlsext_host_name)dlsym(libssl, "SSL_set_tlsext_host_name");
    p_SSL_CTX_set_verify = (f_SSL_CTX_set_verify)dlsym(libssl, "SSL_CTX_set_verify");
    p_SSL_CTX_set_cipher_list = (f_SSL_CTX_set_cipher_list)dlsym(libssl, "SSL_CTX_set_cipher_list");
    p_SSL_library_init = (f_SSL_library_init)dlsym(libssl, "SSL_library_init");
    p_SSL_load_error_strings = (f_SSL_load_error_strings)dlsym(libssl, "SSL_load_error_strings");
    
    p_ERR_get_error = (f_ERR_get_error)dlsym(libcrypto, "ERR_get_error");
    p_ERR_error_string_n = (f_ERR_error_string_n)dlsym(libcrypto, "ERR_error_string_n");

    if (p_SSL_library_init) p_SSL_library_init();
    if (p_SSL_load_error_strings) p_SSL_load_error_strings();

    return (p_SSL_CTX_new && p_SSL_new && p_SSL_connect);
}

void print_ssl_error() {
    if (!p_ERR_get_error || !p_ERR_error_string_n) return;
    unsigned long err = p_ERR_get_error();
    char buf[256];
    p_ERR_error_string_n(err, buf, sizeof(buf));
    fprintf(stderr, "[-] SSL Details: %s\n", buf);
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Usage: %s <url> [front_domain]\n", argv[0]);
        return 1;
    }

    if (!load_libs()) {
        fprintf(stderr, "[-] Error: Could not load system SSL libraries.\n");
        return 1;
    }

    char* url = argv[1];
    char* front_domain = (argc > 2) ? argv[2] : NULL;
    char host[256];
    char path[1024] = "/";
    int port = 80;

    memset(host, 0, sizeof(host));
    char* p = strstr(url, "://");
    if (p) {
        if (strncmp(url, "https", 5) == 0) port = 443;
        p += 3;
    } else {
        p = url;
    }
    
    char* s = strchr(p, '/');
    if (s) {
        size_t host_len = s - p;
        if (host_len >= sizeof(host)) host_len = sizeof(host) - 1;
        memcpy(host, p, host_len);
        host[host_len] = '\0';
        strncpy(path, s, sizeof(path) - 1);
    } else {
        strncpy(host, p, sizeof(host) - 1);
        host[sizeof(host)-1] = '\0';
    }

    char* colon = strchr(host, ':');
    if (colon) {
        *colon = '\0';
        port = atoi(colon + 1);
    }

    // Domain Fronting Logic: Resolve the front domain if provided
    char* dns_host = front_domain ? front_domain : host;
    struct hostent* server = gethostbyname(dns_host);
    if (!server) {
        fprintf(stderr, "[-] Error: Resolve failed for %s\n", dns_host);
        return 1;
    }

    int sockfd = socket(AF_INET, SOCK_STREAM, 0);
    struct sockaddr_in serv_addr;
    memset(&serv_addr, 0, sizeof(serv_addr));
    serv_addr.sin_family = AF_INET;
    memcpy(&serv_addr.sin_addr.s_addr, server->h_addr, server->h_length);
    serv_addr.sin_port = htons(port);

    if (connect(sockfd, (struct sockaddr*)&serv_addr, sizeof(serv_addr)) < 0) {
        perror("Connect failed");
        return 1;
    }

    void* ctx = NULL;
    void* ssl = NULL;

    if (port == 443) {
        void* method = p_TLS_client_method ? p_TLS_client_method() : (p_SSLv23_client_method ? p_SSLv23_client_method() : NULL);
        if (!method) {
            fprintf(stderr, "[-] Error: Failed to get SSL client method.\n");
            return 1;
        }
        ctx = p_SSL_CTX_new(method);
        
        if (p_SSL_CTX_set_verify) p_SSL_CTX_set_verify(ctx, 0, NULL); // SSL_VERIFY_NONE
        if (p_SSL_CTX_set_cipher_list) p_SSL_CTX_set_cipher_list(ctx, "DEFAULT:!SSLv3:!SSLv2");

        ssl = p_SSL_new(ctx);
        
        // SNI Support: Use front_domain for SNI if provided
        char* sni_host = front_domain ? front_domain : host;
        if (p_SSL_set_tlsext_host_name) {
            p_SSL_set_tlsext_host_name(ssl, sni_host);
        } else if (p_SSL_ctrl) {
            p_SSL_ctrl(ssl, 55, 0, (char *)sni_host);
        }

        p_SSL_set_fd(ssl, sockfd);
        if (p_SSL_connect(ssl) <= 0) {
            fprintf(stderr, "[-] Error: SSL connection failed.\n");
            print_ssl_error();
            return 1;
        }
    }

    char request[2048];
    snprintf(request, sizeof(request),
             "GET %s HTTP/1.1\r\n"
             "Host: %s\r\n"
             "User-Agent: Mozilla/5.0 (Linux; Android 11) SuperSploit/2.0\r\n"
             "Accept: */*\r\n"
             "Connection: close\r\n"
             "\r\n", path, host);

    if (port == 443) p_SSL_write(ssl, request, strlen(request));
    else write(sockfd, request, strlen(request));

    char response[8192];
    int n;
    int body_started = 0;
    while (1) {
        if (port == 443) n = p_SSL_read(ssl, response, sizeof(response) - 1);
        else n = read(sockfd, response, sizeof(response) - 1);
        
        if (n <= 0) break;
        response[n] = '\0';
        if (!body_started) {
            char* body = strstr(response, "\r\n\r\n");
            if (body) {
                printf("%s", body + 4);
                body_started = 1;
            }
        } else {
            printf("%s", response);
        }
    }

    if (ssl) p_SSL_free(ssl);
    if (ctx) p_SSL_CTX_free(ctx);
    close(sockfd);
    return 0;
}
