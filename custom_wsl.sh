#!/bin/bash

# Launch script oneliner and put the content of the hole script on it
# Made for kali-linux on WSL
# DO NOT USE SUDO
# echo ''>script;nano script;chmod +x script;bash -x ./script

set -euo pipefail

# Add Kali repository
grep -qxF 'deb http://http.kali.org/kali kali-rolling main non-free contrib' /etc/apt/sources.list || \
echo 'deb http://http.kali.org/kali kali-rolling main non-free contrib' | sudo tee -a /etc/apt/sources.list
wget http://http.kali.org/kali/pool/main/k/kali-archive-keyring/kali-archive-keyring_2025.1_all.deb
sudo apt install ./kali-archive-keyring*.deb
rm ./kali-archive-keyring*.deb

sudo apt update -y
user=$(awk -F: '$3 == 1000 {print $1}' /etc/passwd)
sudo chsh -s /bin/zsh $user
sudo chsh -s /bin/zsh root
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
sudo /usr/bin/curl -s https://raw.githubusercontent.com/josemlwdf/random_scripts/refs/heads/main/wsl.conf -o /etc/wsl.conf

# INSTALL GEMINI
sudo apt install nodejs npm -y
sudo npm install -g @google/gemini-cli

echo "Your Windows Username:"
read wusername
# Create symlinks to Windows Downloads folder, force if they exist
ln -sf /mnt/c/Users/$wusername/Downloads ~/Downloads  2>/dev/null
sudo ln -sf /mnt/c/Users/$wusername/Downloads /root/Downloads  2>/dev/null

# Create an edit script
echo 'notepad.exe "$1"' | sudo tee /usr/sbin/edit >/dev/null
sudo chmod +x /usr/sbin/edit
# Redirect history and other files to /dev/null
ln -sf /dev/null ~/.lesshst
ln -sf /dev/null ~/.viminfo
ln -sf /dev/null ~/.wget-hsts
ln -sf /dev/null ~/.python_history
# Append cron jobs safely, handling missing crontab case
(echo '10 * * * * /usr/sbin/backup'; echo '2 * * * * /usr/bin/rm -rf /wsl*'; echo '2 * * * * /usr/bin/rm -rf ~/*.tmp*'; echo '2 * * * * /usr/bin/rm -rf /tmp/*'; echo '@reboot echo "nameserver 8.8.8.8" > /etc/resolv.conf
' ) | sudo crontab -

sudo ln -s /usr/bin/python3 /usr/sbin/python 2>/dev/null
# Install Git
sudo apt install git -y
# Install PIP
sudo apt install python3-pip -y
sudo pip3 install bloodyAD fierce tabulate colorama requests git-dumper pyftpdlib requests pypykatz scapy Cython ratelimit --break-system-packages

sudo ln -s /usr/local/bin/git-dumper /usr/sbin/gitdumper 2>/dev/null
# Create username-anarchy script
echo 'ruby /opt/username-anarchy/username-anarchy $@' | sudo tee /usr/sbin/username-anarchy >/dev/null

# Download and setup various scripts, checking for /usr/bin/curl success
SCRIPTS=("untar" "hist" "urlencode" "smbserver" "fpingc" "cve_checker"
         "shells" "pyftplibd" "ligolox" "IP" "create" "home" "ips" "http" "fix_zsh"
         "academy" "backup" "thm" "htb" "offsec" "ncx" "upgrade" "beep")
for script in "${SCRIPTS[@]}"; do
    sudo /usr/bin/curl -s https://raw.githubusercontent.com/josemlwdf/random_scripts/refs/heads/main/$script -o /usr/sbin/$script 2>/dev/null
done

# Install CTFEnum
sudo /usr/bin/curl -s https://raw.githubusercontent.com/josemlwdf/CTFEnum/main/install.sh | bash

mkdir -p /opt/Windows
cd /opt/Windows

sudo apt install unzip 

# Download AccessChk
sudo wget https://github.com/josemlwdf/random_scripts/raw/refs/heads/main/AccessChk.zip 2>/dev/null
sudo unzip AccessChk.zip 2>/dev/null
sudo rm -f AccessChk.zip 2>/dev/null
sudo rm -f Eula.txt 2>/dev/null

sudo /usr/bin/wget https://github.com/josemlwdf/ExploitWindowsPrivileges/releases/download/v0.1.0/SeDebugPrivilegeExploit.exe 2>/dev/null
sudo /usr/bin/wget https://github.com/josemlwdf/ExploitWindowsPrivileges/releases/download/v0.1.0/SeTakeOwnershipPrivilegeExploit.exe 2>/dev/null
sudo /usr/bin/wget https://github.com/josemlwdf/ExploitWindowsPrivileges/releases/download/v0.1.0/SeLoadDriverPrivilegeExploit.tar.gz 2>/dev/null
sudo /usr/bin/wget https://github.com/josemlwdf/ExploitWindowsPrivileges/releases/download/v0.1.0/ServerOperators.exe 2>/dev/null
sudo /usr/bin/wget https://github.com/josemlwdf/ExploitWindowsPrivileges/raw/refs/heads/main/Kernel/CVE-2021-36934.exe 2>/dev/null
sudo /usr/bin/wget https://raw.githubusercontent.com/josemlwdf/ExploitWindowsPrivileges/refs/heads/main/Kernel/CVE-2021-1675.ps1 2>/dev/null
sudo /usr/bin/wget https://github.com/josemlwdf/ExploitWindowsPrivileges/raw/refs/heads/main/Kernel/CVE-2020-0668.tar.gz 2>/dev/null
sudo /usr/bin/wget https://github.com/josemlwdf/ExploitWindowsPrivileges/raw/refs/heads/main/Perms/SharpChrome.exe 2>/dev/null
sudo /usr/bin/wget https://github.com/josemlwdf/ExploitWindowsPrivileges/raw/refs/heads/main/Perms/SharpUp.exe 2>/dev/null
sudo /usr/bin/wget https://github.com/josemlwdf/random_scripts/raw/refs/heads/main/Seatbelt.exe 2>/dev/null
sudo /usr/bin/wget https://github.com/josemlwdf/random_scripts/raw/refs/heads/main/Watson.exe 2>/dev/null
sudo /usr/bin/wget https://raw.githubusercontent.com/Arvanaghi/SessionGopher/refs/heads/master/SessionGopher.ps1 2>/dev/null
sudo /usr/bin/wget https://github.com/AlessandroZ/LaZagne/releases/download/v2.4.7/LaZagne.exe 2>/dev/null
sudo /usr/bin/wget https://github.com/josemlwdf/random_scripts/raw/refs/heads/main/cmd.exe 2>/dev/null
sudo /usr/bin/wget https://raw.githubusercontent.com/josemlwdf/random_scripts/refs/heads/main/lnk_creator.ps1 2>/dev/null
sudo /usr/bin/wget https://github.com/josemlwdf/random_scripts/raw/refs/heads/main/hhupd.exe 2>/dev/null
sudo /usr/bin/wget https://github.com/josemlwdf/random_scripts/raw/refs/heads/main/Snaffler.exe 2>/dev/null
sudo /usr/bin/wget https://github.com/josemlwdf/random_scripts/raw/refs/heads/main/Inveigh.exe 2>/dev/null
sudo /usr/bin/wget https://raw.githubusercontent.com/josemlwdf/random_scripts/refs/heads/main/Inveigh.ps1 2>/dev/null
sudo /usr/bin/wget https://raw.githubusercontent.com/josemlwdf/DomainPasswordSpray/refs/heads/master/DomainPasswordSpray.ps1 2>/dev/null
sudo /usr/bin/wget https://github.com/josemlwdf/random_scripts/raw/refs/heads/main/WMIC.exe 2>/dev/null
sudo /usr/bin/wget https://github.com/josemlwdf/random_scripts/raw/refs/heads/main/Group3r.exe 2>/dev/null

# Install various packages
PKGS=(
golang libatk-bridge2.0-0 libcups2 libxcomposite1 libxrandr2 libxdamage1 libpango-1.0-0
libnss3 libxshmfence1 libgbm-dev libxkbcommon0 oracle-instantclient-sqlplus krb5-user
nmap lsof gdb subfinder p7zip-full stegseek fping pkg-config btop hashid imagemagick
traceroute libfuse3-dev python3-dev net-tools cewl pipx xxd steghide html2text cifs-utils
medusa responder mitmproxy nfs-common stegsnow cupp openvpn unrar man mitm6 wafw00f
mariadb-client-core ffuf file php exiftool impacket-scripts python3-impacket rlwrap
john smbmap smbclient nikto exploitdb hydra wpscan poppler-utils sqlmap hash-identifier
enum4linux hashcat dos2unix whatweb docker.io knockd evil-winrm jq strace ltrace
ntpsec-ntpdig tftp-hpa keepassxc-minimal onesixtyone krbrelayx
)

for pkg in "${PKGS[@]}"; do
  printf '\n=== Installing: %s ===\n' "$pkg"
  if sudo DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends --ignore-missing "$pkg"; then
    printf 'OK: %s\n' "$pkg"
  else
    printf 'FAILED: %s (logged)\n' "$pkg"
    echo "$pkg" >> failed_packages.txt
  fi
done

# Try to fix unresolved deps at the end
sudo apt-get -f install -y || true

if [ -s failed_packages.txt ]; then
  printf '\nSome packages failed to install. See failed_packages.txt\n'
  cat failed_packages.txt
else
  printf '\nAll packages installed (or were ignored/missing).\n'
fi

sudo ln -s /usr/bin/pdftotext /usr/sbin/pdf2text 2>/dev/null

# Install Gowitness
go install github.com/sensepost/gowitness@latest; sudo mv $HOME/go/bin/gowitness /usr/sbin

# Config for gdb
echo 'set disassembly-flavor intel' > ~/.gdbinit
/usr/bin/wget https://raw.githubusercontent.com/hugsy/gef/refs/heads/main/gef.py 2>/dev/null; echo source ~/.gdbinit-gef.py >> ~/.gdbinit

# Subbrute
cd /opt; sudo git clone https://github.com/TheRook/subbrute.git >> /dev/null 2>&1; 
sudo ln -s /opt/subbrute/subbrute.py /usr/sbin/subbrute 2>/dev/null
sudo sh -c "echo /usr/lib/oracle/12.2/client64/lib > /etc/ld.so.conf.d/oracle-instantclient.conf";sudo ldconfig
sudo nmap --script-updatedb 2>/dev/null
pipx ensurepath 2>/dev/null
pipx install git+https://github.com/hvs-consulting/nfs-security-tooling.git 2>/dev/null

# Download and configure additional files
sudo /usr/bin/wget https://raw.githubusercontent.com/josemlwdf/random_scripts/refs/heads/main/ferox-config.toml -O /etc/feroxbuster/ferox-config.toml 2>/dev/null
sudo /usr/bin/wget https://raw.githubusercontent.com/josemlwdf/PasswordPolicyChecker/refs/heads/main/policy_checker.py -O /usr/sbin/policy_checker 2>/dev/null
sudo /usr/bin/wget https://raw.githubusercontent.com/ticarpi/jwt_tool/refs/heads/master/jwt_tool.py -O /usr/sbin/jwt_tool 2>/dev/null
sudo /usr/bin/wget https://raw.githubusercontent.com/josemlwdf/Decodify/refs/heads/master/dcode -O /usr/sbin/dcode 2>/dev/null
sudo /usr/bin/wget https://raw.githubusercontent.com/josemlwdf/check_ip_info/refs/heads/main/get_ip_info  -O /usr/sbin/get_ip_info 2>/dev/null
sudo /usr/bin/wgets https://raw.githubusercontent.com/josemlwdf/random_scripts/refs/heads/main/PowerShellBase64ReverseShell.py -O /usr/sbin/shellps1 2>/dev/null
sudo /usr/bin/wget https://raw.githubusercontent.com/josemlwdf/random_scripts/refs/heads/main/docker.zip -O /opt/docker.zip 2>/dev/null
sudo /usr/bin/wget https://raw.githubusercontent.com/josemlwdf/random_scripts/refs/heads/main/cptcracker-ng -O /usr/sbin/cptcracker-ng 2>/dev/null
sudo /usr/bin/wget https://raw.githubusercontent.com/edoardottt/takeover/master/takeover.py -O /usr/sbin/takeover; sudo chmod +x /usr/sbin/takeover 2>/dev/null
cd /dev/shm; /usr/bin/wget https://github.com/RedTeamPentesting/pretender/releases/download/v1.3.2/pretender_Linux_x86_64.tar.gz; untar pretender_Linux_x86_64.tar.gz; chmod +x pretender; rm LICENSE README.md; sudo mv pretender /usr/sbin; rm pretender_Linux_x86_64.tar.gz 
cd /opt; sudo /usr/bin/wget https://raw.githubusercontent.com/pentestmonkey/smtp-user-enum/refs/heads/master/smtp-user-enum.pl; sudo chmod +x smtp-user-enum.pl; sudo ln -s /opt/smtp-user-enum.pl /usr/sbin/smtp_user_enum
sudo /usr/bin/wget https://jetmore.org/john/code/swaks/files/swaks-20240103.0/swaks -O /usr/sbin/swaks 2>/dev/null
sudo /usr/bin/wget https://github.com/josemlwdf/random_scripts/raw/refs/heads/main/cookiemonster -O /usr/sbin/cookiemonster 2>/dev/null
sudo /usr/bin/wget https://raw.githubusercontent.com/josemlwdf/random_scripts/refs/heads/main/py_server.py -O /usr/sbin/http 2>/dev/null
sudo /usr/bin/wget https://raw.githubusercontent.com/josemlwdf/random_scripts/refs/heads/main/pcredz -O /usr/sbin/pcredz 2>/dev/null
sudo /usr/bin/wget https://raw.githubusercontent.com/josemlwdf/PCAP_Parser/refs/heads/main/pcap_parser.py -O /usr/sbin/pcap_parser 2>/dev/null
sudo /usr/bin/wget https://raw.githubusercontent.com/josemlwdf/Unescaper/refs/heads/main/unescaper.py -O /usr/sbin/unescaper 2>/dev/null
sudo /usr/bin/wget https://github.com/josemlwdf/random_scripts/raw/refs/heads/main/evtx_dump -O /usr/sbin/evtx_dump 2>/dev/null
sudo /usr/bin/wget https://raw.githubusercontent.com/josemlwdf/keepass4brute/refs/heads/master/keepass4brute.sh -O /usr/sbin/keepass4brute 2>/dev/null
sudo /usr/bin/wget https://raw.githubusercontent.com/josemlwdf/Windows-Exploit-Suggester/refs/heads/master/windows-exploit-suggester.py -O /usr/sbin/windows-exploit-suggester 2>/dev/null

#linkedin2username
git clone https://github.com/initstring/linkedin2username && cd linkedin2username
sudo pip install -r requirements.txt --break-system-packages
echo '#!/bin/bash' | sudo tee /usr/sbin/linkedin2username 2>/dev/null
echo 'python3 /opt/linkedin2username/linkedin2username .py "$@"' | sudo tee -a /usr/sbin/linkedin2username 2>/dev/null 
sudo chmod +x /usr/sbin/linkedin2username

cd /opt

# bat
sudo wget https://github.com/josemlwdf/random_scripts/raw/refs/heads/main/bat_0.25.0_amd64.deb; sudo apt install -y ./bat_0.25.0_amd64.deb 2>/dev/null; sudo rm -f ./bat_0.25.0_amd64.deb 2>/dev/null

sudo chmod +x /usr/sbin/* 2>/dev/null

sudo untar /usr/share/seclists/Passwords/Leaked-Databases/rockyou.txt.tar.gz
sudo mv rockyou.txt /usr/share/seclists/Passwords/Leaked-Databases/ 2>/dev/null

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
sudo /usr/bin/curl https://raw.githubusercontent.com/drtychai/wordlists/refs/heads/master/fasttrack.txt -o /opt/wordlists/fasttrack.txt
sudo ln -sf /opt/google/chrome/chrome /usr/sbin/chrome 2>/dev/null
sudo ln -sf /opt/Windows/pywerview/pywerview.py /usr/sbin/pywerview 2>/dev/null
echo '/usr/sbin/chrome --proxy-server="http://localhost:8080"' > /tmp/chrome-proxy && chmod +x /tmp/chrome-proxy
sudo mv /tmp/chrome-proxy /usr/sbin/chrome-proxy
sudo chmod +x -R /opt/*
sudo ln -s /opt/kerbrute /usr/sbin/kerbrute
sudo chmod +x /usr/sbin/kerbrute

# Download and setup bash and zsh configs
curl -s https://raw.githubusercontent.com/josemlwdf/random_scripts/refs/heads/main/kali-zshrc -o ~/.zshrc
curl -s https://raw.githubusercontent.com/josemlwdf/random_scripts/refs/heads/main/bashrc -o ~/.bashrc
curl -s https://raw.githubusercontent.com/josemlwdf/random_scripts/refs/heads/main/zsh_history -o ~/.zsh_history
sudo cp ~/.bashrc /root/.bashrc 2>/dev/null
sudo cp ~/.zshrc /root/.zshrc 2>/dev/null
sudo cp ~/.zsh_history /root/.zsh_history 2>/dev/null
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.zshrc
export PATH="$HOME/.cargo/bin:$PATH"
pipx install git+https://github.com/Pennyw0rth/NetExec
/home/think/.local/bin/nxc --version

echo "Removing installation garbage"
sudo find / -name *$'\r' -exec rm -rf {} \; 2>/dev/null

# Install gcloud-cli
cd /opt
sudo /usr/bin/curl -s -O https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-cli-linux-x86_64.tar.gz && sudo untar google-cloud-cli-linux-x86_64.tar.gz && sudo ./google-cloud-sdk/install.sh
sudo rm google-cloud-cli-linux-x86_64.tar.gz

echo 'BONUS: Launch this Script Powershell as Administrator on Windows to redirect the connections to your common Windows ports to your WSL.'
echo ' -> https://raw.githubusercontent.com/josemlwdf/random_scripts/refs/heads/main/portforward.ps1'

# curlie
curl -sS https://webinstall.dev/curlie | bash

sudo activate-global-python-argcomplete

# Mount G drive on WSL
$(drv=G; mountpoint="/mnt/$(echo $drv | tr '[:upper:]' '[:lower:]')"; echo "$drv: $mountpoint drvfs defaults 0 0" | sudo tee -a /etc/fstab; sudo mkdir -p "$mountpoint"; sudo mount -t drvfs "$drv:" "$mountpoint"; sudo systemctl daemon-reload)

# Update locate database
echo updating file database
sudo updatedb






