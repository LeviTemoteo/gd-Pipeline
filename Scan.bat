@echo off
title gdPipeline - First Scan

cd /d "%~dp0"

echo ----------------------------------------------------
echo   Creating the database and scanning all levels...
echo ----------------------------------------------------
echo.

python FirstScanStarter.py

echo.
echo ---------------------------------------------------
echo            Finished! Let's go Ahead!
echo ---------------------------------------------------
pause