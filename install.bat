@echo off
:: Ponder installer for Windows
:: Double-click this file to install

echo.
echo   Ponder installer
echo.

:: Find Python
where python >nul 2>&1
if %errorlevel% == 0 (
    set PY=python
    goto run
)
where python3 >nul 2>&1
if %errorlevel% == 0 (
    set PY=python3
    goto run
)

echo   Python not found.
echo   Download it from: https://www.python.org/downloads
echo   Make sure to tick "Add Python to PATH" during install.
echo.
pause
exit /b 1

:run
echo   Using %PY%
echo.
%PY% install.py
pause
