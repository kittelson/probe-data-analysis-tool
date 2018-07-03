@echo off

set SCRIPT="%TEMP%\%RANDOM%-%RANDOM%-%RANDOM%-%RANDOM%.vbs"

echo Set oWS = WScript.CreateObject("WScript.Shell") >> %SCRIPT%
echo sLinkFile = oWS.CurrentDirectory+"\PDAT.lnk" >> %SCRIPT%
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> %SCRIPT%
echo oLink.TargetPath = oWS.CurrentDirectory+"\PDAT\PDAT.exe" >> %SCRIPT%
echo oLink.WorkingDirectory = oWS.CurrentDirectory+"\PDAT" >> %SCRIPT%
echo oLink.IconLocation = oWS.CurrentDirectory+"\PDAT\PDAT_Icon.ico" >> %SCRIPT%
echo oLink.Save >> %SCRIPT%

cscript /nologo %SCRIPT%
del %SCRIPT%