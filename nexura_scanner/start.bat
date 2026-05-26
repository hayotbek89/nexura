@echo off
title NEXURA Scanner
cd /d "%~dp0"

echo ===================================
echo   NEXURA Scanner — Ishga tushirish
echo ===================================
echo.

:: Backend server
echo [1/2] Backend server ishga tushmoqda...
start "NEXURA Backend" cmd /c "python -m uvicorn nexura.web.app:app --host 0.0.0.0 --port 8080"

timeout /t 3 /nobreak >nul

:: Frontend server
echo [2/2] Frontend server ishga tushmoqda...
cd frontend
start "NEXURA Frontend" cmd /c "npm run dev"
cd ..

echo.
echo ===================================
echo   NEXURA ishga tushdi!
echo ===================================
echo.
echo   Frontend: http://localhost:5173
echo   Backend:  http://localhost:8080
echo   API:      http://localhost:8080/api/status
echo.
echo   CLI buyruqlari:
echo     python -m nexura quick example.com
echo     python -m nexura scan "example.com ni tekshir"
echo.
echo   O'chirish uchun: start_stop.bat
echo.
pause
