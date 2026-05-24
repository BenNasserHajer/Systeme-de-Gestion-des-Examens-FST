@echo off
echo ========================================
echo   Test d'Authentification
echo ========================================
echo.

echo Verification que le backend est accessible...
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Backend non accessible sur http://localhost:8000
    echo.
    echo Demarrez d'abord le backend:
    echo   START_BACKEND.bat
    echo.
    pause
    exit /b 1
)

echo ✓ Backend accessible
echo.
echo Execution du script de diagnostic...
echo.

python diagnose_auth.py

echo.
pause
