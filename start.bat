@echo off
echo ========================================
echo   HealthAgent - ???????
echo   ?????streamlit run app.py
echo ========================================
cd /d %~dp0
call streamlit run app.py --server.port 8503
pause
