@echo off
title gdPipeline - Watchdog

cd /d "%~dp0"

echo ------------------------------------------------
echo   gdPipeline has started! Go play some levels.
echo ------------------------------------------------
echo.

python gdPipelineStarter.py

echo.
pause