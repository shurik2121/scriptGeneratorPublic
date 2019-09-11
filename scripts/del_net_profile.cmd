@echo off
SET /P ANSWER=Are You Sure You Want To Delete Network Profiles(Y/N)?
echo You choose: %ANSWER%
if /i {%ANSWER%}=={y} (goto :yes)
if /i {%ANSWER%}=={yes} (goto :yes)
goto :no

:yes
reg delete "HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Network" /v Config /f
echo all done
pause
exit /b 0

:no
echo Exiting...
pause
exit /b 1
