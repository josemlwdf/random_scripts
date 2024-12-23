#!/bin/bash
sudo chown think:think /opt 2>/dev/null
sudo chmod 777 /opt 2>/dev/null
# Suppress login messages
sudo touch ~/.hushlogin
sudo touch /root/.hushlogin
mkdir ~/CTF
PLATFORMS=("HackMyVM" "HTB" "DockerLabs" "OSCP" "OTW" "THM"
         "VulnHub" "Vulnyx")
for platform in "${PLATFORMS[@]}"; do
    mkdir ~/CTF/$platform
done 
mkdir ~/CTF/OSCP/Play
sudo curl -s https://raw.githubusercontent.com/josemlwdf/random_scripts/refs/heads/main/wsl.conf -o /etc/wsl.conf
wusername='josel'
# Create symlinks to Windows Downloads folder, force if they exist
ln -sf /mnt/c/Users/$wusername/Downloads ~/Downloads  2>/dev/null
sudo ln -sf /mnt/c/Users/$wusername/Downloads /root/Downloads  2>/dev/null
sudo ln -sf /usr/bin/google-chrome /usr/sbin/chrome 2>/dev/null
# Create an edit script
echo 'notepad.exe $1' | sudo tee /usr/sbin/edit > /dev/null
sudo chmod +x /usr/sbin/edit
# Redirect history and other files to /dev/null
ln -sf /dev/null ~/.lesshst
ln -sf /dev/null ~/.viminfo
ln -sf /dev/null ~/.wget-hsts
ln -sf /dev/null ~/.python_history
# Append cron jobs safely, handling missing crontab case
(echo '10 * * * * /usr/sbin/backup'; echo '2 * * * * /usr/bin/rm -rf /wsl*'; echo '2 * * * * /usr/bin/rm -rf ~/*.tmp*'; echo '2 * * * * /usr/bin/rm -rf /tmp/*' ) | sudo crontab -
# Download and setup bash and zsh configs
curl -s https://raw.githubusercontent.com/josemlwdf/random_scripts/refs/heads/main/kali-zshrc -o ~/.zshrc
curl -s https://raw.githubusercontent.com/josemlwdf/random_scripts/refs/heads/main/bashrc -o ~/.bashrc
sudo cp ~/.bashrc /root/.bashrc
sudo cp ~/.zshrc /root/.zshrc
sudo ln -s /usr/bin/python3 /usr/sbin/python
# Install Git
sudo apt install git -y
# Install PIP
sudo apt install python3-pip -y
# Create username-anarchy script
echo 'ruby /opt/username-anarchy/username-anarchy $@' | sudo tee /usr/sbin/username-anarchy > /dev/null
sudo chmod +x /usr/sbin/username-anarchy
sudo curl -s https://raw.githubusercontent.com/josemlwdf/Decodify/refs/heads/master/dcode -o /usr/sbin/dcode
# Download and setup various scripts, checking for curl success
SCRIPTS=("untar" "hist" "urlencode" "smbserver"
         "shells" "pyftplibd" "ligolox" "IP" "create" "home" "ips" "http" "fix_zsh"
         "academy" "backup" "thm" "htb" "offsec" "ncx" "upgrade")
for script in "${SCRIPTS[@]}"; do
    sudo curl -s https://raw.githubusercontent.com/josemlwdf/random_scripts/refs/heads/main/$script -o /usr/sbin/$script
done
sudo curl -s https://raw.githubusercontent.com/josemlwdf/random_scripts/refs/heads/main/PowerShellBase64ReverseShell.py -o /usr/sbin/shellps1
sudo chmod +x /usr/sbin/*
# Add Kali repository
echo 'deb http://http.kali.org/kali kali-rolling main non-free contrib' | sudo tee -a /etc/apt/sources.list > /dev/null
echo 'deb-src http://http.kali.org/kali kali-rolling main non-free contrib' | sudo tee -a /etc/apt/sources.list > /dev/null
# Install other tools
curl -s https://raw.githubusercontent.com/josemlwdf/CTFEnum/main/install.sh | bash
# Install various packages
sudo apt install net-tools xxd steghide freerdp2-wayland responder mitmproxy stegsnow cupp openvpn unrar mariadb-client-core ffuf pipx file php exiftool impacket-scripts rlwrap john smbmap smbclient nikto exploitdb hydra wpscan poppler-utils sqlmap hash-identifier enum4linux hashcat dos2unix whatweb docker.io knockd evil-winrm jq ltrace sntp tftp-hpa -y
pipx ensurepath
sudo pip install requests git-dumper pyftpdlib --break-system-packages
# Download and configure additional files
sudo curl -s https://raw.githubusercontent.com/josemlwdf/random_scripts/refs/heads/main/ferox-config.toml -o /etc/feroxbuster/ferox-config.toml
sudo curl -s https://raw.githubusercontent.com/josemlwdf/PasswordPolicyChecker/refs/heads/main/policy_checker.py -o /usr/sbin/policy_checker
sudo chmod +x /usr/sbin/policy_checker
sudo curl -s https://raw.githubusercontent.com/ticarpi/jwt_tool/refs/heads/master/jwt_tool.py -o /usr/sbin/jwt_tool
sudo chmod +x /usr/sbin/jwt_tool
sudo untar /usr/share/seclists/Passwords/Leaked-Databases/rockyou.txt.tar.gz
sudo mv rockyou.txt /usr/share/seclists/Passwords/Leaked-Databases/
# Update locate database
sudo updatedb
# Install ngrok and configure it
curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | \
  sudo gpg --dearmor -o /etc/apt/keyrings/ngrok.gpg && \
  echo "deb [signed-by=/etc/apt/keyrings/ngrok.gpg] https://ngrok-agent.s3.amazonaws.com buster main" | \
  sudo tee /etc/apt/sources.list.d/ngrok.list && \
  sudo apt update -y && sudo apt install ngrok -y
# Prompt for Ngrok token
echo https://dashboard.ngrok.com/get-started/your-authtoken
echo "Ngrok Token:"
read ntoken
ngrok config add-authtoken $ntoken
sudo ngrok config add-authtoken $ntoken
# Generate SSH keys
mkdir ~/.ssh
ssh-keygen -t rsa -b 4096
# Instructions for the user
echo '[!] Download the /opt folder backup from Mega'
echo 'Press Enter when the /opt folder is in place.'
read
sudo ln -s /opt/kerbrute /usr/sbin/kerbrute
sudo chmod +x /usr/sbin/kerbrute
sudo chsh -s /bin/zsh think
rm -f custom_wsl.sh
pipx install git+https://github.com/Pennyw0rth/NetExec
sudo find / -name *$'\r' -exec rm -rf {} \; 2>/dev/null
