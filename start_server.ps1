Write-Host "🚀 Starting Smart EMS Dashboard Server..." -ForegroundColor Green
Set-Location "smart_ems"
Write-Host "📊 Launching dashboard on http://localhost:8501" -ForegroundColor Yellow
python -m streamlit run dashboard/simple_advanced_dashboard.py --server.port 8501

