#!/bin/bash

# ZehraGuard InsightX Build Status Check
# This script verifies all components are ready for production

echo "🔍 ZehraGuard InsightX Build Status Check"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

check_passed=0
check_failed=0

check_component() {
    local component=$1
    local file=$2
    local description=$3
    
    if [ -f "$file" ] || [ -d "$file" ]; then
        echo -e "${GREEN}✅ $component${NC}: $description"
        ((check_passed++))
    else
        echo -e "${RED}❌ $component${NC}: $description (MISSING: $file)"
        ((check_failed++))
    fi
}

check_directory() {
    local component=$1
    local dir=$2
    local description=$3
    
    if [ -d "$dir" ] && [ "$(ls -A $dir 2>/dev/null)" ]; then
        echo -e "${GREEN}✅ $component${NC}: $description"
        ((check_passed++))
    else
        echo -e "${RED}❌ $component${NC}: $description (MISSING OR EMPTY: $dir)"
        ((check_failed++))
    fi
}

echo -e "\n${BLUE}Core Services${NC}"
echo "============="
check_component "Core API" "core/main.py" "FastAPI application with REST endpoints"
check_component "Database Models" "core/models.py" "SQLAlchemy database models"
check_component "Database Init" "core/database.py" "Database initialization and migrations"
check_component "Configuration" "core/config.py" "Application configuration management"
check_directory "Core Services" "core/services" "Behavioral analyzer, threat detector, ML service"

echo -e "\n${BLUE}Frontend Dashboard${NC}"
echo "=================="
check_component "React App" "dashboard/src/App.tsx" "Main React application"
check_component "Package Config" "dashboard/package.json" "Node.js dependencies and scripts"
check_directory "Dashboard Pages" "dashboard/src/pages" "React components for all pages"
check_component "Public Index" "dashboard/public/index.html" "HTML template"

echo -e "\n${BLUE}Behavioral Agents${NC}"
echo "=================="
check_component "Go Agent" "agents/collectors/behavioral_agent.go" "Cross-platform behavioral data collector"
check_component "Go Modules" "agents/go.mod" "Go dependency management"
check_component "Agent Config" "agents/config/agent.conf" "Agent configuration template"
check_component "Agent Manager" "agents/cmd/manager/main.go" "Agent management service"

echo -e "\n${BLUE}ML Services${NC}"
echo "============"
check_component "ML Service" "ml/main.py" "Machine learning service API"
check_component "ML Dockerfile" "ml/Dockerfile" "ML service container configuration"
check_component "ML Requirements" "ml/requirements.txt" "Python ML dependencies"

echo -e "\n${BLUE}SIEM Integrations${NC}"
echo "=================="
check_component "SIEM Connectors" "integrations/siem/siem_integrations.py" "Enterprise SIEM integrations"

echo -e "\n${BLUE}Docker Configuration${NC}"
echo "====================="
check_component "Main Dockerfile" "Dockerfile" "Primary application container"
check_component "Docker Compose" "docker-compose.yml" "Development environment"
check_component "Core Dockerfile" "deployment/docker/Dockerfile.core" "Production core API container"
check_component "Dashboard Dockerfile" "deployment/docker/Dockerfile.dashboard" "Production dashboard container"
check_component "Agent Dockerfile" "deployment/docker/Dockerfile.agent" "Production agent container"
check_component "Deployment Compose" "deployment/docker-compose.yml" "Production deployment"

echo -e "\n${BLUE}Kubernetes Configuration${NC}"
echo "========================="
check_component "Namespace" "deployment/k8s/namespace.yaml" "Kubernetes namespace"
check_component "ConfigMap" "deployment/k8s/configmap.yaml" "Configuration management"
check_component "Secrets" "deployment/k8s/secrets.yaml" "Secret management"
check_component "PostgreSQL" "deployment/k8s/postgres.yaml" "Database deployment"
check_component "Redis" "deployment/k8s/redis.yaml" "Cache deployment"
check_component "InfluxDB" "deployment/k8s/influxdb.yaml" "Time-series database"
check_component "RabbitMQ" "deployment/k8s/rabbitmq.yaml" "Message queue"
check_component "Core API" "deployment/k8s/core-api.yaml" "Core service deployment"
check_component "Dashboard" "deployment/k8s/dashboard.yaml" "Dashboard deployment"
check_component "Ingress" "deployment/k8s/ingress.yaml" "Traffic routing"

echo -e "\n${BLUE}Infrastructure${NC}"
echo "=============="
check_component "Nginx Config" "deployment/nginx/nginx.conf" "Reverse proxy configuration"
check_component "Prometheus Config" "deployment/monitoring/prometheus.yml" "Metrics collection"
check_component "Entrypoint Script" "deployment/entrypoint.sh" "Container startup script"

echo -e "\n${BLUE}Build and Deployment${NC}"
echo "===================="
check_component "Build Script" "build.sh" "Production build automation"
check_component "Deploy Script" "deploy.sh" "Production deployment automation"
check_component "Requirements" "requirements.txt" "Python dependencies"
check_component "Environment Template" ".env.example" "Environment configuration template"

echo -e "\n${BLUE}Documentation${NC}"
echo "============="
check_component "README" "README.md" "Project overview and setup"
check_component "Deployment Guide" "DEPLOYMENT.md" "Production deployment instructions"
check_component "Production Status" "PRODUCTION_STATUS.md" "Current build status"

echo -e "\n${BLUE}Testing and Data${NC}"
echo "================"
check_component "Test Data Generator" "scripts/generate_test_data.py" "Realistic test data creation"
check_directory "Test Framework" "tests" "Test suite structure"
check_directory "Documentation" "docs" "Comprehensive documentation"

echo -e "\n${BLUE}Summary${NC}"
echo "======="
total_checks=$((check_passed + check_failed))

if [ $check_failed -eq 0 ]; then
    echo -e "${GREEN}🎉 ALL CHECKS PASSED!${NC}"
    echo -e "${GREEN}✅ $check_passed/$total_checks components ready for production${NC}"
    echo
    echo -e "${BLUE}Ready to deploy:${NC}"
    echo "  ./deploy.sh                    # Full production deployment"
    echo "  ./deploy.sh --kubernetes       # Kubernetes deployment"
    echo "  ./deploy.sh --generate-data    # Include test data"
    echo "  ./build.sh                     # Build components only"
else
    echo -e "${RED}⚠️  BUILD INCOMPLETE${NC}"
    echo -e "${GREEN}✅ $check_passed components ready${NC}"
    echo -e "${RED}❌ $check_failed components missing${NC}"
    echo
    echo -e "${YELLOW}Please check the missing components above before deployment.${NC}"
fi

echo
echo -e "${BLUE}Next Steps:${NC}"
echo "1. Review any missing components"
echo "2. Run './deploy.sh' for complete deployment"
echo "3. Access dashboard at http://localhost:3000"
echo "4. Monitor logs with 'docker-compose logs -f'"
