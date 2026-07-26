# check if install exist
printf "[*] check for prior install at $HOME/.SuperSploit \n"
if [ -d "$HOME/.SuperSploit" ]; then
  printf "[*] removing old install at $HOME/.SuperSploit \n"
  sudo rm -r $HOME/.SuperSploit
fi

# install system dependencies
printf "[*] Installing system dependencies \n"
sudo apt-get update
sudo apt-get install -y libcurl4-openssl-dev python3 python3-pip build-essential libssl-dev libffi-dev python3-dev

printf "[*] Installing Advanced Evasion & Hardware Dependencies \n"
sudo apt-get install -y hostapd dnsmasq aircrack-ng apktool zipalign apksigner default-jdk gcc-aarch64-linux-gnu

# copy latest local version to install path
printf  "[*] Copying files to install path \n"
sudo cp -r  $HOME/PycharmProjects/SuperSploit-Framework $HOME/.SuperSploit

# change ownership
printf "[*] Changing ownership to $USER \n"
sudo chown -R $USER ~/.SuperSploit

printf "[*] Installing Python Libraries \n"
pip3 install -r $HOME/.SuperSploit/requirements.txt --break-system-packages || pip3 install -r $HOME/.SuperSploit/requirements.txt

printf "[*] Setting execution permissions \n"
chmod +x $HOME/.SuperSploit/SuperSploit.py

printf "[*] Building OpenSSL for Android NDK \n"
chmod +x $HOME/.SuperSploit/setup/build_ndk_openssl.sh
bash $HOME/.SuperSploit/setup/build_ndk_openssl.sh

# start application
supersploit
