#!/bin/bash
echo "================================================="
echo "  SuperSploit OpenSSL Android NDK Builder"
echo "================================================="

NDK_PATH=$(find "$HOME/.buildozer/android/platform/" -maxdepth 1 -type d -name "android-ndk-r*" | sort | tail -n 1)

if [ -z "$NDK_PATH" ]; then
    echo "[-] Error: Android NDK not found in $HOME/.buildozer/android/platform/"
    echo "[*] Please generate a Buildozer APK once to let it auto-download the NDK."
    exit 1
fi

echo "[+] Found Android NDK at: $NDK_PATH"
export ANDROID_NDK_ROOT=$NDK_PATH
export PATH=$ANDROID_NDK_ROOT/toolchains/llvm/prebuilt/linux-x86_64/bin:$PATH

WORK_DIR="/tmp/ss_openssl_build"
mkdir -p $WORK_DIR
cd $WORK_DIR

if [ ! -d "openssl-3.0.12" ]; then
    echo "[*] Downloading OpenSSL 3.0.12 source..."
    wget -q https://www.openssl.org/source/openssl-3.0.12.tar.gz
    tar -xzf openssl-3.0.12.tar.gz
fi

cd openssl-3.0.12

ASSETS_DIR="$HOME/.SuperSploit/.data/.assets/openssl"
mkdir -p $ASSETS_DIR/include
cp -r include/openssl $ASSETS_DIR/include/

build_for_abi() {
    ABI=$1
    COMPILER_TARGET=$2
    echo "[*] Cross-compiling libcrypto.a for $ABI..."
    
    make clean > "build_clean_$ABI.log" 2>&1
    ./Configure $COMPILER_TARGET -D__ANDROID_API__=21 no-shared > "build_config_$ABI.log" 2>&1
    make build_libs -j$(nproc) > "build_make_$ABI.log" 2>&1
    
    if [ -f "libcrypto.a" ]; then
        mkdir -p "$ASSETS_DIR/$ABI"
        cp libcrypto.a "$ASSETS_DIR/$ABI/"
        echo "[+] Successfully built and cached $ABI"
    else
        echo "[-] Failed to build libcrypto.a for $ABI. Check $WORK_DIR/openssl-3.0.12/build_make_$ABI.log for details."
    fi
}

build_for_abi "arm64-v8a" "android-arm64"
build_for_abi "armeabi-v7a" "android-arm"
build_for_abi "x86_64" "android-x86_64"
build_for_abi "x86" "android-x86"

echo "[+] All OpenSSL architectures compiled and statically cached for SuperSploit!"