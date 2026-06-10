# check if install exist
printf "[*] check for prior install at $HOME/.SuperSploit \n"
if [ -d "$HOME/.SuperSploit" ]; then
  printf "[*] removing old install at $HOME/.SuperSploit \n"
  sudo rm -r $HOME/.SuperSploit
fi

# copy latest local version to install path
printf  "[*] Copying files to install path \n"
sudo cp -r  $HOME/PycharmProjects/SuperSploit-Framework $HOME/.SuperSploit

# change ownership
printf "[*] Changing ownership to $USER \n"
sudo chown -R $USER ~/.SuperSploit

# start application
supersploit
