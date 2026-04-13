@echo off
setlocal

echo ============================================================
echo   Operational Fragility Modeling Framework
echo   CS4982 - Winter 2026
echo ============================================================
echo.

REM Go to script directory (project root)
cd /d "%~dp0"

REM Create venv if missing
if not exist "venv\Scripts\activate.bat" (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate.bat
echo.

echo Installing dependencies...
pip install -r requirements.txt
echo.

:menu
echo ============================================================
echo   MENU
echo ============================================================
echo   1. Comparative analysis (sparse/medium/dense/original)
echo   2. Single benchmark pipeline
echo   3. Diagnostics / convergence test
echo   4. Kaggle operational analysis
echo   5. Launch dashboard
echo   6. Exit
echo ============================================================
set /p choice="Choose (1-6): "

if "%choice%"=="1" goto compare
if "%choice%"=="2" goto pipeline
if "%choice%"=="3" goto diag
if "%choice%"=="4" goto kaggle
if "%choice%"=="5" goto dash
if "%choice%"=="6" goto end

echo Invalid choice.
echo.
goto menu

:compare
python scripts\compare_networks.py
pause
goto menu

:pipeline
python scripts\run_pipeline.py
pause
goto menu

:diag
python scripts\run_diagnostics.py
pause
goto menu

:kaggle
python scripts\run_kaggle_analysis.py
pause
goto menu

:dash
streamlit run src\dashboard.py
goto menu

:end
echo Goodbye.
endlocal
exit /b