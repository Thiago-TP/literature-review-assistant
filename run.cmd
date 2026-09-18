@echo off
rem Convenience wrapper for Windows, so run.py can be started by double-click
rem as well as from a terminal. The start-up logic itself lives in run.py.
setlocal

where py >nul 2>&1
if %errorlevel%==0 (
  py -3 "%~dp0run.py" %*
  goto :done
)

where python >nul 2>&1
if %errorlevel%==0 (
  python "%~dp0run.py" %*
  goto :done
)

echo Python 3 not found on PATH. Install Python 3.13+ from https://www.python.org/ and try again. 1>&2
exit /b 1

:done
exit /b %errorlevel%
