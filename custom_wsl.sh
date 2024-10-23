#!/bin/bash

sudo chown think:think /opt
sudo chmod 777 /opt

# Suppress login messages
sudo touch ~/.hushlogin
sudo touch /root/.hushlogin

# Prompt for Windows username
echo 'Windows Username:'
read wusername

# Create symlinks to Windows Downloads folder, force if they exist
ln -sf /mnt/c/Users/$wusername/Downloads ~/Downloads
sudo ln -sf /mnt/c/Users/$wusername/Downloads /root/Downloads

# Create an edit script
echo 'notepad.exe $1' | sudo tee /usr/sbin/edit > /dev/null
sudo chmod +x /usr/sbin/edit

# Redirect history and other files to /dev/null
ln -sf /dev/null ~/.lesshst
ln -sf /dev/null ~/.viminfo
ln -sf /dev/null ~/.wget-hsts
ln -sf /dev/null ~/.nc_history
ln -sf /dev/null ~/.python_history

# Append cron jobs safely, handling missing crontab case
( crontab -l 2>/dev/null; echo '10 * * * * /usr/sbin/backup'; echo '2 * * * * /usr/bin/rm -rf /wsl*'; echo '2 * * * * /usr/bin/rm -rf ~/*.tmp*' ) | crontab -

# Download and setup bash and zsh configs
curl -s https://raw.githubusercontent.com/josemlwdf/random_scripts/refs/heads/main/kali-zshrc -o ~/.zshrc
curl -s https://raw.githubusercontent.com/josemlwdf/random_scripts/refs/heads/main/bashrc -o ~/.bashrc
sudo cp ~/.bashrc /root/.bashrc
sudo cp ~/.zshrc /root/.zshrc

# Install Git
sudo apt install git -y

# Install PIP
sudo apt install python3-pip

# Create username-anarchy script
echo 'ruby /opt/username-anarchy/username-anarchy' | sudo tee /usr/sbin/username-anarchy > /dev/null
sudo chmod +x /usr/sbin/username-anarchy

# Download and setup various scripts, checking for curl success
SCRIPTS=("untar" "hist" "dcode" "urlencode" "smbserver" "PowerShellBase64ReverseShell.py"
         "shells" "pyftplibd" "ligolox" "IP" "create" "home" "ips" "http" "fix_zsh"
         "academy" "backup" "thm" "htb" "offsec" "ncx")

for script in "${SCRIPTS[@]}"; do
    sudo curl -s https://raw.githubusercontent.com/josemlwdf/random_scripts/refs/heads/main/$script -o /usr/sbin/$script
    if [[ $? -eq 0 ]]; then
        sudo chmod +x /usr/sbin/$script
    else
        echo "Failed to download $script. Skipping..."
    fi
done

# Add Kali repository
echo 'deb http://http.kali.org/kali kali-rolling main non-free contrib' | sudo tee -a /etc/apt/sources.list > /dev/null
echo 'deb-src http://http.kali.org/kali kali-rolling main non-free contrib' | sudo tee -a /etc/apt/sources.list > /dev/null

# Install other tools
curl -s https://raw.githubusercontent.com/josemlwdf/CTFEnum/main/install.sh | bash

# Install various packages
sudo apt install steghide stegsnow ffuf pipx file php exiftool impacket-scripts rlwrap john smbmap smbclient nikto exploitdb hydra wpscan poppler-utils sqlmap hash-identifier enum4linux hashcat dos2unix whatweb docker.io knockd evil-winrm jq ltrace sntp tftp-hpa -y
sudo pipx ensurepath
sudo pip install requests git-dumper

# Download and configure additional files
sudo curl -s https://raw.githubusercontent.com/josemlwdf/random_scripts/refs/heads/main/ferox-config.toml -o /etc/feroxbuster/ferox-config.toml

# Update locate database
sudo updatedb

# Install ngrok and configure it
curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc > /dev/null
echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list > /dev/null
sudo apt install ngrok -y

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

sudo chsh -s /bin/zsh think
sudo ln -s /usr/bin/google-chrome /usr/sbin/chrome

rm -f custom_wsl.sh

sudo pipx install git+https://github.com/Pennyw0rth/NetExec
