#!/bin/bash
# Post-start script for development container
set -e

echo "🔄 Starting development services..."

# Wait for database services to be ready
echo "⏳ Waiting for database services..."

# Function to wait for service
wait_for_service() {
    local host=$1
    local port=$2
    local service_name=$3
    local max_attempts=30
    local attempt=1

    echo "Waiting for $service_name at $host:$port..."

    while [ $attempt -le $max_attempts ]; do
        if nc -z $host $port 2>/dev/null; then
            echo "✅ $service_name is ready!"
            return 0
        fi

        echo "⏳ Attempt $attempt/$max_attempts: $service_name not ready yet..."
        sleep 2
        attempt=$((attempt + 1))
    done

    echo "⚠️  Warning: $service_name not available after $max_attempts attempts"
    return 1
}

# Wait for database services
wait_for_service postgres-dev 5432 "PostgreSQL"
wait_for_service mysql-dev 3306 "MySQL"
wait_for_service redis-dev 6379 "Redis"
wait_for_service mongodb-dev 27017 "MongoDB"
wait_for_service elasticsearch-dev 9200 "Elasticsearch"

# Create database connections test
echo "🔍 Testing database connections..."

# Test PostgreSQL
if pg_isready -h postgres-dev -p 5432 -U postgres >/dev/null 2>&1; then
    echo "✅ PostgreSQL connection test passed"
else
    echo "⚠️  PostgreSQL connection test failed"
fi

# Test MySQL
if mysqladmin ping -h mysql-dev -P 3306 -u root -proot >/dev/null 2>&1; then
    echo "✅ MySQL connection test passed"
else
    echo "⚠️  MySQL connection test failed"
fi

# Test Redis
if redis-cli -h redis-dev -p 6379 ping >/dev/null 2>&1; then
    echo "✅ Redis connection test passed"
else
    echo "⚠️  Redis connection test failed"
fi

# Test MongoDB
if mongosh --host mongodb-dev:27017 --eval "db.runCommand('ping')" >/dev/null 2>&1; then
    echo "✅ MongoDB connection test passed"
else
    echo "⚠️  MongoDB connection test failed"
fi

# Test Elasticsearch
if curl -s http://elasticsearch-dev:9200/_cluster/health >/dev/null 2>&1; then
    echo "✅ Elasticsearch connection test passed"
else
    echo "⚠️  Elasticsearch connection test failed"
fi

# Update package lists and install any missing packages
echo "📦 Updating development tools..."

# Update Python packages
if command -v pip3 >/dev/null 2>&1; then
    pip3 install --upgrade pip >/dev/null 2>&1 || true
fi

# Update Node.js packages if package.json exists
if [ -f /workspace/package.json ]; then
    cd /workspace && npm update >/dev/null 2>&1 || true
fi

# Update Go modules if go.mod exists
if [ -f /workspace/go.mod ]; then
    cd /workspace && go mod tidy >/dev/null 2>&1 || true
fi

# Display service URLs
echo ""
echo "🌐 Available services:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Database Admin Interfaces:"
echo "   • pgAdmin (PostgreSQL):     http://localhost:8081"
echo "   • phpMyAdmin (MySQL):       http://localhost:8082"
echo "   • Redis Commander:          http://localhost:8083"
echo "   • Mongo Express:            http://localhost:8084"
echo ""
echo "🗄️  Object Storage:"
echo "   • MinIO Console:            http://localhost:9001"
echo ""
echo "📨 Message Queue & Email:"
echo "   • RabbitMQ Management:      http://localhost:15672"
echo "   • Mailhog (Email Testing):  http://localhost:8025"
echo ""
echo "🔍 Search & Analytics:"
echo "   • Elasticsearch:            http://localhost:9200"
echo "   • Kibana:                   http://localhost:5601"
echo ""
echo "🌐 Development Servers:"
echo "   • Frontend Dev Server:      http://localhost:3000"
echo "   • Backend API:              http://localhost:5000"
echo "   • Alternative Backend:      http://localhost:8080"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🚀 Development environment is ready!"
echo "💡 Tip: Use 'docker-compose logs <service>' to view service logs"
echo "💡 Tip: Use 'docker-compose restart <service>' to restart a service"
echo ""
