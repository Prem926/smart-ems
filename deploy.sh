#!/bin/bash

# Smart EMS Deployment Script
# This script automates the deployment process for the Smart Energy Management System

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="smart-ems"
DOCKER_IMAGE="smart-ems"
CONTAINER_NAME="smart-ems-app"
PORT=8501
ENV_FILE=".env"

# Functions
print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}  Smart EMS Deployment Script   ${NC}"
    echo -e "${BLUE}================================${NC}"
    echo
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

check_requirements() {
    print_info "Checking system requirements..."
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    print_success "Docker is installed"
    
    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    print_success "Docker Compose is installed"
    
    # Check if .env file exists
    if [ ! -f "$ENV_FILE" ]; then
        print_warning ".env file not found. Creating from template..."
        if [ -f "config/env_template.txt" ]; then
            cp config/env_template.txt .env
            print_success ".env file created from template"
            print_warning "Please edit .env file with your API keys before continuing"
        else
            print_error "Environment template not found. Please create .env file manually."
            exit 1
        fi
    else
        print_success ".env file found"
    fi
}

build_docker_image() {
    print_info "Building Docker image..."
    docker build -t $DOCKER_IMAGE:latest .
    print_success "Docker image built successfully"
}

deploy_single_container() {
    print_info "Deploying single container..."
    
    # Stop existing container if running
    if [ "$(docker ps -q -f name=$CONTAINER_NAME)" ]; then
        print_info "Stopping existing container..."
        docker stop $CONTAINER_NAME
    fi
    
    # Remove existing container if exists
    if [ "$(docker ps -aq -f name=$CONTAINER_NAME)" ]; then
        print_info "Removing existing container..."
        docker rm $CONTAINER_NAME
    fi
    
    # Create necessary directories
    mkdir -p data logs
    
    # Run new container
    docker run -d \
        --name $CONTAINER_NAME \
        -p $PORT:8501 \
        --env-file $ENV_FILE \
        -v "$(pwd)/data:/app/data" \
        -v "$(pwd)/logs:/app/logs" \
        --restart unless-stopped \
        $DOCKER_IMAGE:latest
    
    print_success "Container deployed successfully"
}

deploy_full_stack() {
    print_info "Deploying full stack with Docker Compose..."
    
    # Create necessary directories
    mkdir -p data logs monitoring/prometheus monitoring/grafana/dashboards monitoring/grafana/datasources
    
    # Start services
    docker-compose up -d
    
    print_success "Full stack deployed successfully"
}

check_deployment() {
    print_info "Checking deployment status..."
    
    # Wait for service to start
    sleep 10
    
    # Check if container is running
    if [ "$(docker ps -q -f name=$CONTAINER_NAME)" ]; then
        print_success "Container is running"
    else
        print_error "Container is not running"
        return 1
    fi
    
    # Check if service is responding
    if curl -f http://localhost:$PORT/_stcore/health &> /dev/null; then
        print_success "Service is responding on port $PORT"
    else
        print_warning "Service is not responding yet. It may take a few minutes to start."
    fi
}

show_status() {
    print_info "Deployment Status:"
    echo
    echo "Container Status:"
    docker ps -f name=$CONTAINER_NAME
    echo
    echo "Service URLs:"
    echo "  Main Dashboard: http://localhost:$PORT"
    echo "  Health Check: http://localhost:$PORT/_stcore/health"
    echo
    echo "Logs:"
    echo "  docker logs $CONTAINER_NAME"
    echo
    echo "Stop Service:"
    echo "  docker stop $CONTAINER_NAME"
    echo
    echo "Remove Service:"
    echo "  docker rm $CONTAINER_NAME"
}

cleanup() {
    print_info "Cleaning up..."
    
    # Stop and remove container
    if [ "$(docker ps -q -f name=$CONTAINER_NAME)" ]; then
        docker stop $CONTAINER_NAME
    fi
    
    if [ "$(docker ps -aq -f name=$CONTAINER_NAME)" ]; then
        docker rm $CONTAINER_NAME
    fi
    
    # Remove image
    if [ "$(docker images -q $DOCKER_IMAGE)" ]; then
        docker rmi $DOCKER_IMAGE:latest
    fi
    
    print_success "Cleanup completed"
}

show_help() {
    echo "Usage: $0 [OPTION]"
    echo
    echo "Options:"
    echo "  deploy          Deploy single container (default)"
    echo "  full            Deploy full stack with monitoring"
    echo "  status          Show deployment status"
    echo "  logs            Show container logs"
    echo "  stop            Stop the service"
    echo "  cleanup         Remove container and image"
    echo "  help            Show this help message"
    echo
    echo "Examples:"
    echo "  $0 deploy       # Deploy single container"
    echo "  $0 full         # Deploy with monitoring stack"
    echo "  $0 status       # Check deployment status"
    echo "  $0 logs         # View logs"
}

# Main script
main() {
    print_header
    
    case "${1:-deploy}" in
        "deploy")
            check_requirements
            build_docker_image
            deploy_single_container
            check_deployment
            show_status
            ;;
        "full")
            check_requirements
            build_docker_image
            deploy_full_stack
            check_deployment
            show_status
            ;;
        "status")
            show_status
            ;;
        "logs")
            docker logs $CONTAINER_NAME
            ;;
        "stop")
            print_info "Stopping service..."
            docker stop $CONTAINER_NAME
            print_success "Service stopped"
            ;;
        "cleanup")
            cleanup
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            print_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
