##########################################################################################################
# FIX!!
# * if server pings but not in OS, it wil fail and wont be in the list!!!
# * 1GB NICs link speed - CHECK!! - ADDED, TEST!
# * Wi-Fi adapters - add check DISABLED
# * try to add PARALLEL RUN!!
# * after adding 1gig speed check, all 10gig & 40gig speedss reported as incorrect - FIX!!
#
##########################################################################################################



cls

Set-Item -Path WSMan:\localhost\Client\TrustedHosts -Value * -force

# Classic System#$srvlist = @("Nav", "Main","Output", "Outputspare", "Sync1", "Sync2", "Gateway","FGC01","FGC02","FGC03","FGC04","FGC05","FGC06","FGC07","FGC08","FGC09","FGC10","FGC11","FGC12","FGC13","FGC14","FGC15","FGC16","FGC17","FGC18","FGC19","FGC20","FGC21","FGC22","FGC23","FGC24","FGC25","FGC26","FGC27","FGC28","FGC29","FGC30","FGC31","FGC32","FGC33","FGC34","FGC35","FGC36","FGC37","FGC38","FGCSPARE1","FGCSPARE2","FGCSPARE3","FGCSPARE4")# System with 3rd Rack$srvlist =  @("Main", "Nav", "Output", "Outputspare", "Sync1", "Sync2", "Gateway","FGC01","FGC02","FGC03","FGC04","FGC05","FGC06","FGC07","FGC08","FGC09","FGC10","FGC11","FGC12","FGC13","FGC14","FGC15","FGC16","FGC17","FGC18","FGC19","FGC20","FGC21","FGC22","FGC23","FGC24","FGC25","FGC26","FGC27","FGC28","FGC29","FGC30","FGC31","FGC32","FGC33","FGC34","FGC35","FGC36","FGC37","FGC38","FGCSPARE1","FGCSPARE2","FGCSPARE3","FGCSPARE4", "Recon01","Recon02","Recon03","Recon04","Recon05","Recon06","Recon07","Recon08","Recon09","Recon10","Recon11","Recon12","Render01","Render02")

#$srvlist =  @("Main")

# Get Start Time
$startDTM = (Get-Date)
$global:currDir = Split-Path -Path $MyInvocation.MyCommand.Definition -Parent
$localpath = "c:\tmp"
$htmlfile = "snapshot.html"
$htmlred = "style='background-color:#FF8080'>"
$ciara = "ciara"
$ref_timezone = tzutil /g
$report = "snapshot summary report"
$dt = Get-Date -Format g
$Jobs = @()
$results = @()
$offlist = @()
# get unique snapshot string as reference
$snapshot  = cmd /c 'bcdedit /v | find /i "osdevice"'
$snapshot = $snapshot -split "-"
if ($snapshot[1] -like "*prod*") { $snapshot = ($snapshot[1] -split "prod")[1]}
elseif ($snapshot[1] -like "*dev*") { $snapshot = ($snapshot[1] -split "dev")[1] }

write-host "Testing server connectivity and building a list of online servers.. " -NoNewline -ForegroundColor Yellow
$online = $srvlist | where { Test-Connection -ComputerName $_ -Count 1 -Quiet } #| out-file -filepath $global:currDir\$listfile -Encoding ASCII -append
$offline = $srvlist | where { $online -notcontains $_ } | foreach {
    $offlist += $_
    #$Body+="<H2>$("$_ [offline]")</H2>"
    #Convertto-Html -Fragment -As Tables
    $obj = New-Object PSObject
    $obj | Add-Member -MemberType NoteProperty -Name Hostname      -Value "~~~$_"
    $obj | Add-Member -MemberType NoteProperty -Name "C: drive"    -Value ''
    $obj | Add-Member -MemberType NoteProperty -Name "D: drive"    -Value ''
    $obj | Add-Member -MemberType NoteProperty -Name "E: drive"    -Value ''
    $obj | Add-Member -MemberType NoteProperty -Name "V: drive"    -Value ''
    $obj | Add-Member -MemberType NoteProperty -Name Remarks       -Value '%%%Server is OFFLINE'
    $results += $obj
}

write-host 'Done' -ForegroundColor Green

if ($offlist) {
    $offlist = $offlist -join ', '
    write-host ''
    write-warning "found offline servers: $offlist"
}


# removed table attrib: width: 100%;
[string]$css = @'
<style>
    html body       { font-family: Verdana, Geneva, sans-serif; font-size: 12px; height: 100%; margin: 0; overflow: auto; }
    #header         { background: #0066a1; color: #ffffff; width: 100% }
    #headerTop      { padding: 10px; }
    .logo1          { float: left;  font-size: 25px; font-weight: bold; padding: 0 7px 0 0; }
    .logo2          { float: left;  font-size: 25px; }
    .logo3          { float: right; font-size: 12px; text-align: right; }
    .headerRow1     { background: #66a3c7; height: 5px; }
    .serverRow      { background: #000000; color: #ffffff; font-size: 32px; padding: 10px; text-align: center; text-transform: uppercase; }
    .sectionRow     { background: #0066a1; color: #ffffff; font-size: 13px; padding: 1px 5px!important; font-weight: bold; height: 15px!important; }
    table           { background: #eaebec; border: #cccccc 1px solid; border-collapse: collapse; margin: 0; }
    table th        { background: #ededed; border-top: 1px solid #fafafa; border-bottom: 1px solid #e0e0e0; border-left: 1px solid #e0e0e0; height: 45px; min-width: 55px; padding: 0px 15px; text-transform: capitalize; }
    table tr        { text-align: left; }
    table td        { border-top: 1px solid #ffffff; border-bottom: 1px solid #e0e0e0; border-left: 1px solid #e0e0e0; height: 55px; min-width: 55px; padding: 0px 10px; }
    table td:first-child   { min-width: 175px; text-align: left; }
    table tr:last-child td { border-bottom: 0; }
    table tr:hover td      { background: #f2f2f2; }
    table tr:hover td.sectionRow { background: #0066a1; width: 100% }
    tr:nth-child(even) {background: #CCC}
    tr:nth-child(odd) {background: #FFF}
    tr td:nth-child(even){ width:1%; white-space:nowrap; }
    tr td:nth-child(odd) { width:1%; white-space:nowrap; }
</style>
'@

# Page header rows...
[string]$body = @"
<div id="header"> 
    <div id="headerTop">
        <div class="logo1"></div>
        <div class="logo2">$report</div>
        <div class="logo3">&nbsp;<br/>Generated by $env:computername on $dt</div>
        <div style="clear:both;"></div>
    </div>
    <div style="clear:both;"></div>
</div>

<script>
function sortTable(n) {
  var table, rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;
  table = document.getElementById("myTable");
  switching = true;
  //Set the sorting direction to ascending:
  dir = "asc"; 
  /*Make a loop that will continue until
  no switching has been done:*/
  while (switching) {
    //start by saying: no switching is done:
    switching = false;
    rows = table.getElementsByTagName("TR");
    /*Loop through all table rows (except the
    first, which contains table headers):*/
    for (i = 1; i < (rows.length - 1); i++) {
      //start by saying there should be no switching:
      shouldSwitch = false;
      /*Get the two elements you want to compare,
      one from current row and one from the next:*/
      x = rows[i].getElementsByTagName("TD")[n];
      y = rows[i + 1].getElementsByTagName("TD")[n];
      /*check if the two rows should switch place,
      based on the direction, asc or desc:*/
      if (dir == "asc") {
        if (x.innerHTML.toLowerCase() > y.innerHTML.toLowerCase()) {
          //if so, mark as a switch and break the loop:
          shouldSwitch= true;
          break;
        }
      } else if (dir == "desc") {
        if (x.innerHTML.toLowerCase() < y.innerHTML.toLowerCase()) {
          //if so, mark as a switch and break the loop:
          shouldSwitch= true;
          break;
        }
      }
    }
    if (shouldSwitch) {
      /*If a switch has been marked, make the switch
      and mark that a switch has been done:*/
      rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
      switching = true;
      //Each time a switch is done, increase this count by 1:
      switchcount ++;      
    } else {
      /*If no switching has been done AND the direction is "asc",
      set the direction to "desc" and run the while loop again.*/
      if (switchcount == 0 && dir == "asc") {
        dir = "desc";
        switching = true;
      }
    }
  }
}
</script>
"@


# Scriptblock for getting all the info from single server
$sbGetInfo =  {
    param($srv, $ven, $time, $timezone, $srvip, $procname, $procip, $refsnap)
    $remarks = "%%%"
    $obj = New-Object PSObject

    # NAMES
    $obj | Add-Member -MemberType NoteProperty -Name Hostname -Value $srv

    # STORAGE
    $C = ''
    $D = ''
    $E = ''
    $V = ''

    # check if C: volume exists and has a correct label
    $c_drive = Get-WmiObject -Class Win32_logicaldisk | where { $_.deviceid -eq 'C:' }
    if ($c_drive) {
        if ($c_drive.VolumeName -ne "System") {
            if ($C[0] -ne '~') { $C = "~~~$C" }
            $remarks += "C: drive: incorrect label:::"
        }
        #$E_size = "$([math]::round($e_drive.Size/1074000000))" + 'GB'
        $obj | Add-Member -MemberType NoteProperty -Name "C: drive" -Value "$C$($c_drive.VolumeName) [$([math]::round($c_drive.Size/1074000000))GB] / FREE: $([math]::round($c_drive.FreeSpace/1074000000))GB"  
    }
    else {
        $remarks += "C: drive is missing:::"
        $obj | Add-Member -MemberType NoteProperty -Name "C: drive" -Value ''
    }
    
    # check if D: volume exists, has a correct label & min. size
    $d_drive = Get-WmiObject -Class Win32_logicaldisk | where { $_.deviceid -eq 'D:' }
    if ($d_drive) {
        if ($d_drive.VolumeName -ne "Data") {
            if ($D[0] -ne '~') { $D = "~~~$D" }
            $remarks += "E: drive: incorrect label:::"
        }
        #$D_size = "$([math]::round($d_drive.Size/1074000000))" + 'GB'
        if ($env:computername -eq "gateway") {
            if ($([math]::round($d_drive.Size/1074000000)) -le 950) {
                if ($D[0] -ne '~') { $D = "~~~$D" }
                $remarks += "D: drive: size is smaller than expected:::"
            }
        }
        else {
            if ($([math]::round($d_drive.Size/1074000000)) -le 1900) {
                if ($D[0] -ne '~') { $D = "~~~$D" }
                $remarks += "D: drive: size is smaller than expected:::"
            }
        }
        $obj | Add-Member -MemberType NoteProperty -Name "D: drive" -Value "$D$($d_drive.VolumeName) [$([math]::round($d_drive.Size/1074000000))GB] / FREE: $([math]::round($d_drive.FreeSpace/1074000000))GB"  
    }
    else {
        $remarks += "D: drive is missing:::"
        $obj | Add-Member -MemberType NoteProperty -Name "D: drive" -Value ''
    }      

    # check if E: volume exists and has a correct label
    $e_drive = Get-WmiObject -Class Win32_logicaldisk | where { $_.deviceid -eq 'E:' }
    if ( ((($srv -like "main*") -or ($srv -like "nav*") -or ($srv -like "output*") -or ($srv -like "gateway*")) -and (!$e_drive)) ) {
        if ($E[0] -ne '~') { $E = "~~~$E" }
        $remarks += "E: drive is missing:::"
    }
    if ($e_drive) {
        if ($e_drive.VolumeName -ne "Storage") {
            if ($E[0] -ne '~') { $E = "~~~$E" }
            $remarks += "E: drive: incorrect label:::"
        }
        $obj | Add-Member -MemberType NoteProperty -Name "E: drive" -Value "$E$($e_drive.VolumeName) [$([math]::round($e_drive.Size/1074000000))GB] / FREE: $([math]::round($e_drive.FreeSpace/1074000000))GB" 
    }
    else { $obj | Add-Member -MemberType NoteProperty -Name "E: drive" -Value '' }

    # check if V: volume exists and has a correct label
    $v_drive = Get-WmiObject -Class Win32_logicaldisk | where { $_.deviceid -eq 'V:' }
    if ($v_drive) {
        if ($v_drive.VolumeName -ne "VHDs") {
            if ($V[0] -ne '~') { $V = "~~~$V" }
            $remarks += "V: drive: incorrect label:::"
        }
        if ($([math]::round($v_drive.FreeSpace/1074000000) -le 10)) {
            if ($V[0] -ne '~') { $V = "~~~$V" }
            $remarks += "V: drive: insufficient space left!!:::"
        }
        $obj | Add-Member -MemberType NoteProperty -Name "V: drive" -Value "$V$($v_drive.VolumeName) [$([math]::round($v_drive.Size/1074000000))GB] / FREE: $([math]::round($v_drive.FreeSpace/1074000000))GB"
    }
    else {
        if ($V[0] -ne '~') { $V = "~~~$V" }
        $remarks += "V: drive is missing:::"
        $obj | Add-Member -MemberType NoteProperty -Name "V: drive" -Value ''
    }

    $obj | Add-Member -MemberType NoteProperty -Name Remarks -Value $remarks

    return $obj
}#scripblock

write-host ''
write-host "running report on: " -ForegroundColor Yellow #-NoNewline

foreach ($server in $online) {
    write-host $server  
    $results += Invoke-Command -ComputerName $server -AsJob -ScriptBlock $sbGetInfo -ArgumentList $server | Wait-Job | Receive-Job | Select-Object -Property * -ExcludeProperty PSComputerName,RunspaceID,PSShowComputerName
}

# Convert to HTML
[string[]]$html = $results | ConvertTo-Html -head $css -body $body

# Make line breaks in cells
$html = $html.replace(":::", "</br>")
$html = $html.replace(">~~~", " style='background-color:#FF8080'>")
$html = $html.replace(">%%%", " style='color:red'>")

$html | Out-File $currDir\$htmlfile
Invoke-Expression $currDir\$htmlfile

# Get End Time
$endDTM = (Get-Date)
# Echo Time elapsed
$runtime = [math]::Round($(($endDTM-$startDTM).totalseconds))
write-host ''
write-host "All Done, elapsed time: $runtime seconds" -ForegroundColor Green