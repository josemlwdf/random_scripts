#!/bin/bash

# Suppress login messages
sudo touch ~/.hushlogin
sudo touch /root/.hushlogin

mkdir -p ~/CTF/{HackMyVM,HTB,THM,Vulnyx,OSCP/Play,OTW,DockerLabs}

# Prompt for Windows username
echo 'Windows Username:'
read wusername

# Create symlinks to Windows Downloads folder
ln -s /mnt/c/Users/$wusername/Downloads ~/Downloads
sudo ln -s /mnt/c/Users/$wusername/Downloads /root/Downloads

# Create an edit script
echo 'notepad.exe $1' | sudo tee /usr/sbin/edit
sudo chmod +x /usr/sbin/edit

# Redirect history and other files to /dev/null
ln -s /dev/null ~/.lesshst
ln -s /dev/null ~/.viminfo
ln -s /dev/null ~/.wget-hsts
ln -s /dev/null ~/.nc_history
ln -s /dev/null ~/.python_history
ln -s /dev/null ~/.lesshst

# Append cron jobs safely
{ crontab -l; echo '10 * * * * /usr/sbin/backup'; echo '2 * * * * /usr/bin/rm -rf /wsl*'; echo '2 * * * * /usr/bin/rm -rf ~/*.tmp*'; } | crontab -

# Download and setup bash and zsh configs
curl -s https://raw.githubusercontent.com/josemlwdf/random_scripts/refs/heads/main/kali-zshrc -o ~/.zshrc
curl -s https://raw.githubusercontent.com/josemlwdf/random_scripts/refs/heads/main/bashrc -o ~/.bashrc
sudo cp ~/.bashrc /root/.bashrc
sudo cp ~/.zshrc /root/.zshrc

# Install Git
sudo apt install git -y

# Create username-anarchy script
echo 'ruby /opt/username-anarchy/username-anarchy' | sudo tee /usr/sbin/username-anarchy
sudo chmod +x /usr/sbin/username-anarchy

# Download and setup various scripts
SCRIPTS=("untar" "hist" "dcode" "urlencode" "smbserver" "PowerShellBase64ReverseShell.py" 
         "shells" "pyftplibd" "ligolox" "IP" "create" "home" "ips" "http" "fix_zsh" 
         "academy" "backup" "thm" "htb" "offsec" "ncx")

for script in "${SCRIPTS[@]}"; do
    sudo curl -s https://raw.githubusercontent.com/josemlwdf/random_scripts/refs/heads/main/$script -o /usr/sbin/$script
    sudo chmod +x /usr/sbin/$script
done

# Add Kali repository
echo 'deb http://http.kali.org/kali kali-rolling main non-free contrib' | sudo tee -a /etc/apt/sources.list
echo 'deb-src http://http.kali.org/kali kali-rolling main non-free contrib' | sudo tee -a /etc/apt/sources.list

# Install other tools
curl -s https://raw.githubusercontent.com/josemlwdf/CTFEnum/main/install.sh | bash

# Install various packages
sudo apt install steghide stegsnow ffuf pipx file php exiftool impacket-scripts rlwrap john smbmap smbclient nikto searchsploit hydra wpscan poppler-utils sqlmap hash-identifier enum4linux hashcat dos2unix whatweb docker.io knockd evil-winrm jq ltrace sntp tftp-hpa -y
sudo pipx ensurepath
sudo pipx install git+https://github.com/Pennyw0rth/NetExec
sudo pip install requests git-dumper

# Download and configure additional files
sudo curl https://raw.githubusercontent.com/josemlwdf/random_scripts/refs/heads/main/ferox-config.toml -o /etc/feroxbuster/ferox-config.toml

# Update locate database
sudo updatedb

# Install ngrok and configure it
curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list
sudo apt update && sudo apt install ngrok -y

# Prompt for Ngrok token
echo https://dashboard.ngrok.com/get-started/your-authtoken
echo "Ngrok Token:"
read ntoken
sudo ngrok config add-authtoken $ntoken

# Generate SSH keys
ssh-keygen -t rsa -b 4096

# Instructions for the user
echo '[!] Download the /opt folder backup from Mega'
echo 'Press Enter when the /opt folder is in place.'
read
sudo ln -s /opt/kerbrute /usr/sbin/kerbrute

# Instructions to install additional software
echo '[!] Install Caido and Google Chrome'
echo 'Move caido-cli to /usr/sbin'
echo 'sudo apt -y install ./google-chrome-stable_current_amd64.deb'
sudo ln -s /usr/bin/google-chrome /usr/sbin/chrome
