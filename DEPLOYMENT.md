# Smart EMS Deployment Guide 🚀

This guide provides comprehensive instructions for deploying the Smart Energy Management System on various platforms.

## 📋 Prerequisites

### System Requirements
- **OS**: Windows 10/11, macOS 10.15+, or Linux (Ubuntu 20.04+)
- **RAM**: Minimum 4GB, Recommended 8GB+
- **Storage**: 2GB free space
- **Network**: Internet connection for API calls

### Required Software
- **Docker**: Version 20.10+ ([Download](https://www.docker.com/products/docker-desktop))
- **Docker Compose**: Version 2.0+ (included with Docker Desktop)
- **Git**: For cloning the repository ([Download](https://git-scm.com/downloads))

### API Keys Required
- **OpenWeather API**: [Get free key](https://openweathermap.org/api)
- **NREL API**: [Get free key](https://developer.nrel.gov/signup/)
- **ElectricityMaps API**: [Get free key](https://electricitymaps.com/api)
- **Gemini AI API**: [Get free key](https://makersuite.google.com/app/apikey)

## 🚀 Quick Deployment

### Option 1: One-Click Deployment (Recommended)

#### Windows
```powershell
# Clone repository
git clone https://github.com/prem926/smart-ems.git
cd smart-ems

# Run deployment script
.\deploy.ps1 deploy
```

#### Linux/macOS
```bash
# Clone repository
git clone https://github.com/prem926/smart-ems.git
cd smart-ems

# Make script executable and run
chmod +x deploy.sh
./deploy.sh deploy
```

### Option 2: Manual Docker Deployment

```bash
# 1. Clone repository
git clone https://github.com/prem926/smart-ems.git
cd smart-ems

# 2. Configure environment
cp config/env_template.txt .env
# Edit .env with your API keys

# 3. Build and run
docker build -t smart-ems .
docker run -d --name smart-ems-app -p 8501:8501 --env-file .env smart-ems

# 4. Access dashboard
# Open http://localhost:8501 in your browser
```

## 🐳 Docker Deployment Options

### Single Container Deployment
Perfect for development and testing:

```bash
# Build image
docker build -t smart-ems .

# Run container
docker run -d \
  --name smart-ems-app \
  -p 8501:8501 \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  --restart unless-stopped \
  smart-ems
```

### Full Stack Deployment
Includes monitoring and caching:

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

## ☁️ Cloud Deployment

### AWS EC2 Deployment

1. **Launch EC2 Instance**
   ```bash
   # Ubuntu 20.04 LTS, t3.medium (2 vCPU, 4GB RAM)
   # Security Group: Allow ports 22, 80, 443, 8501
   ```

2. **Install Dependencies**
   ```bash
   # Update system
   sudo apt update && sudo apt upgrade -y
   
   # Install Docker
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   sudo usermod -aG docker $USER
   
   # Install Docker Compose
   sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   ```

3. **Deploy Application**
   ```bash
   # Clone repository
   git clone https://github.com/prem926/smart-ems.git
   cd smart-ems
   
   # Configure environment
   cp config/env_template.txt .env
   nano .env  # Add your API keys
   
   # Deploy
   ./deploy.sh full
   ```

4. **Configure Nginx (Optional)**
   ```bash
   # Install Nginx
   sudo apt install nginx -y
   
   # Create configuration
   sudo nano /etc/nginx/sites-available/smart-ems
   ```
   
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://localhost:8501;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection 'upgrade';
           proxy_set_header Host $host;
           proxy_cache_bypass $http_upgrade;
       }
   }
   ```
   
   ```bash
   # Enable site
   sudo ln -s /etc/nginx/sites-available/smart-ems /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

### Google Cloud Platform (GCP)

1. **Create VM Instance**
   ```bash
   # Create instance
   gcloud compute instances create smart-ems-vm \
     --image-family=ubuntu-2004-lts \
     --image-project=ubuntu-os-cloud \
     --machine-type=e2-medium \
     --zone=us-central1-a \
     --tags=http-server,https-server
   ```

2. **Deploy Application**
   ```bash
   # SSH into instance
   gcloud compute ssh smart-ems-vm --zone=us-central1-a
   
   # Follow AWS deployment steps 2-3
   ```

### Azure Container Instances

1. **Create Resource Group**
   ```bash
   az group create --name smart-ems-rg --location eastus
   ```

2. **Deploy Container**
   ```bash
   az container create \
     --resource-group smart-ems-rg \
     --name smart-ems \
     --image yourusername/smart-ems:latest \
     --dns-name-label smart-ems \
     --ports 8501 \
     --environment-variables \
       OPENWEATHER_API_KEY=your_key \
       NREL_API_KEY=your_key \
       ELECTRICITYMAPS_API_KEY=your_key \
       GEMINI_API_KEY=your_key
   ```

## 🔧 Configuration

### Environment Variables

Create `.env` file from template:

```bash
cp config/env_template.txt .env
```

Key variables to configure:

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

# Location (Default: Delhi, India)
DEFAULT_LATITUDE=28.7041
DEFAULT_LONGITUDE=77.1025
DEFAULT_TIMEZONE=Asia/Kolkata

# Performance
MAX_WORKERS=4
CACHE_TTL=3600
REQUEST_TIMEOUT=30
```

### System Configuration

Edit `config/system_config.yaml`:

```yaml
system:
  name: "Smart Energy Management System"
  environment: "production"

# RL Environment
rl_environment:
  observation_space: 25
  action_space: 6
  reward_weights:
    economic: 0.30
    sustainability: 0.30
    reliability: 0.25
    health: 0.15

# IoT Devices
iot_devices:
  solar_panels: 15
  battery_systems: 5
  inverters: 8
  ev_chargers: 20
  grid_connections: 2
```

## 📊 Monitoring and Logs

### View Logs

```bash
# Container logs
docker logs smart-ems-app

# Follow logs in real-time
docker logs -f smart-ems-app

# Docker Compose logs
docker-compose logs -f
```

### Health Checks

```bash
# Check container status
docker ps

# Check service health
curl http://localhost:8501/_stcore/health

# Check system metrics
curl http://localhost:9090/metrics
```

### Monitoring Dashboards

- **Main Dashboard**: http://localhost:8501
- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090

## 🔄 Updates and Maintenance

### Update Application

```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose up -d --build
```

### Backup Data

```bash
# Backup data directory
tar -czf smart-ems-backup-$(date +%Y%m%d).tar.gz data/

# Backup logs
tar -czf smart-ems-logs-$(date +%Y%m%d).tar.gz logs/
```

### Scale Services

```bash
# Scale specific service
docker-compose up -d --scale smart-ems=3

# Update resource limits
docker-compose up -d --scale smart-ems=2 --scale redis=1
```

## 🛠️ Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Find process using port 8501
   lsof -i :8501
   
   # Kill process
   kill -9 <PID>
   ```

2. **Container Won't Start**
   ```bash
   # Check logs
   docker logs smart-ems-app
   
   # Check environment variables
   docker exec smart-ems-app env | grep API
   ```

3. **API Key Issues**
   ```bash
   # Verify API keys in .env file
   cat .env | grep API_KEY
   
   # Test API connectivity
   curl "https://api.openweathermap.org/data/2.5/weather?q=Delhi&appid=YOUR_API_KEY"
   ```

4. **Memory Issues**
   ```bash
   # Check memory usage
   docker stats smart-ems-app
   
   # Increase memory limits
   docker run -m 2g smart-ems
   ```

### Performance Optimization

1. **Enable Caching**
   ```bash
   # Start Redis
   docker run -d --name redis -p 6379:6379 redis:alpine
   
   # Update .env
   echo "REDIS_URL=redis://localhost:6379/0" >> .env
   ```

2. **Optimize Docker Image**
   ```bash
   # Multi-stage build
   docker build --target production -t smart-ems:prod .
   
   # Use specific Python version
   docker build --build-arg PYTHON_VERSION=3.9 -t smart-ems .
   ```

## 🔒 Security Considerations

### Production Security

1. **Use HTTPS**
   ```bash
   # Generate SSL certificates
   openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes
   ```

2. **Secure Environment Variables**
   ```bash
   # Use Docker secrets
   echo "your_api_key" | docker secret create api_key -
   
   # Use external secret management
   # AWS Secrets Manager, Azure Key Vault, etc.
   ```

3. **Network Security**
   ```bash
   # Create custom network
   docker network create smart-ems-network
   
   # Use internal networks
   docker run --network smart-ems-network smart-ems
   ```

## 📞 Support

### Getting Help

- **GitHub Issues**: [Report bugs and request features](https://github.com/prem926/smart-ems/issues)
- **Documentation**: [Complete documentation](https://github.com/prem926/smart-ems/wiki)
- **Discussions**: [Community discussions](https://github.com/prem926/smart-ems/discussions)

### Deployment Support

- **Docker Issues**: Check [Docker documentation](https://docs.docker.com/)
- **Cloud Deployment**: Refer to cloud provider documentation
- **API Issues**: Check API provider status pages

---

**Happy Deploying! 🚀**

*For more information, visit the [main README](README.md) or [complete documentation](smart_ems/README_COMPLETE.md).*
