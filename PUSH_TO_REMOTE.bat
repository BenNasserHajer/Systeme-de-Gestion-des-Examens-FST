@echo off
echo ========================================
echo PUSH vers origin/Farah
echo ========================================
echo.

cd /d "c:\Users\dongm\OneDrive\Desktop\projet"

echo Vérification de l'état Git...
echo.
git status
echo.

echo ========================================
echo Commits à pusher:
echo ========================================
git log origin/Farah..HEAD --oneline
echo.

echo ========================================
echo ATTENTION
echo ========================================
echo.
echo Vous êtes sur le point de pusher 4 commits vers origin/Farah:
echo.
echo   1. Merge branch origin/hajer2
echo   2. Corrections surveillance
echo   3. Fix bugs critiques
echo   4. Mise à jour requirements.txt
echo.
echo Ces commits incluent:
echo   - Nouvelles fonctionnalités Auth JWT
echo   - Nouvelles fonctionnalités Indisponibilités
echo   - Corrections bugs Salle.id
echo   - Corrections filtres conditionnels
echo.

set /p confirm="Voulez-vous continuer? (O/N): "

if /i "%confirm%" NEQ "O" (
    echo.
    echo ❌ Push annulé
    pause
    exit /b 0
)

echo.
echo ========================================
echo Push en cours...
echo ========================================
echo.

git push origin Farah

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo ✅ PUSH RÉUSSI
    echo ========================================
    echo.
    echo Les commits ont été pushés vers origin/Farah
    echo.
    echo Vérifiez sur GitHub/GitLab:
    echo   - Les commits sont visibles
    echo   - Les fichiers sont à jour
    echo   - Pas de conflits
    echo.
) else (
    echo.
    echo ========================================
    echo ❌ ERREUR LORS DU PUSH
    echo ========================================
    echo.
    echo Causes possibles:
    echo   - Pas de connexion internet
    echo   - Conflits avec le remote
    echo   - Permissions insuffisantes
    echo.
    echo Solution:
    echo   1. Vérifier la connexion
    echo   2. git pull origin Farah
    echo   3. Résoudre les conflits
    echo   4. Réessayer le push
    echo.
)

pause
