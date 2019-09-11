@echo off

SET /P ANSWER=Are You Sure You Want To Configure iKVM NICs (Y/N)?
echo You chose: %ANSWER%
if /i {%ANSWER%}=={y} (goto :yes)
if /i {%ANSWER%}=={yes} (goto :yes)
goto :no

:yes
echo Please make sure the updated fgc_list.txt is present at this server's "C:\tmp\scripts" location
echo Please make sure that ALL [hostname].cmd files are present at this server's "C:\tmp\scripts\iKVM" folder
pause
echo copying [hostname].cmd files to selected servers:
for /f %%i in (C:\tmp\scripts\fgc_list.txt) do robocopy C:\tmp\scripts\iKVM\ \\%%i\c$\tmp\scripts\ %%i.cmd
echo done copying files
pause
echo updating ProcName values values on selected servers:
for /f %%i in (C:\tmp\scripts\fgc_list.txt) do C:\tmp\scripts\PsExec.exe \\%%i -u produser -p PU1234$ -h -i -d C:\tmp\scripts\%%i.cmd
echo all done
pause
exit /b 0

:no
echo Exiting...
pause
exit /b 1