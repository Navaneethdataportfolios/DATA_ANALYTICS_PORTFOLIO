@echo off
echo Starting Retail Analytics Streamlit Dashboard...
cd /d "%~dp0"
python -m streamlit run app.py
pause

