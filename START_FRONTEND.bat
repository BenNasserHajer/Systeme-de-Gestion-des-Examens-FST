@echo off
echo ========================================
echo   Demarrage du Frontend
echo ========================================
echo.

cd frontend

echo Verification de node_modules...
if not exist node_modules (
    echo Installation des dependances...
    call npm install
)

echo.
echo Demarrage du serveur Next.js...
echo URL: http://localhost:3000
echo Login: http://localhost:3000/login
echo.
echo Appuyez sur Ctrl+C pour arreter
echo.

call npm run dev

pause
