@echo off
echo ========================================
echo DEMARRAGE COMPLET - Surveillance System
echo ========================================
echo.

REM Vérifier que nous sommes dans le bon répertoire
cd /d "c:\Users\dongm\OneDrive\Desktop\projet"

echo [1/4] Vérification de l'environnement...
echo.

REM Vérifier backend
if not exist "server\.venv\Scripts\python.exe" (
    echo ❌ Environnement virtuel Python non trouvé!
    echo    Exécutez d'abord: cd server ^& python -m venv .venv ^& .venv\Scripts\pip install -r requirements.txt
    pause
    exit /b 1
)

REM Vérifier frontend
if not exist "frontend\node_modules" (
    echo ❌ node_modules non trouvé!
    echo    Exécutez d'abord: cd frontend ^& npm install
    pause
    exit /b 1
)

echo ✅ Environnement OK
echo.

echo [2/4] Démarrage du Backend (FastAPI)...
echo.
start "Backend - FastAPI" cmd /k "cd /d c:\Users\dongm\OneDrive\Desktop\projet\server && .venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000"

REM Attendre que le backend démarre
timeout /t 5 /nobreak >nul

echo ✅ Backend démarré sur http://localhost:8000
echo.

echo [3/4] Démarrage du Frontend (Next.js)...
echo.
start "Frontend - Next.js" cmd /k "cd /d c:\Users\dongm\OneDrive\Desktop\projet\frontend && npm run dev"

REM Attendre que le frontend démarre
timeout /t 10 /nobreak >nul

echo ✅ Frontend démarré sur http://localhost:3000
echo.

echo [4/4] Ouverture du navigateur...
echo.
timeout /t 3 /nobreak >nul
start http://localhost:3000

echo.
echo ========================================
echo ✅ SYSTÈME DÉMARRÉ AVEC SUCCÈS
echo ========================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
echo API Docs: http://localhost:8000/docs
echo.
echo Pour arrêter les serveurs, fermez les fenêtres de terminal.
echo.
pause
