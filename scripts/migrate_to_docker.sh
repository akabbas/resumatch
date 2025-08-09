#!/bin/bash

echo "🚀 Migrating Working Local Version to Docker"
echo "=============================================="

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose -f docker-compose.production.yml down 2>/dev/null || true
docker-compose -f docker-compose.working.yml down 2>/dev/null || true

# Build the new working version
echo "🔨 Building working Docker image..."
docker-compose -f docker-compose.working.yml build

# Start the working version
echo "🚀 Starting working version..."
docker-compose -f docker-compose.working.yml up -d

# Wait for the service to be ready
echo "⏳ Waiting for service to be ready..."
sleep 10

# Test the service
echo "🧪 Testing the service..."
curl -f http://localhost:8001/ > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "✅ Migration successful!"
    echo "🌐 Access your app at: http://localhost:8001"
    echo "📊 Container status:"
    docker-compose -f docker-compose.working.yml ps
else
    echo "❌ Migration failed. Checking logs..."
    docker-compose -f docker-compose.working.yml logs
fi

echo ""
echo "📋 Migration Summary:"
echo "  ✅ Working local version → Docker"
echo "  ✅ Enhanced AI features included"
echo "  ✅ Free Mode with ChatGPT-like intelligence"
echo "  ✅ Port 8001 (same as local)"
echo "  ✅ 4GB memory limit (vs 2GB before)"
echo "  ✅ Better error handling"
