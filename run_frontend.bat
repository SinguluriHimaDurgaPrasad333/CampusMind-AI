@echo off
echo ========================================================
echo  Starting CampusMind AI - Frontend Server (Vite)
echo ========================================================
set PATH=C:\Users\himad\AppData\Local\Programs\nodejs;%PATH%
cd /d "%~dp0frontend"
npm run dev
pause
