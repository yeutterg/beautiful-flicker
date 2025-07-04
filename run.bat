@echo off
REM Beautiful Flicker Run Script for Windows
REM Usage: run.bat [port]
REM Example: run.bat 3000

REM Default port
set PORT=%1
if "%PORT%"=="" set PORT=8080

echo Beautiful Flicker - Flask Web Application
echo ========================================
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Docker is not installed. Please install Docker Desktop for Windows first.
    exit /b 1
)

REM Check if docker-compose is installed
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Docker Compose is not installed. Please install Docker Compose first.
    exit /b 1
)

REM Check if port is already in use
netstat -an | findstr :%PORT% | findstr LISTENING >nul 2>&1
if %errorlevel% equ 0 (
    echo Warning: Port %PORT% appears to be in use!
    echo.
    echo You can either:
    echo 1. Stop the process using port %PORT%
    echo 2. Choose a different port: run.bat 3000
    echo.
    echo Press Ctrl+C to cancel or any key to continue anyway...
    pause >nul
)

echo Starting Beautiful Flicker on port %PORT%...
echo.

REM Set the port environment variable and run
set PORT=%PORT%
docker-compose up --build

REM Note: Use Ctrl+C to stop the application