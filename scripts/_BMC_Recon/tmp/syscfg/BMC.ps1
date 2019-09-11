#Initial step:
##############
# Change $servers & $ipServer if needed 
# Run the this file! 

$servers = @("recon01","recon02","recon03","recon04","recon05","recon06","recon07","recon08","recon09","recon10","recon11","recon12")
$ipServer = @("192.168.11.71","192.168.11.72","192.168.11.73","192.168.11.74","192.168.11.75","192.168.11.76","192.168.11.77","192.168.11.78","192.168.11.79","192.168.11.80","192.168.11.81","192.168.11.82")

########-----Main-Variables-----########
$mask="255.255.255.0"
$newline = "`r`n"
$source = 'c:\tmp\syscfg'
$exe='syscfg.exe'
$file = 'C:\tmp\syscfg\syscfg.exe'
$ipmi = 'C:\tmp\syscfg\msipmi.dll'
$bapi = 'C:\tmp\syscfg\imbapi.dll'


########-----Function-copy-files-----########
function copy-files{
	copy-item -Path $file -Destination "filesystem::\\$server\c$\tmp\syscfg"
	copy-item -Path $ipmi -Destination "filesystem::\\$server\c$\tmp\syscfg"
    copy-item -Path $bapi -Destination "filesystem::\\$server\c$\tmp\syscfg"
	write-output 'copying files are finished'
}

########-----Main-----########
$online = $servers | where { Test-Connection -ComputerName $_ -Count 1 -Quiet }
$i = 0
 foreach ($server in $online){# 
        if (!(test-path "filesystem::\\$server\c$\tmp\syscfg"))
		{
         New-Item -ItemType Directory -Force -Path "filesystem::\\$server\c$\tmp\syscfg"
         copy-files
		}
    copy-files
    $result = Test-Connection $server -Count 1 -ErrorAction SilentlyContinue
    Write-Host $result
     if ($result){
        $prepcmd= 
        "cd " + $source + $newline +
        "$exe /pefc enable reset" + $newline +
        "$exe /u 2 `"root`" `"PU1234$`"" + $newline +     
        "$exe /ue 2 enable 2" + $newline +
        "$exe /up 2 2 admin sol" + $newline +
        "$exe /le 2 static"+' '+ $ipServer[$i] +' ' + $Mask | out-file "$source\$server.cmd" -Encoding ASCII
        }
    $i++
 }# 


 ########-----Copy-files-to-remote-computer-----########
 foreach($scriptToRun in (Get-ChildItem -Path $source -Recurse -Filter "*.cmd")){
    Write-Host "$source\$scriptToRun"
    $server = $scriptToRun.ToString()
    $serverPath =  $server.Substring(0,$server.Length-4)
    Write-Host "Copying to server: $serverPath script"
    copy-item -Path $source\$scriptToRun -Destination "filesystem::\\$serverPath\c$\tmp\syscfg"
	write-Host 'file are copied successfuly to his destination'
 }
 ########-----run-those-files-on-each-computer-all-at-once-----########
 foreach ($server in $servers){
    Write-Host 'runnig script remotely at server:' 
	Write-Host $server
    Invoke-Command -ComputerName $server -AsJob -ScriptBlock {Param($server) cmd /c  c:\tmp\syscfg\$server.cmd } -ArgumentList $server | Wait-Job | Receive-Job
 }