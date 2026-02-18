@echo off
echo ============================================================
echo   Operational Fragility Modeling Framework
echo   CS4982 - Winter 2026
echo ============================================================
echo.

cd /d C:\Users\malek\Projects\cs4982-fragility

echo Activating virtual environment...
call venv\Scripts\activate

echo.
echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Running diagnostics...
python run_diagnostics.py

echo.
echo Running simulation pipeline...
python run_pipeline.py

echo.
echo Launching dashboard...
streamlit run dashboard.py

pause