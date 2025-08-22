#!/bin/bash

echo "🐳 Starting ResuMatch with Docker"
echo "=================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop first."
    exit 1
fi

echo "✅ Docker is running"
echo "🔧 Building and starting ResuMatch container..."

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose -f docker-compose.new.yml down 2>/dev/null || true

# Build and start the container
echo "🔨 Building ResuMatch container..."
docker-compose -f docker-compose.new.yml up --build -d

# Wait for the service to be ready
echo "⏳ Waiting for service to be ready..."
sleep 20

# Test the service
echo "🧪 Testing the service..."
if curl -f http://localhost:8000/ > /dev/null 2>&1; then
    echo "✅ ResuMatch is running successfully in Docker!"
    echo "🌐 Access your app at: http://localhost:8000"
    echo ""
    echo "📊 Container status:"
    docker-compose -f docker-compose.new.yml ps
    echo ""
    echo "📝 Logs:"
    docker-compose -f docker-compose.new.yml logs --tail=10
else
    echo "❌ Service failed to start. Checking logs..."
    docker-compose -f docker-compose.new.yml logs
    exit 1
fi

echo ""
echo "🎉 ResuMatch Docker deployment complete!"
echo "💡 Features:"
echo "   - FREE local AI resume generation"
echo "   - Web interface accessible at http://localhost:8000"
echo "   - Professional PDF output"
echo "   - ATS optimization"
echo ""
echo "🔧 To stop: docker-compose -f docker-compose.new.yml down"
echo "🔍 To view logs: docker-compose -f docker-compose.new.yml logs -f"
echo "🔄 To restart: ./start_docker.sh"
