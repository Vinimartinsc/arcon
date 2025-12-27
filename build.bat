@echo off
REM ARCON Build Script for Windows

echo === ARCON Production Build ===
echo.

REM Check if PyInstaller is installed
pip list | findstr /I "PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install PyInstaller
)

echo Building ARCON.exe...
echo.

REM Build using the spec file
pyinstaller arcon.spec --onefile --distpath .\dist --buildpath .\build

echo.
echo Build complete!
echo.
echo Executable location: .\dist\arcon.exe
echo.
echo Usage:
echo   - CLI mode:  arcon.exe --archive C:\path\in --output C:\path\out [options]
echo   - UI mode:   arcon.exe --ui
echo.
pause
