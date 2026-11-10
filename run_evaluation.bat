@echo off
echo ========================================================
echo  Running CampusMind AI — Automated RAG Evaluation
echo ========================================================
set PYTHONPATH=%~dp0backend
python "%~dp0backend\scripts\run_evaluation.py"
pause
