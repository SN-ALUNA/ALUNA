@echo off
cd /d "%~dp0"

set "PY_CMD="

where py >nul 2>&1
if %errorlevel% equ 0 set "PY_CMD=py -3"

if "%PY_CMD%"=="" (
    where python >nul 2>&1
    if %errorlevel% equ 0 set "PY_CMD=python"
)

if "%PY_CMD%"=="" (
    echo No se encontro ni 'py' ni 'python' en este equipo.
    echo Instala Python desde python.org o habilita el launcher de Python.
    pause
    exit /b 1
)

%PY_CMD% main.py
if %errorlevel% neq 0 (
    echo.
    echo La aplicacion se cerro con errores.
    pause
)
