#!/bin/bash
pip install -r requirements.txt
pip install flet pyinstaller
pyinstaller --noconfirm --onefile --windowed --icon=DocPro.ico app.py 