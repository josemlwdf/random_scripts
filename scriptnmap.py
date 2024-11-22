#!/usr/bin/env python3

import subprocess
import time

def run_nmap(targets):
    print('[!] Searching for servers TCP')
    cmd = [
        'sudo', 'nmap', '-Pn', '-n', '-p21,22,25,80,443,445,88,389,8080,8000', 
        '-T5', targets, '--open', '-oG', 'assets_discovery.txt', '--source-port', '53', '--data-string', 'becycure'
    ]
    subprocess.run(cmd)

def create_host_files():
    with open('assets_discovery.txt', 'r') as f:
        lines = f.readlines()

    smb_hosts = set()
    ssh_hosts = set()
    http_hosts = set()
    dc_hosts = set()
    ftp_hosts = set()
    smtp_hosts = set()

    for line in lines:
        if 'Ports' in line:
            ip = line.split()[1]
            if '445/open' in line:
                smb_hosts.add(ip)
            if '22/open' in line:
                ssh_hosts.add(ip)
            if any(port in line for port in ['80/open', '443/open', '8080/open', '8000/open']):
                http_hosts.add(ip)
            if any(port in line for port in ['88/open', '389/open']):
                dc_hosts.add(ip)
            if '21/open' in line:
                ftp_hosts.add(ip)
            if '25/open' in line:
                smtp_hosts.add(ip)

    write_hosts_to_file('smb_hosts.txt', smb_hosts)
    write_hosts_to_file('ssh_hosts.txt', ssh_hosts)
    write_hosts_to_file('http_hosts.txt', http_hosts)
    write_hosts_to_file('dc_hosts.txt', dc_hosts)
    write_hosts_to_file('ftp_hosts.txt', ftp_hosts)
    write_hosts_to_file('smtp_hosts.txt', smtp_hosts)

def write_hosts_to_file(filename, hosts):
    with open(filename, 'w') as f:
        for host in sorted(hosts):
            f.write(f"{host}\n")

scanned_hosts = []

def ctfenum_scan(file):
    global scanned_hosts
    with open(file, 'r') as f:
        hosts = f.readlines()
    for host in hosts:
        if host in scanned_hosts: continue
        scanned_hosts.append(host)
        host = host.strip()
        if host:
            print(f'[!] Scanning {file.split("_")[0].upper()} Server: {host}')
            subprocess.run(['/usr/sbin/ctfenum', host])
            time.sleep(5)

def main():
    targets = input('[!] Enter NMAP targets: ')
    run_nmap(targets)
    print('\n[!] Creating hosts files\n')
    time.sleep(5)
    create_host_files()

    print('\n[!] Scanning DC / AD')
    with open('dc_hosts.txt', 'r') as f:
        DC01 = f.readline().strip()
    if DC01:
        subprocess.run(['/usr/sbin/ctfenum', DC01])
        time.sleep(5)

    for file in ['ssh_hosts.txt', 'ftp_hosts.txt', 'http_hosts.txt', 'smb_hosts.txt']:
        ctfenum_scan(file)

if __name__ == "__main__":
    main()
