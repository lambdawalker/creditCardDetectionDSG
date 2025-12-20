@echo off
setlocal enabledelayedexpansion

set /a n=1

for %%f in (*) do (
    if not "%%f"=="%~nx0" (
        :: We wrap the entire new name in quotes to handle spaces/special chars
        ren "%%f" "!n!%%~xf"
        set /a n+=1
    )
)

echo Task Complete.