# Smart EMS Deployment Script for Windows PowerShell
# This script automates the deployment process for the Smart Energy Management System

param(
    [Parameter(Position=0)]
    [ValidateSet("deploy", "full", "status", "logs", "stop", "cleanup", "help")]
    [string]$Action = "deploy"
)

# Configuration
$PROJECT_NAME = "smart-ems"
$DOCKER_IMAGE = "smart-ems"
$CONTAINER_NAME = "smart-ems-app"
$PORT = 8501
$ENV_FILE = ".env"

# Functions
function Write-Header {
    Write-Host "=================================" -ForegroundColor Blue
    Write-Host "  Smart EMS Deployment Script   " -ForegroundColor Blue
    Write-Host "=================================" -ForegroundColor Blue
    Write-Host ""
}

function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠️  $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

function Write-Info {
    param([string]$Message)
    Write-Host "ℹ️  $Message" -ForegroundColor Blue
}

function Test-Requirements {
    Write-Info "Checking system requirements..."
    
    # Check if Docker is installed
    try {
        $null = docker --version
        Write-Success "Docker is installed"
    }
    catch {
        Write-Error "Docker is not installed. Please install Docker Desktop first."
        exit 1
    }
    
    # Check if Docker Compose is installed
    try {
        $null = docker-compose --version
        Write-Success "Docker Compose is installed"
    }
    catch {
        Write-Error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    }
    
    # Check if .env file exists
    if (-not (Test-Path $ENV_FILE)) {
        Write-Warning ".env file not found. Creating from template..."
        if (Test-Path "config/env_template.txt") {
            Copy-Item "config/env_template.txt" $ENV_FILE
            Write-Success ".env file created from template"
            Write-Warning "Please edit .env file with your API keys before continuing"
        }
        else {
            Write-Error "Environment template not found. Please create .env file manually."
            exit 1
        }
    }
    else {
        Write-Success ".env file found"
    }
}

function Build-DockerImage {
    Write-Info "Building Docker image..."
    docker build -t "${DOCKER_IMAGE}:latest" .
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Docker image built successfully"
    }
    else {
        Write-Error "Failed to build Docker image"
        exit 1
    }
}

function Deploy-SingleContainer {
    Write-Info "Deploying single container..."
    
    # Stop existing container if running
    $existingContainer = docker ps -q -f "name=$CONTAINER_NAME"
    if ($existingContainer) {
        Write-Info "Stopping existing container..."
        docker stop $CONTAINER_NAME
    }
    
    # Remove existing container if exists
    $existingContainer = docker ps -aq -f "name=$CONTAINER_NAME"
    if ($existingContainer) {
        Write-Info "Removing existing container..."
        docker rm $CONTAINER_NAME
    }
    
    # Create necessary directories
    if (-not (Test-Path "data")) { New-Item -ItemType Directory -Path "data" }
    if (-not (Test-Path "logs")) { New-Item -ItemType Directory -Path "logs" }
    
    # Run new container
    docker run -d `
        --name $CONTAINER_NAME `
        -p "${PORT}:8501" `
        --env-file $ENV_FILE `
        -v "${PWD}/data:/app/data" `
        -v "${PWD}/logs:/app/logs" `
        --restart unless-stopped `
        "${DOCKER_IMAGE}:latest"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Container deployed successfully"
    }
    else {
        Write-Error "Failed to deploy container"
        exit 1
    }
}

function Deploy-FullStack {
    Write-Info "Deploying full stack with Docker Compose..."
    
    # Create necessary directories
    $directories = @("data", "logs", "monitoring/prometheus", "monitoring/grafana/dashboards", "monitoring/grafana/datasources")
    foreach ($dir in $directories) {
        if (-not (Test-Path $dir)) { 
            New-Item -ItemType Directory -Path $dir -Force 
        }
    }
    
    # Start services
    docker-compose up -d
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Full stack deployed successfully"
    }
    else {
        Write-Error "Failed to deploy full stack"
        exit 1
    }
}

function Test-Deployment {
    Write-Info "Checking deployment status..."
    
    # Wait for service to start
    Start-Sleep -Seconds 10
    
    # Check if container is running
    $runningContainer = docker ps -q -f "name=$CONTAINER_NAME"
    if ($runningContainer) {
        Write-Success "Container is running"
    }
    else {
        Write-Error "Container is not running"
        return $false
    }
    
    # Check if service is responding
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:$PORT/_stcore/health" -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-Success "Service is responding on port $PORT"
        }
    }
    catch {
        Write-Warning "Service is not responding yet. It may take a few minutes to start."
    }
    
    return $true
}

function Show-Status {
    Write-Info "Deployment Status:"
    Write-Host ""
    Write-Host "Container Status:"
    docker ps -f "name=$CONTAINER_NAME"
    Write-Host ""
    Write-Host "Service URLs:"
    Write-Host "  Main Dashboard: http://localhost:$PORT" -ForegroundColor Cyan
    Write-Host "  Health Check: http://localhost:$PORT/_stcore/health" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Commands:"
    Write-Host "  View Logs: docker logs $CONTAINER_NAME" -ForegroundColor Cyan
    Write-Host "  Stop Service: docker stop $CONTAINER_NAME" -ForegroundColor Cyan
    Write-Host "  Remove Service: docker rm $CONTAINER_NAME" -ForegroundColor Cyan
    Write-Host ""
}

function Show-Logs {
    Write-Info "Showing container logs..."
    docker logs $CONTAINER_NAME
}

function Stop-Service {
    Write-Info "Stopping service..."
    docker stop $CONTAINER_NAME
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Service stopped"
    }
    else {
        Write-Error "Failed to stop service"
    }
}

function Remove-Service {
    Write-Info "Cleaning up..."
    
    # Stop and remove container
    $runningContainer = docker ps -q -f "name=$CONTAINER_NAME"
    if ($runningContainer) {
        docker stop $CONTAINER_NAME
    }
    
    $existingContainer = docker ps -aq -f "name=$CONTAINER_NAME"
    if ($existingContainer) {
        docker rm $CONTAINER_NAME
    }
    
    # Remove image
    $existingImage = docker images -q $DOCKER_IMAGE
    if ($existingImage) {
        docker rmi "${DOCKER_IMAGE}:latest"
    }
    
    Write-Success "Cleanup completed"
}

function Show-Help {
    Write-Host "Usage: .\deploy.ps1 [ACTION]"
    Write-Host ""
    Write-Host "Actions:"
    Write-Host "  deploy          Deploy single container (default)"
    Write-Host "  full            Deploy full stack with monitoring"
    Write-Host "  status          Show deployment status"
    Write-Host "  logs            Show container logs"
    Write-Host "  stop            Stop the service"
    Write-Host "  cleanup         Remove container and image"
    Write-Host "  help            Show this help message"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\deploy.ps1 deploy       # Deploy single container"
    Write-Host "  .\deploy.ps1 full         # Deploy with monitoring stack"
    Write-Host "  .\deploy.ps1 status       # Check deployment status"
    Write-Host "  .\deploy.ps1 logs         # View logs"
}

# Main script
function Main {
    Write-Header
    
    switch ($Action) {
        "deploy" {
            Test-Requirements
            Build-DockerImage
            Deploy-SingleContainer
            Test-Deployment
            Show-Status
        }
        "full" {
            Test-Requirements
            Build-DockerImage
            Deploy-FullStack
            Test-Deployment
            Show-Status
        }
        "status" {
            Show-Status
        }
        "logs" {
            Show-Logs
        }
        "stop" {
            Stop-Service
        }
        "cleanup" {
            Remove-Service
        }
        "help" {
            Show-Help
        }
        default {
            Write-Error "Unknown action: $Action"
            Show-Help
            exit 1
        }
    }
}

# Run main function
Main
