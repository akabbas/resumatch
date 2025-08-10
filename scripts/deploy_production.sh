#!/bin/bash

# 🚀 ResuMatch Production Deployment Script
# This script builds and deploys the ResuMatch application

set -e  # Exit on any error

echo "🚀 Starting ResuMatch Production Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="resumatch"
VERSION=$(git describe --tags --always --dirty)
DOCKER_IMAGE="${APP_NAME}:${VERSION}"
COMPOSE_FILE="docker-compose.production.yml"

echo -e "${BLUE}📋 Deployment Configuration:${NC}"
echo -e "  App Name: ${APP_NAME}"
echo -e "  Version: ${VERSION}"
echo -e "  Docker Image: ${DOCKER_IMAGE}"
echo -e "  Compose File: ${COMPOSE_FILE}"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running. Please start Docker and try again.${NC}"
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "app.py" ] || [ ! -f "requirements.txt" ]; then
    echo -e "${RED}❌ Please run this script from the ResuMatch project root directory.${NC}"
    exit 1
fi

# Stop existing containers
echo -e "${YELLOW}🛑 Stopping existing containers...${NC}"
docker-compose -f ${COMPOSE_FILE} down --remove-orphans || true

# Clean up old images (optional)
echo -e "${YELLOW}🧹 Cleaning up old images...${NC}"
docker image prune -f || true

# Build the new Docker image
echo -e "${BLUE}🔨 Building Docker image...${NC}"
docker build -f Dockerfile.production -t ${DOCKER_IMAGE} .

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Docker image built successfully!${NC}"
else
    echo -e "${RED}❌ Docker build failed!${NC}"
    exit 1
fi

# Start the application
echo -e "${BLUE}🚀 Starting ResuMatch application...${NC}"
docker-compose -f ${COMPOSE_FILE} up -d

# Wait for the application to be ready
echo -e "${YELLOW}⏳ Waiting for application to be ready...${NC}"
sleep 10

# Check if the application is running
echo -e "${BLUE}🔍 Checking application status...${NC}"
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Application is running and healthy!${NC}"
else
    echo -e "${YELLOW}⚠️  Health check failed, but checking if app is responding...${NC}"
    if curl -f http://localhost:8000/ > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Application is running and responding!${NC}"
    else
        echo -e "${RED}❌ Application failed to start properly.${NC}"
        echo -e "${YELLOW}📋 Checking logs...${NC}"
        docker-compose -f ${COMPOSE_FILE} logs --tail=50
        exit 1
    fi
fi

# Show running containers
echo -e "${BLUE}📊 Current container status:${NC}"
docker-compose -f ${COMPOSE_FILE} ps

# Show application info
echo ""
echo -e "${GREEN}🎉 ResuMatch v2.0 Successfully Deployed!${NC}"
echo -e "${BLUE}🌐 Access your application at: http://localhost:8000${NC}"
echo -e "${BLUE}📝 API Documentation: http://localhost:8000/api/sample-data${NC}"
echo -e "${BLUE}🐳 Docker Image: ${DOCKER_IMAGE}${NC}"
echo -e "${BLUE}📋 View logs: docker-compose -f ${COMPOSE_FILE} logs -f${NC}"
echo ""

# Optional: Show recent commits
echo -e "${BLUE}📝 Recent commits:${NC}"
git log --oneline -5

echo ""
echo -e "${GREEN}🚀 Deployment complete! Your ResuMatch application is now running.${NC}"
