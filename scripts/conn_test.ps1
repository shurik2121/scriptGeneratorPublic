$mnglist = @("Main","Nav", "Output", "Outputspare", "Sync1", "Sync2", "Gateway")
$fgclist = @("FGC01","FGC02","FGC03","FGC04","FGC05","FGC06","FGC07","FGC08","FGC09","FGC10","FGC11","FGC12","FGC13","FGC14","FGC15","FGC16","FGC17","FGC18","FGC19","FGC20","FGC21","FGC22","FGC23","FGC24","FGC25","FGC26","FGC27","FGC28","FGC29","FGC30","FGC31","FGC32","FGC33","FGC34","FGC35","FGC36","FGC37","FGC38","FGCSPARE1","FGCSPARE2","FGCSPARE3","FGCSPARE4")
$proclist = @("PROC01","PROC02","PROC03","PROC04","PROC05","PROC06","PROC07","PROC08","PROC09","PROC10","PROC11","PROC12","PROC13","PROC14","PROC15","PROC16","PROC17","PROC18","PROC19","PROC20","PROC21","PROC22","PROC23","PROC24","PROC25","PROC26","PROC27","PROC28","PROC29","PROC30","PROC31","PROC32","PROC33","PROC34","PROC35","PROC36","PROC37","PROC38","PROCSPARE1","PROCSPARE2","PROCSPARE3","PROCSPARE4")
$srvselect = "Management servers", "FGCs", "PROCs", "ALL" | Out-GridView -OutputMode Single -Title 'Select server group to test:'

$path = "c:\tmp" 

$header = @"
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="en" xml:lang="en">
<head>
<title>Server Connectivity Report</title>
<style type="text/css">
<!--
body {
background-color: #E0E0E0;
font-family: sans-serif
}
table, th, td {
background-color: white;
border-collapse:collapse;
border: 1px solid black;
padding: 5px
}
-->
</style>
"@

$body = @"
<h1>$srvselect</h1>
<p>The following report was run on $(get-date).</p>
"@

if ($srvselect -eq "Management servers") {
    $list = $mnglist
}

elseif ($srvselect -eq "FGCs") {
    $list = $fgclist
}

elseif ($srvselect -eq "PROCs") {
    $list = $proclist
}

elseif ($srvselect -eq "ALL") {
    $list = $mnglist + $fgclist + $proclist
}


$results = foreach ($server in $list) { 
    if (Test-Connection $server -Count 1 -ea 0 -Quiet) { 
        $status = "Up"
        write-host $server -ForegroundColor yellow -NoNewline
        write-host " is " -NoNewline
        write-host "Online" -ForegroundColor green
    } 
    else { 
        $status = "Down"
        write-host $server -ForegroundColor yellow -NoNewline
        write-host " is " -NoNewline
        write-host "Offline" -ForegroundColor red
    }
        [PSCustomObject]@{
            Name = $server
            Status = $status
        }
    }

$results | ConvertTo-Html -head $header -body $body | foreach {
    $PSItem -replace "<td>Down</td>", "<td style='background-color:#FF8080'>Down</td>"
} | Out-File $path\uptime.html
Invoke-Expression $path\uptime.html