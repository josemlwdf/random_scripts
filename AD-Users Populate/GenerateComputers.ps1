# Function to register a computer on the domain
# Define the range of computers and servers
$numberOfComputers = 90

# Register Servers
$serverNames = @(
    "WebServer",
    "DatabaseServer",
    "FileServer",
    "MailServer",
    "BackupServer",
    "ApplicationServer",
    "PrintServer",
    "ProxyServer",
    "MonitoringServer",
    "CitrixServer"
)

Import-Module ActiveDirectory

foreach ($serverName in $serverNames) {
	New-ADComputer -Name $serverName -SamAccountName $serverName
}

# Register Computers
for ($i = 1; $i -le $numberOfComputers; $i++) {
    $computerName = "PC-$i"
    New-ADComputer -Name $computerName -SamAccountName $computerName
}

Write-Host "Registration completed for servers and computers."
