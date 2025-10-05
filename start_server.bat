@echo off
echo Starting Smart EMS Dashboard Server...
cd "smart_ems"
python -m streamlit run dashboard/simple_advanced_dashboard.py --server.port 8501
pause

