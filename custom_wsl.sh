#!/bin/bash

# Launch script oneliner
# Only works in kali-linuw on WSL
# DO NOT USE SUDO
# echo ''>script;nano script;chmod +x script;./script

set -euo pipefail

# Add Kali repository
echo 'deb http://http.kali.org/kali kali-rolling main non-free contrib' | sudo tee -a /etc/apt/sources.list > /dev/null
echo 'deb-src http://http.kali.org/kali kali-rolling main non-free contrib' | sudo tee -a /etc/apt/sources.list > /dev/null

sudo apt update -y
user=$(awk -F: '$3 == 1000 {print $1}' /etc/passwd)
sudo chsh -s /bin/zsh $user
sudo chown $user:$user /opt 2>/dev/null
sudo chmod 777 /opt 2>/dev/null
# Suppress login messages
sudo touch ~/.hushlogin
sudo touch /root/.hushlogin
mkdir -p ~/CTF
PLATFORMS=("HackMyVM" "HTB" "DockerLabs" "OSCP" "OTW" "THM"
         "VulnHub" "Vulnyx")
for platform in "${PLATFORMS[@]}"; do
    mkdir -p ~/CTF/$platform
done 
mkdir -p ~/CTF/OSCP/Play
sudo curl -s https://raw.githubusercontent.com/josemlwdf/random_scripts/refs/heads/main/wsl.conf -o /etc/wsl.conf

# INSTALL GEMINI
sudo apt install nodejs npm -y && sudo npm install -g @google/gemini-cli

echo "Your Windows Username:"
read wusername
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
sudo ln -s /usr/bin/python3 /usr/sbin/python 2>/dev/null
# Install Git
sudo apt install git -y
# Install PIP
sudo apt install python3-pip -y
sudo pip3 install fierce tabulate colorama requests git-dumper pyftpdlib requests pypykatz scapy Cython --break-system-packages

sudo ln -s /usr/local/bin/git-dumper /usr/sbin/gitdumper
# Create username-anarchy script
echo 'ruby /opt/username-anarchy/username-anarchy $@' | sudo tee /usr/sbin/username-anarchy > /dev/null

# Download and setup various scripts, checking for curl success
SCRIPTS=("untar" "hist" "urlencode" "smbserver" "fpingc" "cve_checker"
         "shells" "pyftplibd" "ligolox" "IP" "create" "home" "ips" "http" "fix_zsh"
         "academy" "backup" "thm" "htb" "offsec" "ncx" "upgrade")
for script in "${SCRIPTS[@]}"; do
    sudo curl -s https://raw.githubusercontent.com/josemlwdf/random_scripts/refs/heads/main/$script -o /usr/sbin/$script
done

# Install other tools
sudo curl -s https://raw.githubusercontent.com/josemlwdf/CTFEnum/main/install.sh | bash
# Install various packages
sudo apt install oracle-instantclient-sqlplus krb5-user nmap gdb subfinder stegseek fping pkg-config btop hashid imagemagick traceroute libfuse3-dev python3-dev net-tools cewl pipx xxd steghide html2text cifs-utils medusa responder libpcap-dev mitmproxy nfs-common stegsnow cupp openvpn unrar mariadb-client-core ffuf file php exiftool impacket-scripts rlwrap john smbmap smbclient nikto exploitdb hydra wpscan poppler-utils sqlmap hash-identifier enum4linux hashcat dos2unix whatweb docker.io knockd evil-winrm jq strace ltrace ntpsec-ntpdig tftp-hpa -y
# Config for gdb
echo 'set disassembly-flavor intel' > ~/.gdbinit
curl -s https://raw.githubusercontent.com/hugsy/gef/refs/heads/main/gef.py -o ~/.gdbinit-gef.py; echo source ~/.gdbinit-gef.py >> ~/.gdbinit

# Subbrute
cd /opt; sudo git clone https://github.com/TheRook/subbrute.git >> /dev/null 2>&1; 
sudo ln -s /opt/subbrute/subbrute.py /usr/sbin/subbrute
sudo sh -c "echo /usr/lib/oracle/12.2/client64/lib > /etc/ld.so.conf.d/oracle-instantclient.conf";sudo ldconfig
sudo nmap --script-updatedb
pipx ensurepath
pipx install git+https://github.com/hvs-consulting/nfs-security-tooling.git

# Download and configure additional files
sudo curl -s https://raw.githubusercontent.com/josemlwdf/random_scripts/refs/heads/main/ferox-config.toml -o /etc/feroxbuster/ferox-config.toml
sudo curl -s https://raw.githubusercontent.com/josemlwdf/PasswordPolicyChecker/refs/heads/main/policy_checker.py -o /usr/sbin/policy_checker
sudo curl -s https://raw.githubusercontent.com/ticarpi/jwt_tool/refs/heads/master/jwt_tool.py -o /usr/sbin/jwt_tool
sudo curl -s https://raw.githubusercontent.com/josemlwdf/Decodify/refs/heads/master/dcode -o /usr/sbin/dcode
sudo curl -s https://raw.githubusercontent.com/josemlwdf/check_ip_info/refs/heads/main/get_ip_info  -o /usr/sbin/get_ip_info
sudo curl -s https://raw.githubusercontent.com/josemlwdf/random_scripts/refs/heads/main/PowerShellBase64ReverseShell.py -o /usr/sbin/shellps1
sudo curl -s https://raw.githubusercontent.com/josemlwdf/random_scripts/refs/heads/main/docker.zip -o /opt/docker.zip
sudo curl -s https://raw.githubusercontent.com/josemlwdf/random_scripts/refs/heads/main/cptcracker-ng -o /usr/sbin/cptcracker-ng
sudo curl -s https://raw.githubusercontent.com/edoardottt/takeover/master/takeover.py -o /usr/sbin/takeover; sudo chmod +x /usr/sbin/takeover
cd /dev/shm; wget https://github.com/RedTeamPentesting/pretender/releases/download/v1.3.2/pretender_Linux_x86_64.tar.gz; untar pretender_Linux_x86_64.tar.gz; chmod +x pretender; rm LICENSE README.md; sudo mv pretender /usr/sbin; rm pretender_Linux_x86_64.tar.gz 
cd /opt; sudo wget https://raw.githubusercontent.com/pentestmonkey/smtp-user-enum/refs/heads/master/smtp-user-enum.pl; sudo chmod +x smtp-user-enum.pl; sudo ln -s /opt/smtp-user-enum.pl /usr/sbin/smtp_user_enum
sudo curl -s https://jetmore.org/john/code/swaks/files/swaks-20240103.0/swaks -o /usr/sbin/swaks
sudo curl -s https://github.com/josemlwdf/random_scripts/raw/refs/heads/main/cookiemonster  -o /usr/sbin/cookiemonster
sudo curl -s https://raw.githubusercontent.com/josemlwdf/random_scripts/refs/heads/main/py_server.py -o /usr/sbin/http
sudo curl -s https://raw.githubusercontent.com/josemlwdf/random_scripts/refs/heads/main/pcredz -o /usr/sbin/pcredz
sudo curl -s https://raw.githubusercontent.com/josemlwdf/PCAP_Parser/refs/heads/main/pcap_parser.py -o /usr/sbin/pcap_parser
sudo curl -s https://raw.githubusercontent.com/josemlwdf/Unescaper/refs/heads/main/unescaper.py -o /usr/sbin/unescaper

# bat
sudo wget https://github.com/josemlwdf/random_scripts/raw/refs/heads/main/bat_0.25.0_amd64.deb; sudo apt install -y ./bat_0.25.0_amd64.deb; sudo rm -f ./bat_0.25.0_amd64.deb

sudo chmod +x /usr/sbin/*

sudo untar /usr/share/seclists/Passwords/Leaked-Databases/rockyou.txt.tar.gz
sudo mv rockyou.txt /usr/share/seclists/Passwords/Leaked-Databases/
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
read timebreak
sudo curl https://raw.githubusercontent.com/drtychai/wordlists/refs/heads/master/fasttrack.txt -o /opt/wordlists/fasttrack.txt
sudo chmod +x -R /opt/*
sudo ln -s /opt/kerbrute /usr/sbin/kerbrute
sudo chmod +x /usr/sbin/kerbrute
rm -f $0
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.zshrc
export PATH="$HOME/.cargo/bin:$PATH"
source ~/.zshrc
pipx install git+https://github.com/Pennyw0rth/NetExec

# curlie
curl -sS https://webinstall.dev/curlie | bash

echo removing installation garbage
sudo rm /opt/smtp-user-enum.pl.1 2>/dev/null
sudo find / -name *$'\r' -exec rm -rf {} \; 2>/dev/null
sudo rm $0

# Update locate database
echo updating file database
sudo updatedb
