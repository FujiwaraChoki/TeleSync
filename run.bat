@echo off
setlocal enabledelayedexpansion

:: Collect all arguments
set "args=%*"

:: Run src\main.py with sys args
python src\main.py %args%
