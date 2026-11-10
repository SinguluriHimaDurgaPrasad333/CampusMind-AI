@echo off
echo ========================================================
echo  Starting CampusMind AI - Backend Server (FastAPI)
echo ========================================================
set PATH=C:\Users\himad\AppData\Local\Programs\Python\Python313;C:\Users\himad\AppData\Local\Programs\Python\Python313\Scripts;%PATH%
set PYTHONPATH=%~dp0backend
python -m uvicorn app.main:app --app-dir "%~dp0backend" --host 0.0.0.0 --port 8000 --reload
pause
