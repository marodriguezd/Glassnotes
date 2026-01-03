@echo off
echo Building Glassnotes...
pyinstaller --noconsole --onefile --name "Glassnotes" --clean --noconfirm ^
--add-data "src;src" ^
--hidden-import="PyQt6" ^
--hidden-import="qfluentwidgets" ^
run.py
echo.
echo Build Complete! Check the "dist" folder.
pause
