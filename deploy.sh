#!/bin/bash

# ZehraGuard InsightX Production Deployment Script
# This script builds and deploys the complete system

set -e

echo "🚀 ZehraGuard InsightX Production Deployment"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is required but not installed"
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is required but not installed"
        exit 1
    fi
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        log_error "Node.js is required but not installed"
        exit 1
    fi
    
    # Check Go
    if ! command -v go &> /dev/null; then
        log_error "Go is required but not installed"
        exit 1
    fi
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is required but not installed"
        exit 1
    fi
    
    log_success "All prerequisites are installed"
}

# Build Dashboard
build_dashboard() {
    log_info "Building React dashboard..."
    
    cd dashboard
    
    # Install dependencies
    log_info "Installing npm dependencies..."
    npm install
    
    # Build production bundle
    log_info "Building production bundle..."
    npm run build
    
    cd ..
    log_success "Dashboard built successfully"
}

# Build Go Agents
build_agents() {
    log_info "Building Go behavioral agents..."
    
    cd agents
    
    # Download Go dependencies
    log_info "Downloading Go dependencies..."
    go mod tidy
    
    # Build for Linux
    log_info "Building Linux agent..."
    GOOS=linux GOARCH=amd64 go build -o bin/behavioral-agent-linux collectors/behavioral_agent.go
    
    # Build for Windows
    log_info "Building Windows agent..."
    GOOS=windows GOARCH=amd64 go build -o bin/behavioral-agent-windows.exe collectors/behavioral_agent.go
    
    # Build for macOS
    log_info "Building macOS agent..."
    GOOS=darwin GOARCH=amd64 go build -o bin/behavioral-agent-macos collectors/behavioral_agent.go
    
    cd ..
    log_success "Go agents built successfully"
}

# Build Python Services
build_python_services() {
    log_info "Setting up Python environment..."
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install dependencies
    log_info "Installing Python dependencies..."
    pip install -r requirements.txt
    
    log_success "Python services ready"
}

# Build Docker Images
build_docker_images() {
    log_info "Building Docker images..."
    
    # Build core API image
    log_info "Building core API image..."
    docker build -t zehraguard-core:latest -f deployment/docker/Dockerfile.core .
    
    # Build dashboard image
    log_info "Building dashboard image..."
    docker build -t zehraguard-dashboard:latest -f deployment/docker/Dockerfile.dashboard .
    
    # Build agent image
    log_info "Building agent image..."
    docker build -t zehraguard-agent:latest -f deployment/docker/Dockerfile.agent .
    
    log_success "All Docker images built successfully"
}

# Generate SSL Certificates
generate_certificates() {
    log_info "Generating SSL certificates..."
    
    mkdir -p deployment/ssl
    
    # Generate self-signed certificate for development
    openssl req -x509 -newkey rsa:4096 -keyout deployment/ssl/key.pem -out deployment/ssl/cert.pem -days 365 -nodes -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
    
    log_success "SSL certificates generated"
}

# Initialize Database
init_database() {
    log_info "Initializing database..."
    
    # Start database services
    docker-compose -f deployment/docker-compose.yml up -d postgres redis influxdb rabbitmq
    
    # Wait for databases to be ready
    log_info "Waiting for databases to be ready..."
    sleep 30
    
    # Run database migrations
    source venv/bin/activate
    cd core
    python -c "
from database import init_db
init_db()
print('Database initialized successfully')
"
    cd ..
    
    log_success "Database initialized"
}

# Deploy with Docker Compose
deploy_docker_compose() {
    log_info "Deploying with Docker Compose..."
    
    # Start all services
    docker-compose -f deployment/docker-compose.yml up -d
    
    # Wait for services to be ready
    log_info "Waiting for services to start..."
    sleep 60
    
    # Check service health
    log_info "Checking service health..."
    
    # Check core API
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        log_success "Core API is healthy"
    else
        log_warning "Core API health check failed"
    fi
    
    # Check dashboard
    if curl -f http://localhost:3000 > /dev/null 2>&1; then
        log_success "Dashboard is accessible"
    else
        log_warning "Dashboard health check failed"
    fi
    
    log_success "Docker Compose deployment complete"
}

# Deploy with Kubernetes
deploy_kubernetes() {
    log_info "Deploying with Kubernetes..."
    
    # Check if kubectl is available
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl is required for Kubernetes deployment"
        exit 1
    fi
    
    # Apply namespace
    kubectl apply -f deployment/k8s/namespace.yaml
    
    # Apply ConfigMaps and Secrets
    kubectl apply -f deployment/k8s/configmap.yaml
    kubectl apply -f deployment/k8s/secrets.yaml
    
    # Apply persistent volumes
    kubectl apply -f deployment/k8s/postgres-pv.yaml
    kubectl apply -f deployment/k8s/redis-pv.yaml
    
    # Apply database services
    kubectl apply -f deployment/k8s/postgres.yaml
    kubectl apply -f deployment/k8s/redis.yaml
    kubectl apply -f deployment/k8s/influxdb.yaml
    kubectl apply -f deployment/k8s/rabbitmq.yaml
    
    # Wait for databases
    log_info "Waiting for databases to be ready..."
    kubectl wait --for=condition=ready pod -l app=postgres -n zehraguard --timeout=300s
    kubectl wait --for=condition=ready pod -l app=redis -n zehraguard --timeout=300s
    
    # Apply application services
    kubectl apply -f deployment/k8s/core-api.yaml
    kubectl apply -f deployment/k8s/dashboard.yaml
    kubectl apply -f deployment/k8s/ingress.yaml
    
    # Wait for application services
    log_info "Waiting for application services..."
    kubectl wait --for=condition=ready pod -l app=zehraguard-core -n zehraguard --timeout=300s
    kubectl wait --for=condition=ready pod -l app=zehraguard-dashboard -n zehraguard --timeout=300s
    
    log_success "Kubernetes deployment complete"
}

# Generate Test Data
generate_test_data() {
    log_info "Generating test data..."
    
    source venv/bin/activate
    python scripts/generate_test_data.py
    
    log_success "Test data generated"
}

# Main deployment function
main() {
    echo
    log_info "Starting ZehraGuard InsightX deployment..."
    echo
    
    # Parse command line arguments
    DEPLOYMENT_TYPE="docker-compose"
    SKIP_BUILD=false
    GENERATE_DATA=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --kubernetes|-k)
                DEPLOYMENT_TYPE="kubernetes"
                shift
                ;;
            --skip-build|-s)
                SKIP_BUILD=true
                shift
                ;;
            --generate-data|-g)
                GENERATE_DATA=true
                shift
                ;;
            --help|-h)
                echo "Usage: $0 [OPTIONS]"
                echo "Options:"
                echo "  --kubernetes, -k    Deploy to Kubernetes (default: docker-compose)"
                echo "  --skip-build, -s    Skip building components"
                echo "  --generate-data, -g Generate test data after deployment"
                echo "  --help, -h          Show this help message"
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                exit 1
                ;;
        esac
    done
    
    # Check prerequisites
    check_prerequisites
    
    if [ "$SKIP_BUILD" = false ]; then
        # Build components
        build_python_services
        build_dashboard
        build_agents
        build_docker_images
        generate_certificates
    else
        log_info "Skipping build steps"
    fi
    
    # Initialize database
    init_database
    
    # Deploy based on type
    if [ "$DEPLOYMENT_TYPE" = "kubernetes" ]; then
        deploy_kubernetes
    else
        deploy_docker_compose
    fi
    
    # Generate test data if requested
    if [ "$GENERATE_DATA" = true ]; then
        generate_test_data
    fi
    
    echo
    log_success "🎉 ZehraGuard InsightX deployment complete!"
    echo
    echo "📊 Access Points:"
    echo "   Dashboard: http://localhost:3000"
    echo "   API Docs:  http://localhost:8000/docs"
    echo "   Metrics:   http://localhost:9090 (Prometheus)"
    echo "   Logs:      http://localhost:3001 (Grafana)"
    echo
    echo "🔧 Management Commands:"
    echo "   View logs:     docker-compose -f deployment/docker-compose.yml logs -f"
    echo "   Stop services: docker-compose -f deployment/docker-compose.yml down"
    echo "   Scale API:     docker-compose -f deployment/docker-compose.yml up -d --scale core-api=3"
    echo
    echo "📖 Documentation: See DEPLOYMENT.md for detailed instructions"
}

# Run main function
main "$@"
