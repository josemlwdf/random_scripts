$ports = @(21,25,22,445,80,443,4444,5555,6666,7777,8000,8080,8888,9999,11601);

$wslAddress = wsl bash -c "ifconfig eth0 | grep -oP '(?<=inet\s)\d+(\.\d+){3}'"

if ($wslAddress -match '^(\d{1,3}\.){3}\d{1,3}$') {
  Write-Host "WSL IP address: $wslAddress" -ForegroundColor Green
  Write-Host "Ports: $ports" -ForegroundColor Green
}
else {
  Write-Host "Error: Could not find WSL IP address." -ForegroundColor Red
  exit
}

$listenAddress = '0.0.0.0';

netsh int portproxy reset all

$fireWallDisplayName = 'WSL.Port.Forwarding';
$portsStr = $ports -join ",";

foreach ($port in $ports) {
  Invoke-Expression "netsh interface portproxy add v4tov4 listenport=$port listenaddress=$listenAddress connectport=$port connectaddress=$wslAddress";
}

Invoke-Expression "Remove-NetFireWallRule -DisplayName $fireWallDisplayName -ErrorAction SilentlyContinue";
Invoke-Expression "New-NetFireWallRule -DisplayName $fireWallDisplayName -Direction Outbound -LocalPort $portsStr -Action Allow -Protocol TCP";
Invoke-Expression "New-NetFireWallRule -DisplayName $fireWallDisplayName -Direction Inbound -LocalPort $portsStr -Action Allow -Protocol TCP";