@echo off
set mypath=%cd%
SET /P ANSWER=Are You Sure You Want To Configure iKVM NICs (Y/N)?
echo You chose: %ANSWER%
if /i {%ANSWER%}=={y} (goto :yes)
if /i {%ANSWER%}=={yes} (goto :yes)
goto :no

:yes
echo copying [hostname].bat files to selected servers:
for /f %%i in (%mypath%\fgc_list.txt) do robocopy %mypath%\files \\%%i\c$\IT\scripts\iKVM\ %%i.bat
for /f %%i in (C:\tmp\scripts\fgc_list.txt) do robocopy %mypath%\tool\ \\%%i\c$\IT\scripts\iKVM\
echo done copying files
pause
echo updating ProcName values values on selected servers:
for /f %%i in (%mypath%\fgc_list.txt) do %mypath%\PsExec.exe \\%%i -u produser -p PU1234$ -h -i -d C:\IT\scripts\iKVM\%%i.bat
echo all done
pause
exit /b 0

:no
echo Exiting...
pause
exit /b 1