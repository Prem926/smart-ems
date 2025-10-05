# Smart Energy Management System (EMS) 🏭⚡

[![CI/CD Pipeline](https://github.com/prem926/smart-ems/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/prem926/smart-ems/actions/workflows/ci-cd.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28.0-red.svg)](https://streamlit.io/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://www.docker.com/)

A comprehensive Smart Energy Management System with AI-powered optimization, real-time monitoring, and intelligent diagnostics. Built for VidyutAI Hackathon 2025 - Problem Statement 2.

## 🌟 Features

### Core Features (Mandatory) ✅
- **IoT Data Ingestion**: 50 devices (solar, battery, EV chargers, inverters, grid)
- **Intelligent Diagnostics**: Clear messages with root cause analysis
- **Alert System**: Severity levels with recommended actions
- **RL Environment**: 25-state, 6-action with multi-objective reward
- **Streamlit Dashboard**: 12 comprehensive pages

### Advanced Features (Winning) 🏆
- **Location Intelligence**: State-wise personalization with India energy map
- **Clear Diagnostics**: Actionable messages (NOT just "anomaly detected")
- **Multi-objective RL**: Economic + Sustainability + Reliability + Health
- **Real-time Monitoring**: Live metrics and power flow visualization
- **AI Assistant**: Gemini AI chatbot for system explanations

## 🚀 Quick Start

### Option 1: GitHub Deployment (Recommended)

1. **Fork this repository**
   ```bash
   # Click the "Fork" button on GitHub, then clone your fork
   git clone https://github.com/prem926/smart-ems.git
   cd smart-ems
   ```

2. **Deploy with Docker (Easiest)**
   ```bash
   # Copy environment template
   cp config/env_template.txt .env
   
   # Edit .env with your API keys
   nano .env
   
   # Start with Docker Compose
   docker-compose up -d
   
   # Access dashboard at http://localhost:8501
   ```

3. **Deploy with Python**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Configure environment
   cp config/env_template.txt .env
   # Edit .env with your API keys
   
   # Run the system
   python run_complete_system.py
   ```

## 🐳 Docker Deployment

### Single Container
```bash
# Build image
docker build -t smart-ems .

# Run container
docker run -d \
  --name smart-ems \
  -p 8501:8501 \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  smart-ems
```

### Multi-Container (Full Stack)
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

**Services included:**
- Smart EMS App (Port 8501)
- Redis Cache (Port 6379)
- Prometheus Monitoring (Port 9090)
- Grafana Dashboards (Port 3000)

## 📊 Dashboard Access

Once deployed, access the dashboard at:
- **Main Dashboard**: http://localhost:8501
- **Grafana Monitoring**: http://localhost:3000 (admin/admin)
- **Prometheus Metrics**: http://localhost:9090

## 🔧 Configuration

### Environment Variables

Copy `config/env_template.txt` to `.env` and configure:

```bash
# Required API Keys
OPENWEATHER_API_KEY=your_openweather_key
NREL_API_KEY=your_nrel_key
ELECTRICITYMAPS_API_KEY=your_electricitymaps_key
GEMINI_API_KEY=your_gemini_key

# System Configuration
SYSTEM_ENV=production
DEBUG=false
PORT=8501

# Location (Default: Delhi)
DEFAULT_LATITUDE=28.7041
DEFAULT_LONGITUDE=77.1025
```

## 🏗️ Architecture

```
smart_ems/
├── services/                 # Core services
│   ├── iot_data_ingestion.py      # 50 IoT devices simulation
│   ├── diagnostics_engine.py      # Clear diagnostic messages
│   ├── alert_system.py            # Severity-based alerting
│   ├── location_intelligence.py   # India state-wise data
│   └── realtime_api_service.py    # API integrations
├── envs/                    # RL environments
│   └── advanced_ems_env.py        # 25-state, 6-action RL env
├── dashboard/               # Streamlit dashboard
│   ├── app_streamlit.py           # Main dashboard app
│   └── pages/                     # 12 dashboard pages
├── config/                  # Configuration
│   ├── system_config.yaml        # System parameters
│   └── env_template.txt          # Environment variables
├── utils/                   # Utilities
│   ├── data_processor.py         # Data processing
│   └── config.py                 # Configuration loader
└── run_complete_system.py   # System launcher
```

## 📈 Dashboard Pages

1. **🏠 Home**: KPIs, health indicators, energy flow
2. **📊 Real-Time Monitoring**: Live metrics, power flow, device status
3. **🔍 Diagnostics**: Health cards, clear messages, trends
4. **🚨 Alerts & Advisory**: Alert management, recommendations
5. **🤖 RL Scheduler**: RL decisions, SHAP explanations
6. **🗺️ India Energy Map**: State-wise energy visualization
7. **💬 AI Assistant**: Gemini AI chatbot

## 🔌 API Integrations

- **OpenWeather**: Real-time weather data
- **NREL**: Solar irradiance and renewable energy data
- **ElectricityMaps**: Carbon intensity and grid data
- **Gemini AI**: Natural language processing
- **data.gov.in**: Indian energy statistics

## 🏆 Hackathon Submission

**VidyutAI Hackathon 2025 - Problem Statement 2**

### Requirements Met ✅
- ✅ Real-time IoT data ingestion (50 devices)
- ✅ Clear diagnostic messages with root cause analysis
- ✅ Health indices (0-100%) for all components
- ✅ Real-time alerts with recommended actions
- ✅ RL-based scheduling (25-state, 6-action)
- ✅ Cloud dashboard (12 pages)
- ✅ Location-based personalization
- ✅ India energy map
- ✅ AI chatbot for explanations

### Winning Features ✅
- ✅ Clear diagnostics (NOT "anomaly detected")
- ✅ Actionable alerts with impact assessment
- ✅ Multi-objective RL optimization
- ✅ Explainable AI (SHAP explanations)
- ✅ Real-time monitoring with 50 IoT devices
- ✅ India-specific energy intelligence
- ✅ Professional UI with 12 dashboard pages

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/prem926/smart-ems/issues)
- **Discussions**: [GitHub Discussions](https://github.com/prem926/smart-ems/discussions)

---

**Built for VidyutAI Hackathon 2025 - Problem Statement 2** 🏆

*Empowering India's clean energy future with AI-driven smart grid management*
