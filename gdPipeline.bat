@echo off
title gdPipeline - Watchdog

cd /d "%~dp0"

echo ------------------------------------------------
echo   gdPipeline has started! Let's go Ahead!
echo ------------------------------------------------
echo.

python gdPipelineStarter.py

echo.
pause