#!/usr/bin/env python3
"""
Smart EMS Complete System Launcher
VidyutAI Hackathon 2025 - Problem Statement 2

This script launches the complete Smart Energy Management System with all services.
"""

import os
import sys
import subprocess
import time
import yaml
import logging
from pathlib import Path
from typing import Dict, Any
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/system_launcher.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SmartEMSLauncher:
    """Main launcher class for Smart EMS system."""
    
    def __init__(self, config_path: str = "config/system_config.yaml"):
        """Initialize the launcher with configuration."""
        self.config_path = config_path
        self.config = self.load_config()
        self.processes = {}
        
    def load_config(self) -> Dict[str, Any]:
        """Load system configuration from YAML file."""
        try:
            with open(self.config_path, 'r') as file:
                config = yaml.safe_load(file)
            logger.info(f"Configuration loaded from {self.config_path}")
            return config
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            return {}
    
    def check_dependencies(self) -> bool:
        """Check if all required dependencies are installed."""
        logger.info("Checking dependencies...")
        
        required_packages = [
            'streamlit', 'plotly', 'pandas', 'numpy', 'torch', 
            'stable_baselines3', 'gymnasium', 'requests', 'yaml'
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            logger.error(f"Missing packages: {missing_packages}")
            logger.info("Please install missing packages using: pip install -r requirements.txt")
            return False
        
        logger.info("All dependencies are installed")
        return True
    
    def create_directories(self):
        """Create necessary directories."""
        logger.info("Creating directories...")
        
        directories = [
            'logs',
            'data',
            'models',
            'cache',
            'backups'
        ]
        
        for directory in directories:
            Path(directory).mkdir(exist_ok=True)
            logger.info(f"Created directory: {directory}")
    
    def check_environment(self) -> bool:
        """Check environment variables and configuration."""
        logger.info("Checking environment...")
        
        # Check if .env file exists
        env_file = Path('.env')
        if not env_file.exists():
            logger.warning(".env file not found. Using default configuration.")
            logger.info("Copy config/env_template.txt to .env and configure your API keys")
        
        # Check if data files exist
        data_files = [
            'Plant_1_Generation_Data.csv',
            'Plant_1_Weather_Sensor_Data.csv',
            'Plant_2_Generation_Data.csv',
            'Plant_2_Weather_Sensor_Data.csv'
        ]
        
        missing_data = []
        for file in data_files:
            if not Path(file).exists():
                missing_data.append(file)
        
        if missing_data:
            logger.warning(f"Missing data files: {missing_data}")
            logger.info("System will use synthetic data generation")
        
        return True
    
    def start_iot_service(self):
        """Start IoT data ingestion service."""
        logger.info("Starting IoT data ingestion service...")
        
        try:
            # Start IoT service as background process
            cmd = [sys.executable, "-c", """
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from services.iot_data_ingestion import IoTDataStream

async def main():
    config = {'streaming_interval': 5}
    iot_stream = IoTDataStream(config)
    print("IoT service started")
    async for data in iot_stream.start_streaming():
        print(f"Generated {len(data)} device readings")

if __name__ == "__main__":
    asyncio.run(main())
"""]
            
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.processes['iot_service'] = process
            logger.info("IoT service started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start IoT service: {e}")
    
    def start_diagnostics_service(self):
        """Start diagnostics engine service."""
        logger.info("Starting diagnostics engine...")
        
        try:
            # Start diagnostics service
            cmd = [sys.executable, "-c", """
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from services.diagnostics_engine import DiagnosticsEngine

config = {}
diagnostics = DiagnosticsEngine(config)
print("Diagnostics engine started")
"""]
            
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.processes['diagnostics'] = process
            logger.info("Diagnostics engine started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start diagnostics engine: {e}")
    
    def start_alert_service(self):
        """Start alert system service."""
        logger.info("Starting alert system...")
        
        try:
            # Start alert service
            cmd = [sys.executable, "-c", """
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from services.alert_system import AlertSystem

config = {}
alert_system = AlertSystem(config)
print("Alert system started")
"""]
            
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.processes['alert_system'] = process
            logger.info("Alert system started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start alert system: {e}")
    
    def start_dashboard(self):
        """Start Streamlit dashboard."""
        logger.info("Starting Streamlit dashboard...")
        
        try:
            # Start Streamlit dashboard
            cmd = [
                sys.executable, "-m", "streamlit", "run", 
                "dashboard/app_streamlit.py",
                "--server.port", "8501",
                "--server.address", "0.0.0.0",
                "--server.headless", "true"
            ]
            
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.processes['dashboard'] = process
            logger.info("Streamlit dashboard started successfully")
            logger.info("Dashboard available at: http://localhost:8501")
            
        except Exception as e:
            logger.error(f"Failed to start dashboard: {e}")
    
    def start_rl_training(self):
        """Start RL training service."""
        if not self.config.get('features', {}).get('enable_rl_training', True):
            logger.info("RL training disabled in configuration")
            return
        
        logger.info("Starting RL training service...")
        
        try:
            # Start RL training
            cmd = [sys.executable, "rl/train_rl.py"]
            
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.processes['rl_training'] = process
            logger.info("RL training started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start RL training: {e}")
    
    def start_all_services(self):
        """Start all system services."""
        logger.info("Starting Smart EMS system...")
        
        # Create directories
        self.create_directories()
        
        # Check environment
        if not self.check_environment():
            logger.error("Environment check failed")
            return False
        
        # Start services
        self.start_iot_service()
        time.sleep(2)
        
        self.start_diagnostics_service()
        time.sleep(2)
        
        self.start_alert_service()
        time.sleep(2)
        
        self.start_dashboard()
        time.sleep(2)
        
        self.start_rl_training()
        
        logger.info("All services started successfully")
        return True
    
    def stop_all_services(self):
        """Stop all running services."""
        logger.info("Stopping all services...")
        
        for name, process in self.processes.items():
            try:
                process.terminate()
                process.wait(timeout=10)
                logger.info(f"Stopped {name}")
            except subprocess.TimeoutExpired:
                process.kill()
                logger.warning(f"Force killed {name}")
            except Exception as e:
                logger.error(f"Error stopping {name}: {e}")
        
        self.processes.clear()
        logger.info("All services stopped")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get system status."""
        status = {
            'services': {},
            'uptime': time.time(),
            'config_loaded': bool(self.config)
        }
        
        for name, process in self.processes.items():
            status['services'][name] = {
                'running': process.poll() is None,
                'pid': process.pid if process.poll() is None else None
            }
        
        return status
    
    def run_health_check(self):
        """Run system health check."""
        logger.info("Running health check...")
        
        # Check if all services are running
        for name, process in self.processes.items():
            if process.poll() is not None:
                logger.error(f"Service {name} is not running")
                return False
        
        logger.info("Health check passed")
        return True

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Smart EMS System Launcher')
    parser.add_argument('--config', default='config/system_config.yaml', 
                       help='Configuration file path')
    parser.add_argument('--mode', choices=['start', 'stop', 'status', 'health'], 
                       default='start', help='Operation mode')
    parser.add_argument('--dashboard-only', action='store_true', 
                       help='Start only the dashboard')
    
    args = parser.parse_args()
    
    # Initialize launcher
    launcher = SmartEMSLauncher(args.config)
    
    if args.mode == 'start':
        if args.dashboard_only:
            logger.info("Starting dashboard only...")
            launcher.create_directories()
            launcher.start_dashboard()
        else:
            # Check dependencies first
            if not launcher.check_dependencies():
                sys.exit(1)
            
            # Start all services
            if not launcher.start_all_services():
                sys.exit(1)
        
        # Keep running
        try:
            logger.info("System is running. Press Ctrl+C to stop.")
            while True:
                time.sleep(10)
                if not launcher.run_health_check():
                    logger.error("Health check failed")
                    break
        except KeyboardInterrupt:
            logger.info("Shutdown requested by user")
        finally:
            launcher.stop_all_services()
    
    elif args.mode == 'stop':
        launcher.stop_all_services()
    
    elif args.mode == 'status':
        status = launcher.get_system_status()
        print(f"System Status: {status}")
    
    elif args.mode == 'health':
        if launcher.run_health_check():
            print("System is healthy")
            sys.exit(0)
        else:
            print("System health check failed")
            sys.exit(1)

if __name__ == "__main__":
    main()