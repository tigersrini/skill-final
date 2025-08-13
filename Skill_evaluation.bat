@echo off
cd /d "%~dp0"
echo Current directory: %CD%
echo.
echo Starting Streamlit application...
echo.

REM Check if Python is installed
where python >nul 2>nul
if errorlevel 1 (
    echo Python is not installed. Opening Windows Store for Python installation...
    start ms-windows-store://pdp/?productid=9PJPW5LDXLZ5
    echo After installing Python, please close this window and run this batch file again.
    pause
    exit /b
)

REM Check if pip is installed
where pip >nul 2>nul
if errorlevel 1 (
    echo pip is not installed. Please install pip.
    pause
    exit /b
)

REM Check if Streamlit is installed
python -c "import streamlit" 2>nul
if errorlevel 1 (
    echo Streamlit is not installed. Installing now...
    pip install streamlit
)

REM Install required Python packages directly (embedded requirements)
pip install pandas plotly openpyxl pillow

REM Check for requirements.txt and install if present
if exist requirements.txt (
    echo Installing required Python packages from requirements.txt...
    pip install -r requirements.txt
)

echo The application will open in your browser automatically.
echo Press Ctrl+C in this terminal to stop the server.
echo.

python -m streamlit run do_not_edit.py --server.port 8501 --server.headless false

echo.
echo Streamlit server stopped.
echo Press any key to exit...
pause > nul
