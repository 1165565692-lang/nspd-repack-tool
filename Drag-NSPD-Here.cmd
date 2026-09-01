@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
set "REPACK_PY=%SCRIPT_DIR%src\repack.py"
set "REPACK_PS=%SCRIPT_DIR%scripts\Repack-FromNspdCode.ps1"

if "%~1"=="" goto prompt_path
set "NSPD_PATH=%~1"
goto got_path

:prompt_path
echo Drag an NSPD folder onto this file, or paste the NSPD path below.
echo.
set /p "NSPD_PATH=NSPD path: "

:got_path

if "%NSPD_PATH%"=="" goto no_path

echo.
echo NSPD=%NSPD_PATH%
echo.

if exist "%REPACK_PY%" (
    python "%REPACK_PY%" -NspdPath "%NSPD_PATH%"
    set "EXIT_CODE=%ERRORLEVEL%"
) else if exist "%REPACK_PS%" (
    powershell -NoProfile -ExecutionPolicy Bypass -File "%REPACK_PS%" -NspdPath "%NSPD_PATH%"
    set "EXIT_CODE=%ERRORLEVEL%"
) else (
    echo Repack script not found.
    set "EXIT_CODE=1"
    goto fail
)

if not "%EXIT_CODE%"=="0" (
    echo.
    echo Packing failed. Exit code: %EXIT_CODE%
    goto :fail
)

echo.
echo Done.
goto :end

:no_path
echo No NSPD path provided.

:fail
set "EXIT_CODE=1"

:end
if not defined NO_PAUSE pause
exit /b %EXIT_CODE%