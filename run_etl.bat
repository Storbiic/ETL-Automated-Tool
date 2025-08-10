@echo off
echo ========================================
echo    ETL Automation Tool v2.0 Launcher
echo ========================================
echo.

REM Check if conda environment exists
echo 🔍 Checking conda environment...
call C:/Users/Saad/anaconda3/Scripts/activate myenv
if %errorlevel% neq 0 (
    echo ❌ Error: Could not activate conda environment 'myenv'
    echo Please ensure the environment exists and the path is correct
    pause
    exit /b 1
)

echo ✅ Conda environment 'myenv' activated

REM Start backend in a new window
echo 🚀 Starting FastAPI Backend...
start "ETL Backend" cmd /k "C:/Users/Saad/anaconda3/envs/myenv/python.exe -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload"

REM Wait a moment for backend to start
echo ⏳ Waiting for backend to initialize...
timeout /t 5 /nobreak >nul

REM Start frontend in a new window
echo 🎨 Starting Streamlit Frontend...
start "ETL Frontend" cmd /k "C:/Users/Saad/anaconda3/envs/myenv/python.exe -m streamlit run frontend/app.py --server.port 8501 --server.address 0.0.0.0"

REM Wait a moment for frontend to start
echo ⏳ Waiting for frontend to initialize...
timeout /t 8 /nobreak >nul

REM Open browser
echo 🌐 Opening browser...
start http://localhost:8501

echo.
echo ========================================
echo ✅ ETL Automation Tool v2.0 is running!
echo ========================================
echo.
echo 📊 Frontend: http://localhost:8501
echo 🔧 Backend API: http://localhost:8000
echo 📚 API Docs: http://localhost:8000/docs
echo.
echo Press any key to close this launcher...
echo (The backend and frontend will continue running)
pause >nul
