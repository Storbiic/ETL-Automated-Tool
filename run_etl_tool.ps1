# ETL Automation Tool v2.0 PowerShell Launcher
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   ETL Automation Tool v2.0 Launcher" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Function to check if port is in use
function Test-Port {
    param([int]$Port)
    try {
        $connection = New-Object System.Net.Sockets.TcpClient
        $connection.Connect("localhost", $Port)
        $connection.Close()
        return $true
    }
    catch {
        return $false
    }
}

# Check if ports are available
Write-Host "🔍 Checking ports..." -ForegroundColor Yellow
if (Test-Port 8000) {
    Write-Host "⚠️  Port 8000 is already in use. Backend might already be running." -ForegroundColor Yellow
}
if (Test-Port 8501) {
    Write-Host "⚠️  Port 8501 is already in use. Frontend might already be running." -ForegroundColor Yellow
}

# Start backend
Write-Host "🚀 Starting FastAPI Backend..." -ForegroundColor Green
$backendJob = Start-Job -ScriptBlock {
    Set-Location "C:\Users\Saad\Desktop\YAZAKI  Internship\etl_app"
    & "C:/Users/Saad/anaconda3/envs/myenv/python.exe" -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
}

# Wait for backend to start
Write-Host "⏳ Waiting for backend to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Start frontend
Write-Host "🎨 Starting Streamlit Frontend..." -ForegroundColor Green
$frontendJob = Start-Job -ScriptBlock {
    Set-Location "C:\Users\Saad\Desktop\YAZAKI  Internship\etl_app"
    & "C:/Users/Saad/anaconda3/envs/myenv/python.exe" -m streamlit run frontend/app.py --server.port 8501 --server.address 0.0.0.0
}

# Wait for frontend to start
Write-Host "⏳ Waiting for frontend to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 8

# Open browser
Write-Host "🌐 Opening browser..." -ForegroundColor Green
Start-Process "http://localhost:8501"

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "✅ ETL Automation Tool v2.0 is running!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Frontend: http://localhost:8501" -ForegroundColor Cyan
Write-Host "🔧 Backend API: http://localhost:8000" -ForegroundColor Cyan
Write-Host "📚 API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop both services..." -ForegroundColor Yellow

# Keep script running and monitor jobs
try {
    while ($true) {
        Start-Sleep -Seconds 5
        
        # Check if jobs are still running
        if ($backendJob.State -eq "Failed") {
            Write-Host "❌ Backend job failed!" -ForegroundColor Red
            break
        }
        if ($frontendJob.State -eq "Failed") {
            Write-Host "❌ Frontend job failed!" -ForegroundColor Red
            break
        }
    }
}
finally {
    # Cleanup jobs
    Write-Host "🛑 Stopping services..." -ForegroundColor Yellow
    Stop-Job $backendJob, $frontendJob -ErrorAction SilentlyContinue
    Remove-Job $backendJob, $frontendJob -ErrorAction SilentlyContinue
    Write-Host "✅ Services stopped." -ForegroundColor Green
}
