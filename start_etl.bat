@echo off
echo Starting ETL Automation Tool v2.0...

REM Start backend
start "Backend" cmd /k "C:/Users/Saad/anaconda3/envs/myenv/python.exe -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload"

REM Wait 5 seconds
timeout /t 5 /nobreak >nul

REM Start frontend
start "Frontend" cmd /k "C:/Users/Saad/anaconda3/envs/myenv/python.exe -m streamlit run frontend/app.py --server.port 8501 --server.address 0.0.0.0"

REM Wait 8 seconds
timeout /t 8 /nobreak >nul

REM Open browser
start http://localhost:8501

echo ETL Tool is starting...
echo Frontend: http://localhost:8501
echo Backend: http://localhost:8000
