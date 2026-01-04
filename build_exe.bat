@echo off
echo Cleaning up previous builds...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
if exist "Glassnotes.spec" del "Glassnotes.spec"

echo Building Glassnotes...
pyinstaller --noconsole --onefile --name "Glassnotes" --clean --noconfirm ^
--icon="%~dp0assets\icon.ico" ^
--add-data "%~dp0src;src" ^
--add-data "%~dp0assets;assets" ^
--hidden-import="PyQt6" ^
--hidden-import="qfluentwidgets" ^
"%~dp0run.py"

echo.
echo Build Complete! Check the "dist" folder.
echo NOTE: If the icon still looks generic in Explorer, it is likely a Windows Icon Cache issue.
echo Try copying the .exe to a different folder or renaming it to verify.
pause
