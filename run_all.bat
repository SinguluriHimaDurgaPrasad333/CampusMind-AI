@echo off
echo ========================================================
echo  Launching CampusMind AI — Full Stack Application
echo ========================================================
start "CampusMind AI - Backend API" cmd /k "%~dp0run_backend.bat"
timeout /t 3 /nobreak >nul
start "CampusMind AI - React Frontend" cmd /k "%~dp0run_frontend.bat"
echo.
echo Application is starting!
echo - Frontend: http://localhost:5173
echo - Backend API & Swagger: http://localhost:8000/docs
echo.
pause
