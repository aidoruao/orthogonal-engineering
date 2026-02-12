@echo off
REM ==========================================================================
REM VISIBLE DAEMON LAUNCHER
REM Self-Automative Master System with Terminal Visibility
REM ==========================================================================

title Self-Automative Daemon - VISIBLE MODE

echo.
echo ========================================================================
echo  STARTING VISIBLE DAEMON
echo ========================================================================
echo.
echo This daemon will show you:
echo   - Real-time heartbeats every 10 seconds
echo   - Every HTTP request received
echo   - All file changes detected in repository
echo   - Sigma_LORA constraint validations
echo   - Color-coded log messages
echo.
echo Press Ctrl+C to stop the daemon
echo.
echo ========================================================================
echo.

REM Check if watching a directory (set this path to your repo)
set WATCH_PATH=%CD%

REM Run the visible daemon
python VISIBLE_DAEMON.py --host 127.0.0.1 --port 5001 --watch "%WATCH_PATH%"

pause
