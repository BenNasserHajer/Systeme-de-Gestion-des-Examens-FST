@echo off
echo ========================================
echo Viewing Changes in Modified Files
echo ========================================

cd /d "c:\Users\dongm\OneDrive\Desktop\projet"

echo.
echo ========================================
echo Backend Changes
echo ========================================
echo.
echo [1] server/app/routers/surveillances.py
echo ----------------------------------------
git diff server/app/routers/surveillances.py

echo.
echo.
echo [2] server/app/algorithms/surv_auto.py
echo ----------------------------------------
git diff server/app/algorithms/surv_auto.py

echo.
echo ========================================
echo Frontend Changes
echo ========================================
echo.
echo [3] frontend/src/app/(admin)/surveillance/charge/page.tsx
echo ----------------------------------------
git diff frontend/src/app/(admin)/surveillance/charge/page.tsx

echo.
echo.
echo [4] frontend/src/app/(admin)/surveillance/page.tsx
echo ----------------------------------------
git diff frontend/src/app/(admin)/surveillance/page.tsx

echo.
echo.
echo [5] frontend/src/hooks/useDisponibilite.ts
echo ----------------------------------------
git diff frontend/src/hooks/useDisponibilite.ts

echo.
echo ========================================
echo End of Changes
echo ========================================
pause
