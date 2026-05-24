@echo off
echo ========================================
echo Committing Bug Fixes
echo ========================================

cd /d "c:\Users\dongm\OneDrive\Desktop\projet"

echo.
echo Adding modified files...
git add server/app/routers/surveillances.py
git add server/app/algorithms/surv_auto.py
git add frontend/src/app/(admin)/surveillance/charge/page.tsx
git add frontend/src/app/(admin)/surveillance/page.tsx
git add frontend/src/hooks/useDisponibilite.ts

echo.
echo Committing changes...
git commit -m "fix: Correction bugs surveillance affectation

- Fix Salle.id -> Salle.code (2 locations in surveillances.py)
- Fix conditional filters in surv_auto.py algorithm
- Fix frontend imports and types
- Resolves AMPHI-INFO integer conversion error"

echo.
echo ========================================
echo Commit completed!
echo ========================================
echo.
echo To push to remote:
echo   git push origin Farah
echo.
pause
