@echo off
echo ========================================================
echo   CampusAI - AI Student Assistance Chatbot Launcher
echo   Project Code: P08 (SIH1631)
echo ========================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH!
    echo Please install Python 3.11, 3.12, or 3.13 from python.org.
    pause
    exit /b 1
)

echo [1/2] Initializing knowledge base and checking dependencies...
python -c "import streamlit, sentence_transformers, chromadb; print('Dependencies verified!')"

echo [2/2] Launching CampusAI Streamlit Application...
python -m streamlit run app.py --server.port 8501 --server.address localhost

pause
