#!/bin/bash
set -e

# Change to the directory where the script is located
cd "$(dirname "$0")"

echo "Making supersploit executable..."

# Using a heredoc is much cleaner and avoids quote escaping issues that were present in the previous string variable.
# It also allows for clean double quotes inside the C code.
cat << 'EOF' > supersploit.c
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int main() {
    const char *home = getenv("HOME");
    if (home == NULL) {
        fprintf(stderr, "Error: HOME environment variable not set.\n");
        return 1;
    }

    char path[1024];
    snprintf(path, sizeof(path), "%s/.SuperSploit/start.sh", home);

    // Using execl replaces the current process with bash, preventing shell injection vulnerabilities
    // compared to using system().
    execl("/bin/bash", "bash", path, (char *)NULL);

    // If execl returns, an error occurred
    perror("execl failed");
    return 1;
}
EOF

echo "Compiling executable..."
if ! command -v gcc &> /dev/null; then
    echo "Error: gcc is not installed. Please install gcc to compile the executable."
    exit 1
fi
gcc supersploit.c -o supersploit

# Using /usr/local/bin is best practice for user-installed binaries instead of /bin
echo "Moving supersploit to /usr/local/bin folder..."
sudo mv supersploit /usr/local/bin/supersploit
sudo chmod +x /usr/local/bin/supersploit

echo "Making desktop file and app drawer icon..."
cat << 'EOF' > supersploit.desktop
[Desktop Entry]
Name=SuperSploit
Comment=Exploit Management framework
Exec=/usr/local/bin/supersploit
Icon=/usr/share/icons/hicolor/16x16/apps/logo1.png
Terminal=true
Type=Application
Categories=System;Utility;
EOF

sudo mv supersploit.desktop /usr/share/applications/

echo "Moving icon..."
# Using hicolor which is the standard icon theme fallback directory
ICON_DIR="/usr/share/icons/hicolor/16x16/apps"
sudo mkdir -p "$ICON_DIR"
if [ -f "$HOME/.SuperSploit/.data/.assets/logo1.png" ]; then
    sudo cp "$HOME/.SuperSploit/.data/.assets/logo1.png" "$ICON_DIR/logo1.png"
else
    echo "Warning: Icon not found at $HOME/.SuperSploit/.data/.assets/logo1.png"
fi

echo "Cleaning up temporary files..."
rm -f supersploit.c

echo "Setup complete!"
cd "$HOME/.SuperSploit" || exit
