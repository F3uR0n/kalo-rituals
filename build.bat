@echo off
setlocal enabledelayedexpansion

echo ============================================================
echo  Kalo Rituals - PyInstaller Build Script
echo ============================================================
echo.

REM ── Step 1: Verify Python version ───────────────────────────────────────────
echo [1/5] Checking Python version...
python --version
if errorlevel 1 (
    echo ERROR: Python not found in PATH. Install Python 3.11 or 3.12 and retry.
    pause & exit /b 1
)

REM Check for Python 3.14 - PyInstaller may not support it yet
for /f "tokens=2 delims= " %%v in ('python --version 2^>^&1') do set PYVER=%%v
echo Detected Python version: %PYVER%
if "%PYVER:~0,4%"=="3.14" (
    echo.
    echo WARNING: Python 3.14 detected. PyInstaller support for 3.14 is not
    echo guaranteed. If the build fails, install Python 3.11 or 3.12 and use
    echo that interpreter instead:
    echo   py -3.11 -m pip install pyinstaller
    echo   py -3.11 -m PyInstaller kalo_rituals.spec
    echo.
    pause
)

REM ── Step 2: Install / upgrade PyInstaller ───────────────────────────────────
echo [2/5] Installing PyInstaller...
pip install --upgrade "pyinstaller>=6.0"
if errorlevel 1 (
    echo ERROR: pip install failed.
    pause & exit /b 1
)

REM ── Step 3: Clean previous build artifacts ──────────────────────────────────
echo.
echo [3/5] Cleaning previous build...
if exist build    rmdir /s /q build
if exist "dist\KaloRituals" rmdir /s /q "dist\KaloRituals"
echo Done.

REM ── Step 4: Run PyInstaller ──────────────────────────────────────────────────
echo.
echo [4/5] Running PyInstaller (this takes 1-3 minutes)...
pyinstaller kalo_rituals.spec --clean
if errorlevel 1 (
    echo.
    echo BUILD FAILED. Check the output above for errors.
    echo Common fixes:
    echo   - Wrong Python version: use Python 3.11 or 3.12
    echo   - Missing freeglut DLL: check OpenGL\DLLS\ folder exists
    echo   - Try: pyinstaller kalo_rituals.spec --clean --log-level DEBUG
    pause & exit /b 1
)

REM ── Step 5: Verify output ────────────────────────────────────────────────────
echo.
echo [5/5] Verifying output...
if exist "dist\KaloRituals\KaloRituals.exe" (
    echo.
    echo ============================================================
    echo  BUILD SUCCESSFUL
    echo  Executable : dist\KaloRituals\KaloRituals.exe
    echo  Distribute : zip the entire dist\KaloRituals\ folder
    echo ============================================================
) else (
    echo ERROR: KaloRituals.exe not found in dist\KaloRituals\
    pause & exit /b 1
)

echo.
echo Press any key to open the output folder...
pause >nul
explorer "dist\KaloRituals"
