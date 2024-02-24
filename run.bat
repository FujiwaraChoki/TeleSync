:: For simplicity in windows Copied from the closed issue #1 by N7co9
@echo off
setlocal enabledelayedexpansion

:: Collect all arguments
set "args=%*"

:: Run src\main.py with sys args
python src\main.py %args%
