<#
    .SYNOPSIS
    Add-NewUsersRandomPasswords.ps1

    .DESCRIPTION
    Create Active Directory users with a random password using PowerShell.

    .LINK
    www.alitajran.com/bulk-create-ad-users-with-random-passwords/

    .NOTES
    Written by: ALI TAJRAN
    Website:    www.alitajran.com
    LinkedIn:   linkedin.com/in/alitajran

    .CHANGELOG
    V1.00, 03/16/2020 - Initial version
    V2.00, 01/28/2024 - Added try/catch and changed to splatting
    V3.00, 06/07/2024 - Adapted for PowerShell 2.0 compatibility
    V4.00, 06/07/2024 - Fixed object name syntax issues
#>

# Import active directory module for running AD cmdlets
Import-Module ActiveDirectory

$LogDate = Get-Date -f dd-MM-yyyy_HHmmffff

# Location of CSV file that contains the users information
$ImportPath = "C:\NewUsersRP.csv"

# Location of CSV file that will be exported to including random passwords
$ExportPath = "C:\Passwords_$LogDate.csv"

# Define UPN
$UPN = "soupedecode.local"

# Set the password length characters
$PasswordLength = 14

# Store the data from NewUsersRP.csv in the $ADUsers variable
$ADUsers = Import-Csv $ImportPath

# Create an array to store the user data for export
$ExportData = @()

# Randomize passwords
function Get-RandomPassword {
    Param(
        [Parameter(Mandatory = $true)]
        [int]$Length
    )
    if ($Length -lt 4) {
        return
    }

    $Numbers = 1..9
    $LettersLower = 'abcdefghijklmnopqrstuvwxyz'.ToCharArray()
    $LettersUpper = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.ToCharArray()
    $Special = '!@#$%^&*()=+[{}]/?<>'.ToCharArray()

    # For the 4 character types (upper, lower, numerical, and special)
    $N_Count = [math]::Round($Length * .2)
    $L_Count = [math]::Round($Length * .4)
    $U_Count = [math]::Round($Length * .2)
    $S_Count = [math]::Round($Length * .2)

    $Pswrd = @()
    $Pswrd += $LettersLower | Get-Random -Count $L_Count
    $Pswrd += $Numbers | Get-Random -Count $N_Count
    $Pswrd += $LettersUpper | Get-Random -Count $U_Count
    $Pswrd += $Special | Get-Random -Count $S_Count

    # If the password length isn't long enough (due to rounding), add X special characters
    if ($Pswrd.length -lt $Length) {
        $Pswrd += $Special | Get-Random -Count ($Length - $Pswrd.length)
    }

    # Grab the $Pswrd string and randomize the order
    $Pswrd = ($Pswrd | Get-Random -Count $Length) -join ""
    return $Pswrd
}

# Loop through each row containing user details in the CSV file
foreach ($User in $ADUsers) {
    $password = Get-RandomPassword -Length $PasswordLength
    try {
        # Check to see if the user already exists in AD
        if (Get-ADUser -Filter "SamAccountName -eq '$($User.username)'") {
            # If the user already exists, provide a warning
            Write-Host "A user with the username $($User.username) already exists in Active Directory." -ForegroundColor Yellow
        }
        else {
            # User does not exist then proceed to create the new user account
			# To organize the users in an specific Organizational Unit use: -Path $User.ou
            New-ADUser -SamAccountName $User.username `
                       -UserPrincipalName "$($User.username)@$UPN" `
                       -Name "$($User.firstname) $($User.lastname)" `
                       -GivenName $User.firstname `
                       -Surname $User.lastname `
                       -Initials $User.initials `
                       -Enabled $True `
                       -DisplayName "$($User.firstname) $($User.lastname)" `
                       -City $User.city `
                       -PostalCode $User.zipcode `
                       -Company $User.company `
                       -State $User.state `
                       -StreetAddress $User.streetaddress `
                       -OfficePhone $User.telephone `
                       -EmailAddress $User.email `
                       -Title $User.jobtitle `
                       -Department $User.department `
                       -AccountPassword (ConvertTo-SecureString $password -AsPlainText -Force) `
                       -ChangePasswordAtLogon $False `
		       -Description $User.description

            # If the user is created, add the data to the export array
            $User | Add-Member -MemberType NoteProperty -Name "Initial Password" -Value $password -Force
            $ExportData += $User

            # If the user is created, show a message
            Write-Host "The user $($User.username) is created." -ForegroundColor Green
        }
    }
    catch {
        # If an exception occurs during user creation, handle it here
        Write-Host "Failed to create user $($User.username) - $_" -ForegroundColor Red
    }
}

# Export the data to CSV file
if ($ExportData.Count -gt 0) {
    $ExportData | Export-Csv -Path $ExportPath -NoTypeInformation -Encoding UTF8
    Write-Host "CSV file is exported to $ExportPath." -ForegroundColor Cyan
}
else {
    Write-Host "No users were created. CSV file will not be exported." -ForegroundColor Cyan
}
