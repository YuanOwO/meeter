@echo off
title meeter
echo "install require modules..."
pip install -r requirements.txt
echo "start the program..."
python main.py
echo "stopped"
pause