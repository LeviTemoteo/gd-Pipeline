@echo off
title Python requirements

cd /d "%~dp0"

echo updating pip install...
python -m pip install --upgrade pip --quiet

echo installing requirements...
pip install -r requirements.txt

echo.
echo Finished!
pause