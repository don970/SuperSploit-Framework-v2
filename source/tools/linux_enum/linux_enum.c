/**
 * SuperSploit Framework - Exhaustive Linux Security Audit Suite (C)
 * 
 * Version: 1.0 (Linux Pro Edition)
 * Target: Linux (x86_64, x86, aarch64, armv7)
 * 
 * This tool performs a deep-dive security audit of a Linux target, 
 * focusing on LPE micro-cracks, kernel hardening bypasses, container 
 * breakouts, and high-value CVE correlation.
 */

#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/utsname.h>
#include <fcntl.h>
#include <errno.h>
#include <dirent.h>
#include <pwd.h>

/* --- ANSI Colors --- */
#define RED     "\x1b[31m"
#define GREEN   "\x1b[32m"
#define YELLOW  "\x1b[33m"
#define BLUE    "\x1b[34m"
#define MAGENTA "\x1b[35m"
#define CYAN    "\x1b[36m"
#define RESET   "\x1b[0m"
#define BOLD    "\x1b[1m"

/* --- Framework Macros --- */
#define LOG_INFO(msg, ...) printf(BLUE "[+] " RESET msg "\n", ##__VA_ARGS__)
#define LOG_WARN(msg, ...) printf(YELLOW "[!] " RESET msg "\n", ##__VA_ARGS__)
#define LOG_CRIT(msg, ...) printf(RED "[!!!] CRITICAL: " RESET msg "\n", ##__VA_ARGS__)
#define LOG_DATA(key, val) printf("  - %-30s : %s\n", key, val)

/* --- Global State --- */
char g_arch[32] = {0};
char g_kernel_ver[64] = {0};
char g_os_name[128] = "Unknown Linux";

/* --- Helper Functions --- */
void print_header() {
    printf(CYAN BOLD "===============================================================\n");
    printf("   EXHAUSTIVE LINUX SECURITY AUDIT SUITE - VERSION 1.0\n");
    printf("   Black Enum | Security Audit | Mass CVE Correlation\n");
    printf("===============================================================\n" RESET);
}

void print_section(const char* title) {
    printf(BLUE BOLD "\n[+] %s\n" RESET, title);
    printf("---------------------------------------------------------------\n");
}

int check_file_exists(const char* path) {
    return (access(path, F_OK) == 0);
}

int check_file_readable(const char* path) {
    return (access(path, R_OK) == 0);
}

int check_file_writable(const char* path) {
    return (access(path, W_OK) == 0);
}

/* --- Audit Modules --- */

void audit_system_base() {
    print_section("SYSTEM ARCHITECTURE & BLACK ENUM");
    struct utsname name;
    uname(&name);
    strcpy(g_arch, name.machine);
    strcpy(g_kernel_ver, name.release);
    
    // Parse /etc/os-release for distro info
    FILE *fp = fopen("/etc/os-release", "r");
    if (fp) {
        char line[256];
        while (fgets(line, sizeof(line), fp)) {
            if (strncmp(line, "PRETTY_NAME=", 12) == 0) {
                char *val = line + 12;
                if (val[0] == '"') val++;
                char *nl = strchr(val, '"');
                if (!nl) nl = strchr(val, '\n');
                if (nl) *nl = '\0';
                strncpy(g_os_name, val, sizeof(g_os_name)-1);
                break;
            }
        }
        fclose(fp);
    }

    LOG_DATA("Operating System", g_os_name);
    LOG_DATA("Kernel Release", g_kernel_ver);
    LOG_DATA("Architecture", g_arch);
    LOG_DATA("Hostname", name.nodename);

    // Check Container Environment
    if (check_file_exists("/.dockerenv")) {
        LOG_WARN("Execution Environment: DOCKER CONTAINER DETECTED");
    } else {
        FILE *cgroup = fopen("/proc/1/cgroup", "r");
        if (cgroup) {
            char buffer[512];
            size_t bytes = fread(buffer, 1, sizeof(buffer)-1, cgroup);
            buffer[bytes] = '\0';
            if (strstr(buffer, "docker") || strstr(buffer, "lxc") || strstr(buffer, "kubepods")) {
                LOG_WARN("Execution Environment: LINUX CONTAINER DETECTED (cgroup match)");
            } else {
                LOG_DATA("Execution Environment", "Bare Metal / VM");
            }
            fclose(cgroup);
        }
    }
}

void audit_mac_systems() {
    print_section("MANDATORY ACCESS CONTROL (MAC) AUDIT");
    
    // SELinux
    if (check_file_exists("/sys/fs/selinux/enforce")) {
        FILE* fp = fopen("/sys/fs/selinux/enforce", "r");
        if (fp) {
            int enforce = fgetc(fp) - '0';
            fclose(fp);
            LOG_DATA("SELinux Status", enforce ? "Enforcing" : "Permissive");
        }
    } else {
        LOG_DATA("SELinux Status", "Disabled / Not Installed");
    }

    // AppArmor
    if (check_file_exists("/sys/kernel/security/apparmor/profiles")) {
        LOG_DATA("AppArmor Status", "Enabled (Profiles Loaded)");
    } else {
        LOG_DATA("AppArmor Status", "Disabled / Not Installed");
    }
}

void audit_kernel_hardening() {
    print_section("KERNEL HARDENING & EXPLOIT MITIGATIONS");

    const char* mit[] = {
        "/proc/sys/kernel/kptr_restrict",
        "/proc/sys/kernel/dmesg_restrict",
        "/proc/sys/kernel/yama/ptrace_scope",
        "/proc/sys/kernel/unprivileged_bpf_disabled",
        "/proc/sys/net/core/bpf_jit_enable"
    };

    for (int i = 0; i < sizeof(mit) / sizeof(char*); i++) {
        if (check_file_readable(mit[i])) {
            FILE* fp = fopen(mit[i], "r");
            if (fp) {
                char val[32] = {0};
                fgets(val, sizeof(val)-1, fp);
                fclose(fp);
                char* nl = strchr(val, '\n');
                if (nl) *nl = '\0';
                LOG_DATA(mit[i], val);
            }
        } else {
            printf("  - %-30s : " YELLOW "Protected\n" RESET, mit[i]);
        }
    }

    // KASLR Leak Check
    if (check_file_readable("/proc/kallsyms")) {
        FILE *fp = popen("head -n 1 /proc/kallsyms | grep -v '0000000000000000'", "r");
        if (fp) {
            char buffer[64];
            if (fgets(buffer, sizeof(buffer), fp) != NULL) {
                LOG_CRIT("KASLR Bypass Found: /proc/kallsyms pointers are EXPOSED!");
            }
            pclose(fp);
        }
    }
}

void audit_filesystems() {
    print_section("SENSITIVE FILESYSTEM & PERMISSIONS AUDIT");

    // Check critical files for world-writability
    const char* crit_files[] = {
        "/etc/passwd", "/etc/shadow", "/etc/sudoers", 
        "/etc/crontab", "/etc/ld.so.conf"
    };

    for (int i = 0; i < sizeof(crit_files) / sizeof(char*); i++) {
        if (check_file_exists(crit_files[i])) {
            if (check_file_writable(crit_files[i])) {
                printf("  - [!] " RED "WORLD-WRITABLE" RESET ": %s\n", crit_files[i]);
            } else if (strcmp(crit_files[i], "/etc/shadow") == 0 && check_file_readable(crit_files[i])) {
                printf("  - [!] " RED "WORLD-READABLE" RESET ": /etc/shadow (Hash Leak)\n");
            } else {
                printf("  - " GREEN "SECURE" RESET " : %s\n", crit_files[i]);
            }
        }
    }

    printf("\n[*] Scanning for high-value SUID binaries...\n");
    const char* suid_targets[] = {
        "/usr/bin/pkexec", "/usr/bin/sudo", "/usr/bin/doas", 
        "/bin/su", "/usr/bin/passwd", "/usr/sbin/exim4", "/usr/bin/find"
    };

    for (int i = 0; i < sizeof(suid_targets) / sizeof(char*); i++) {
        struct stat st;
        if (stat(suid_targets[i], &st) == 0) {
            if (st.st_mode & S_ISUID) {
                printf("  - " YELLOW "SUID FOUND" RESET " : %s\n", suid_targets[i]);
            }
        }
    }
}

void audit_vulnerabilities() {
    print_section("MASS CVE CORRELATION ENGINE");
    
    LOG_INFO("Matching kernel %s and binaries against SuperSploit DB...", g_kernel_ver);

    int cve_found = 0;

    // Kernel range parsers
    float k_ver = 0.0;
    sscanf(g_kernel_ver, "%f", &k_ver);

    // CVE-2024-1086: Nftables UAF
    if (k_ver >= 5.14 && k_ver <= 6.6) {
        printf("  - [" RED "CRITICAL" RESET "] CVE-2024-1086 : Nftables Use-After-Free (Kernel %s)\n", g_kernel_ver);
        cve_found++;
    }

    // CVE-2022-0847: Dirty Pipe
    if (k_ver >= 5.8 && k_ver < 5.17) {
        // Exclude specific patches if possible, but flag for range
        printf("  - [" RED "CRITICAL" RESET "] CVE-2022-0847 : Dirty Pipe (Kernel %s)\n", g_kernel_ver);
        cve_found++;
    }

    // CVE-2016-5195: Dirty COW
    if (k_ver < 4.8) {
        printf("  - [" RED "CRITICAL" RESET "] CVE-2016-5195 : Dirty COW (Kernel %s)\n", g_kernel_ver);
        cve_found++;
    }

    // CVE-2021-4034: PwnKit
    struct stat st;
    if (stat("/usr/bin/pkexec", &st) == 0 && (st.st_mode & S_ISUID)) {
        printf("  - [" RED "CRITICAL" RESET "] CVE-2021-4034 : PwnKit (pkexec is SUID)\n");
        cve_found++;
    }

    // CVE-2023-4911: Looney Tunables
    if (check_file_exists("/lib/x86_64-linux-gnu/libc.so.6") || check_file_exists("/lib64/libc.so.6")) {
        printf("  - [" YELLOW "HIGH" RESET "]     CVE-2023-4911 : Looney Tunables (glibc ld.so check recommended)\n");
        cve_found++;
    }

    // CVE-2021-3156: Sudo Baron Samedit
    if (stat("/usr/bin/sudo", &st) == 0 && (st.st_mode & S_ISUID)) {
        printf("  - [" YELLOW "HIGH" RESET "]     CVE-2021-3156 : Sudo Baron Samedit (sudo is SUID, verify version < 1.9.5p2)\n");
        cve_found++;
    }

    if (!cve_found) {
        printf("  - [" GREEN "CLEAN" RESET "] No high-confidence 1-day CVEs correlated directly.\n");
    }
}

int main(int argc, char** argv) {
    print_header();

    audit_system_base();
    audit_mac_systems();
    audit_kernel_hardening();
    audit_filesystems();
    audit_vulnerabilities();

    printf(CYAN BOLD "\n[+] Exhaustive Audit Complete. SuperSploit target mapping ready.\n" RESET);
    return 0;
}
/*
#!#!#!
name: "Exhaustive Linux Security Audit Suite"
description: "Deep-dive security audit of a Linux target, focusing on LPE micro-cracks, kernel hardening bypasses, container breakouts, and high-value CVE correlation."
category: "recon"
author: "Donald Ford"
os: "linux"
#!#!#!
*/