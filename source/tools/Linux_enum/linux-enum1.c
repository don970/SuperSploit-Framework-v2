#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#ifdef __ANDROID__
#include <sys/system_properties.h>
#else
#ifndef PROP_VALUE_MAX
#define PROP_VALUE_MAX 92
#endif
#endif
#include <sys/utsname.h>
#include <fcntl.h>
#include <errno.h>
#include <dirent.h>
#include <pwd.h>
#include <grp.h>
#ifdef __ANDROID__
#include <sys/capability.h>
#endif
#include <sys/prctl.h>

#define RED     "\x1b[31m"
#define GREEN   "\x1b[32m"
#define YELLOW  "\x1b[33m"
#define BLUE    "\x1b[34m"
#define MAGENTA "\x1b[35m"
#define CYAN    "\x1b[36m"
#define RESET   "\x1b[0m"
#define BOLD    "\x1b[1m"

void print_section(const char* title) {
    printf(BLUE BOLD "\n[+] %s\n" RESET, title);
    printf("---------------------------------------------------------------\n");
}

void get_prop(const char* prop, char* value) {
#ifdef __ANDROID__
    if (__system_property_get(prop, value) <= 0) {
        strcpy(value, "N/A");
    }
#else
    char cmd[256];
    snprintf(cmd, sizeof(cmd), "getprop %s 2>/dev/null", prop);
    FILE* fp = popen(cmd, "r");
    if (fp) {
        if (fgets(value, PROP_VALUE_MAX, fp) != NULL) {
            char* nl = strchr(value, '\n');
            if (nl) *nl = '\0';
            if (strlen(value) == 0) strcpy(value, "N/A");
        } else {
            strcpy(value, "N/A");
        }
        pclose(fp);
    } else {
        strcpy(value, "N/A");
    }
#endif
}

void read_file_content(const char* path, const char* label) {
    FILE* fp = fopen(path, "r");
    if (fp) {
        printf("  - %s (%s):\n", label, path);
        char buffer[1024];
        while (fgets(buffer, sizeof(buffer), fp)) {
            printf("    %s", buffer);
        }
        fclose(fp);
    } else {
        printf("  - %s: " YELLOW "Could not read %s\n" RESET, label, path);
    }
}

void check_system_extreme() {
    print_section("EXTREME SYSTEM ARCHITECTURE AUDIT");
    struct utsname name;
    uname(&name);
    printf("  - Kernel: %s %s %s %s\n", name.sysname, name.release, name.version, name.machine);

    char val[PROP_VALUE_MAX];
    const char* props[] = {
        "ro.product.brand", "ro.product.model", "ro.product.cpu.abi",
        "ro.build.version.release", "ro.build.version.sdk", "ro.build.version.security_patch",
        "ro.build.fingerprint", "ro.build.type", "ro.debuggable", "ro.secure",
        "ro.adb.secure", "ro.treble.enabled", "ro.vndk.version", "ro.apex.updatable",
        "ro.boot.flash.locked", "ro.boot.verifiedbootstate", "ro.boot.vbmeta.device_state",
        "persist.sys.usb.config", "ro.hardware", "ro.board.platform"
    };

    for (int i = 0; i < sizeof(props) / sizeof(char*); i++) {
        get_prop(props[i], val);
        printf("  - %-30s : %s\n", props[i], val);
    }
}

void audit_installed_apps() {
    print_section("THIRD-PARTY APP AUDIT (LPE & ATTACK SURFACE)");
    printf("  [*] Querying installed packages for vulnerabilities...\n");
    
    FILE* fp = popen("pm list packages -3 -f", "r");
    if (fp) {
        char line[512];
        int count = 0;
        while (fgets(line, sizeof(line), fp) && count < 20) { // Limit to top 20 for speed
            char* pkg = strstr(line, "=");
            if (pkg) {
                pkg++;
                char* nl = strchr(pkg, '\n');
                if (nl) *nl = '\0';
                
                printf("  - Package: %-40s ", pkg);
                
                // Check for debuggable flag
                char cmd[512];
                snprintf(cmd, sizeof(cmd), "dumpsys package %s | grep -E 'flags|versionName' | head -n 2", pkg);
                FILE* dfp = popen(cmd, "r");
                if (dfp) {
                    char dline[512];
                    while (fgets(dline, sizeof(dline), dfp)) {
                        if (strstr(dline, "DEBUGGABLE")) printf("[%sDEBUGGABLE%s] ", RED, RESET);
                        if (strstr(dline, "versionName=")) {
                            char* v = strchr(dline, '=');
                            if (v) {
                                char* v_nl = strchr(v, '\n');
                                if (v_nl) *v_nl = '\0';
                                printf("(Ver: %s) ", v+1);
                            }
                        }
                    }
                    pclose(dfp);
                }
                printf("\n");
                count++;
            }
        }
        pclose(fp);
    }
}

void check_service_fingerprints() {
    print_section("SERVICE & PROCESS FINGERPRINTING");
    const char* targets[] = {"adbd", "surfaceflinger", "vold", "zygote", "netd", "hwservicemanager", "installd"};
    
    for (int i = 0; i < sizeof(targets) / sizeof(char*); i++) {
        char cmd[512];
        snprintf(cmd, sizeof(cmd), "ps -A | grep %s", targets[i]);
        FILE* fp = popen(cmd, "r");
        if (fp) {
            char line[512];
            if (fgets(line, sizeof(line), fp)) {
                printf("  - [ACTIVE] %-20s : %s", targets[i], line);
            }
            pclose(fp);
        }
    }
}

void check_micro_cracks() {
    print_section("DEEP AUDIT FOR MICRO-CRACKS (INFO LEAKS & LOGS)");
    
    // Check for sensitive strings in dmesg (requires permissions)
    printf("  [*] Checking dmesg for sensitive leaks (overflows, pointers)...\n");
    FILE* fp = popen("dmesg | grep -Ei \"address|leak|overflow|fail|error|null pointer\" | tail -n 10", "r");
    if (fp) {
        char line[512];
        while (fgets(line, sizeof(line), fp)) {
            printf("    %s%s%s", RED, line, RESET);
        }
        pclose(fp);
    }

    // Check for world-readable sensitive proc files
    const char* leaks[] = {"/proc/kallsyms", "/proc/slabinfo", "/proc/modules", "/proc/iomem"};
    for (int i = 0; i < sizeof(leaks) / sizeof(char*); i++) {
        if (access(leaks[i], R_OK) == 0) printf("  - [!] %sINFO LEAK%s: %s is readable!\n", RED, RESET, leaks[i]);
    }

    // Check for writeable system properties (rare but critical)
    if (access("/data/property", W_OK) == 0) printf("  - [!] %sCRITICAL%s: /data/property is WRITABLE!\n", RED, RESET);
}

int has_binary(const char* cmd) {
    char check_cmd[128];
    snprintf(check_cmd, sizeof(check_cmd), "which %s > /dev/null 2>&1", cmd);
    return (system(check_cmd) == 0);
}

void online_extreme_correlation() {
    print_section("INTELLIGENT MULTI-SOURCE ONLINE CORRELATION");
    
    struct utsname name;
    uname(&name);
    char base_ver[64];
    strncpy(base_ver, name.release, sizeof(base_ver) - 1);
    char* dash = strchr(base_ver, '-');
    if (dash) *dash = '\0';

    char board[PROP_VALUE_MAX];
    get_prop("ro.board.platform", board);

    printf("  [*] Target Fingerprint: Kernel %s | Platform %s\n", base_ver, board);
    printf("  [*] " MAGENTA "SuperSploit Fingerprint" RESET ": os=android kernel=%s arch=%s board=%s\n", base_ver, name.machine, board);

    const char* fetcher = NULL;
    if (has_binary("curl")) fetcher = "curl -s";
    else if (has_binary("wget")) fetcher = "wget -q -O -";
    else if (access("./minish", X_OK) == 0) fetcher = "./minish";
    else if (access("/data/local/tmp/minish", X_OK) == 0) fetcher = "/data/local/tmp/minish";

    if (!fetcher) {
        printf("  - [!] " YELLOW "Warning" RESET ": No fetcher found (curl, wget, or minish).\n");
        printf("    " BLUE "Manual Step" RESET ": Copy the Fingerprint below and run it in the SuperSploit framework:\n");
        printf("    " MAGENTA "suggest os=android kernel=%s arch=%s board=%s" RESET "\n", base_ver, name.machine, board);
        return;
    }

    printf("  [*] Using fetcher: %s\n", fetcher);

    const char* apis[] = {
        "https://cve.circl.lu/api/search/kernel%%20",
        "https://sploitus.com/search?query=kernel%%20",
        "https://vulners.com/api/v3/search/lucene/?query=kernel%%20"
    };
    const char* api_names[] = {"CIRCL (CVE)", "Sploitus (Exploits)", "Vulners (Aggregate)"};

    for (int i = 0; i < 3; i++) {
        printf("\n  [*] Querying %s for Kernel %s...\n", api_names[i], base_ver);
        char cmd[1024];
        snprintf(cmd, sizeof(cmd), "%s \"%s%s\" | grep -oE \"CVE-[0-9]{4}-[0-9]+\" | sort -u | head -n 10", fetcher, apis[i], base_ver);
        
        FILE* fp = popen(cmd, "r");
        if (fp) {
            char buffer[1024];
            int found = 0;
            while (fgets(buffer, sizeof(buffer), fp)) {
                printf("    -> %s", buffer);
                found = 1;
            }
            pclose(fp);
            if (!found) printf("    " YELLOW "No immediate hits for version %s.\n" RESET, base_ver);
        }
    }

    // Fuzzy SoC Search
    if (strcmp(board, "N/A") != 0) {
        printf("\n  [*] Performing Fuzzy SoC Audit for '%s' vulnerabilities...\n", board);
        char cmd[1024];
        snprintf(cmd, sizeof(cmd), "%s \"https://sploitus.com/search?query=%s%%20LPE\" | grep -oE \"CVE-[0-9]{4}-[0-9]+\" | sort -u | head -n 5", fetcher, board);
        FILE* fp = popen(cmd, "r");
        if (fp) {
            char buffer[1024];
            while (fgets(buffer, sizeof(buffer), fp)) {
                printf("    -> %s (Platform Specific)\n", buffer);
            }
            pclose(fp);
        }
    }
}

// ... (Previous probe_device_nodes, check_filesystem_weakness, etc. remain integrated) ...
void probe_device_nodes() {
    print_section("DEVICE NODE PROBE (LPE SURFACE)");
    const char* nodes[] = {
        "/dev/binder", "/dev/hwbinder", "/dev/vndbinder", "/dev/ashmem", "/dev/ion", "/dev/sw_sync", "/dev/mali0",
        "/dev/kgsl-3d0", "/dev/nvhost-ctrl", "/dev/graphics/fb0", "/dev/dri/renderD128", "/dev/qcedev", "/dev/qseecom",
        "/dev/vpu", "/dev/mali", "/dev/sprd_image", "/dev/sprd_jpg",
        "/dev/sprd_vsp", "/dev/sprd_vpp", "/dev/sprd_vbe", "/dev/trusty-ipc-dev0"
    };
    for (int i = 0; i < sizeof(nodes) / sizeof(char*); i++) {
        struct stat st;
        if (stat(nodes[i], &st) == 0) {
            if (access(nodes[i], R_OK | W_OK) == 0) printf("  - [%sRW%s] %s\n", RED, RESET, nodes[i]);
            else if (access(nodes[i], R_OK) == 0) printf("  - [%sRO%s] %s\n", YELLOW, RESET, nodes[i]);
        }
    }
}

void check_filesystem_weakness() {
    print_section("FILESYSTEM PERMISSIONS");
    const char* paths[] = {
        "/data/local/tmp", "/dev/socket", "/proc/sys/kernel", "/sys/kernel/debug",
        "/mnt/vendor", "/vendor/bin", "/vendor/lib", "/system/xbin"
    };
    for (int i = 0; i < sizeof(paths) / sizeof(char*); i++) {
        if (access(paths[i], W_OK) == 0) printf("  - [%sWRITABLE%s] %s\n", RED, RESET, paths[i]);
    }
}

int main() {
    printf(CYAN BOLD "===============================================================\n");
    printf("   INTELLIGENT ANDROID SECURITY AUDIT SUITE - EXTREME EDITION\n");
    printf("===============================================================\n" RESET);

    check_system_extreme();
    audit_installed_apps();
    check_service_fingerprints();
    check_micro_cracks();
    probe_device_nodes();
    check_filesystem_weakness();
    online_extreme_correlation();

    printf(CYAN BOLD "\n[+] Audit Complete. All micro-cracks reported.\n" RESET);
    return 0;
}
