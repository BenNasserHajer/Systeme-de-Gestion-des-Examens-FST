@echo off
echo ========================================
echo   Demarrage du Backend
echo ========================================
echo.

cd server

echo Activation de l'environnement virtuel...
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
    echo ✓ Environnement virtuel active
) else (
    echo ⚠ Environnement virtuel non trouve
    echo   Creation de l'environnement...
    python -m venv .venv
    call .venv\Scripts\activate.bat
    echo   Installation des dependances...
    pip install -r requirements.txt
)

echo.
echo Demarrage du serveur FastAPI...
echo URL: http://localhost:8000
echo Docs: http://localhost:8000/docs
echo.
echo Appuyez sur Ctrl+C pour arreter
echo.

python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

pause
