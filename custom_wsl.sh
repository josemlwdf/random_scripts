sudo touch ~/.hushlogin
sudo touch /root/.hushlogin
echo 'Windows Username:'
read wusername
ln -s /mnt/c/Users/$wusername/Downloads ~/Downloads
sudo ln -s /mnt/c/Users/$wusername/Downloads /root/Downloads

sudo echo 'notepad.exe $1' > /usr/sbin/edit
sudo chmod +x /usr/sbin/edit

ln -s /dev/null .lesshst
ln -s /dev/null .viminfo
ln -s /dev/null .wget-hsts

echo '10 * * * * /usr/sbin/backup' | crontab -
echo '2 * * * * /usr/bin/rm -rf /wsl*' | crontab -

curl -s https://raw.githubusercontent.com/josemlwdf/random_scripts/refs/heads/main/kali-zshrc -o ~/.zshrc
curl -s https://raw.githubusercontent.com/josemlwdf/random_scripts/refs/heads/main/bashrc -o ~/.bashrc
sudo cp ~/.bashrc /root/.bashrc
sudo cp ~/.zshrc /root/.zshrc

sudo apt install git -y
sudo echo 'ruby /opt/username-anarchy/username-anarchy' > /usr/sbin/username-anarchy
sudo chmod +x /usr/sbin/username-anarchy

sudo curl -s https://raw.githubusercontent.com/josemlwdf/random_scripts/refs/heads/main/untar -o /usr/sbin/untar
sudo chmod +x /usr/sbin/untar 
sudo curl -s https://raw.githubusercontent.com/josemlwdf/random_scripts/refs/heads/main/hist -o /usr/sbin/hist
sudo chmod +x /usr/sbin/hist 
sudo curl -s https://raw.githubusercontent.com/josemlwdf/Decodify/refs/heads/master/dcode -o /usr/sbin/dcode
sudo chmod +x /usr/sbin/dcode 
sudo curl -s https://raw.githubusercontent.com/josemlwdf/random_scripts/refs/heads/main/urlencode -o /usr/sbin/urlencode
sudo chmod +x /usr/sbin/urlencode 
sudo curl -s https://raw.githubusercontent.com/josemlwdf/random_scripts/refs/heads/main/smbserver -o /usr/sbin/smbserver
sudo chmod +x /usr/sbin/smbserver 
sudo curl -s https://raw.githubusercontent.com/josemlwdf/random_scripts/refs/heads/main/PowerShellBase64ReverseShell.py -o /usr/sbin/shellps1
sudo chmod +x /usr/sbin/shellps1 
sudo curl -s https://raw.githubusercontent.com/josemlwdf/random_scripts/refs/heads/main/shells -o /usr/sbin/shells
sudo chmod +x /usr/sbin/shells 
sudo curl -s https://raw.githubusercontent.com/josemlwdf/random_scripts/refs/heads/main/pyftplibd -o /usr/sbin/pyftplibd
sudo chmod +x /usr/sbin/pyftplibd 
sudo curl -s https://raw.githubusercontent.com/josemlwdf/random_scripts/refs/heads/main/ligolox -o /usr/sbin/ligolox
sudo chmod +x /usr/sbin/ligolox 
sudo curl -s https://raw.githubusercontent.com/josemlwdf/random_scripts/refs/heads/main/IP -o /usr/sbin/IP
sudo chmod +x /usr/sbin/IP 
sudo curl -s https://raw.githubusercontent.com/josemlwdf/random_scripts/refs/heads/main/create -o /usr/sbin/create
sudo chmod +x /usr/sbin/create 
sudo curl -s https://raw.githubusercontent.com/josemlwdf/random_scripts/refs/heads/main/home -o /usr/sbin/home
sudo chmod +x /usr/sbin/home 
sudo curl -s https://raw.githubusercontent.com/josemlwdf/random_scripts/refs/heads/main/ips -o /usr/sbin/ips
sudo chmod +x /usr/sbin/ips 
sudo curl -s https://raw.githubusercontent.com/josemlwdf/random_scripts/refs/heads/main/http -o /usr/sbin/http
sudo chmod +x /usr/sbin/http 
sudo curl -s https://raw.githubusercontent.com/josemlwdf/random_scripts/refs/heads/main/fix_zsh -o /usr/sbin/fix_zsh
sudo chmod +x /usr/sbin/fix_zsh 
sudo curl -s https://raw.githubusercontent.com/josemlwdf/random_scripts/refs/heads/main/academy -o /usr/sbin/academy
sudo chmod +x /usr/sbin/academy 
sudo curl -s https://raw.githubusercontent.com/josemlwdf/random_scripts/refs/heads/main/backup -o /usr/sbin/backup
sudo chmod +x /usr/sbin/backup 

sudo curl -s https://raw.githubusercontent.com/josemlwdf/random_scripts/refs/heads/main/thm -o /usr/sbin/thm
sudo chmod +x /usr/sbin/thm 
sudo curl -s https://raw.githubusercontent.com/josemlwdf/random_scripts/refs/heads/main/htb -o /usr/sbin/htb
sudo chmod +x /usr/sbin/htb 
sudo curl -s https://raw.githubusercontent.com/josemlwdf/random_scripts/refs/heads/main/offsec -o /usr/sbin/offsec
sudo chmod +x /usr/sbin/offsec 

echo 'deb http://http.kali.org/kali kali-rolling main non-free contrib' | sudo tee -a /etc/apt/sources.list
echo 'deb-src http://http.kali.org/kali kali-rolling main non-free contrib' | sudo tee -a /etc/apt/sources.list
curl -s https://raw.githubusercontent.com/josemlwdf/CTFEnum/main/install.sh | bash
sudo apt install steghide -y
sudo apt install stegsnow -y
wget https://github.com/josemlwdf/random_scripts/raw/refs/heads/main/stegseek_0.6-1.deb
sudo apt install ./stegseek_0.6-1.deb
rm ./stegseek_0.6-1.deb
sudo apt install ffuf -y
sudo apt install pipx -y
sudo apt install git -y
sudo apt install file -y
sudo apt install php -y
sudo apt install exiftool -y
sudo apt install impacket-scripts -y
sudo apt install rlwrap -y
sudo apt install john -y
sudo apt install smbmap -y
sudo apt install smbclient -y
sudo apt install nikto -y
sudo apt install searchsploit -y
sudo pipx ensurepath
sudo pipx install git+https://github.com/Pennyw0rth/NetExec
sudo apt install hydra -y
sudo apt install wpscan -y
sudo apt install poppler-utils -y
sudo apt install sqlmap -y
sudo apt install hash-identifier -y
sudo apt install enum4linux -y
sudo apt install hashcat -y
sudo apt-get install poppler-utils -y
sudo apt install dos2unix -y
sudo apt install whatweb -y
sudo apt install docker.io -y
sudo apt install knockd -y
sudo apt install rlwrap 
sudo apt install evil-winrm -y
sudo apt install jq -y
sudo apt install ltrace -y
sudo apt install sntp -y
sudo pip install requests
sudo pip install git-dumper
sudo apt install tftp-hpa -y
sudo curl -s https://raw.githubusercontent.com/josemlwdf/random_scripts/refs/heads/main/ncx -o /usr/sbin/ncx
sudo chmod +x /usr/sbin/ncx 
sudo curl https://raw.githubusercontent.com/josemlwdf/random_scripts/refs/heads/main/ferox-config.toml -o /etc/feroxbuster/ferox-config.toml

sudo updatedb
curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null && echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list && sudo apt update && sudo apt install ngrok
echo https://dashboard.ngrok.com/get-started/your-authtoken
echo Ngrok Token:
read ntoken
sudo ngrok config add-authtoken $ntoken
ssh-keygen -t rsa -b 4096

echo '[!] Download the /opt folder backup from Mega'
echo 'Press Enter when /opt folder will be in place.'
read
echo sudo ln -s /opt/kerbrute /usr/sbin/kerbrute
echo '[!] Install Caido and Google Chrome'
echo sudo mv caido-cli /usr/sbin
echo sudo apt -y install ./google-chrome-stable_current_amd64.deb
echo sudo ln -s /usr/bin/google-chrome /usr/sbin/chrome
