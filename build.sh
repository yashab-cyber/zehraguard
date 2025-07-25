#!/bin/bash

# ZehraGuard InsightX Production Build Script

set -e

echo "🚀 Building ZehraGuard InsightX for Production..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="zehraguard"
VERSION=${1:-"latest"}
REGISTRY=${DOCKER_REGISTRY:-"zehraguard"}

echo -e "${BLUE}Project: ${PROJECT_NAME}${NC}"
echo -e "${BLUE}Version: ${VERSION}${NC}"
echo -e "${BLUE}Registry: ${REGISTRY}${NC}"

# Check prerequisites
echo -e "\n${YELLOW}Checking prerequisites...${NC}"

if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker is not installed${NC}"
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo -e "${RED}Node.js is not installed${NC}"
    exit 1
fi

if ! command -v go &> /dev/null; then
    echo -e "${RED}Go is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✓ All prerequisites met${NC}"

# Create build directory
BUILD_DIR="build"
rm -rf $BUILD_DIR
mkdir -p $BUILD_DIR

# Build React Dashboard
echo -e "\n${YELLOW}Building React Dashboard...${NC}"
cd dashboard
npm install
npm run build
cd ..
cp -r dashboard/build $BUILD_DIR/dashboard

# Build Go Agents
echo -e "\n${YELLOW}Building Go Agents...${NC}"
cd agents
go mod tidy
go build -o ../build/behavioral_agent collectors/behavioral_agent.go
cd ..

# Create Python package
echo -e "\n${YELLOW}Preparing Python application...${NC}"
mkdir -p $BUILD_DIR/app
cp -r core $BUILD_DIR/app/
cp -r integrations $BUILD_DIR/app/
cp -r ml $BUILD_DIR/app/
cp requirements.txt $BUILD_DIR/app/
cp main.py $BUILD_DIR/app/

# Build Docker Images
echo -e "\n${YELLOW}Building Docker images...${NC}"

# Core API Image
echo -e "${BLUE}Building core API image...${NC}"
docker build -t ${REGISTRY}/zehraguard-core:${VERSION} .

# Dashboard Image
echo -e "${BLUE}Building dashboard image...${NC}"
cat > Dockerfile.dashboard << EOF
FROM nginx:alpine
COPY build/dashboard /usr/share/nginx/html
COPY deployment/nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
EOF

docker build -f Dockerfile.dashboard -t ${REGISTRY}/zehraguard-dashboard:${VERSION} .
rm Dockerfile.dashboard

# Agent Image
echo -e "${BLUE}Building agent image...${NC}"
cat > Dockerfile.agent << EOF
FROM golang:1.21-alpine AS builder
WORKDIR /app
COPY agents/go.mod agents/go.sum ./
RUN go mod download
COPY agents/ .
RUN go build -o behavioral_agent collectors/behavioral_agent.go

FROM alpine:latest
RUN apk --no-cache add ca-certificates
WORKDIR /root/
COPY --from=builder /app/behavioral_agent .
CMD ["./behavioral_agent"]
EOF

docker build -f Dockerfile.agent -t ${REGISTRY}/zehraguard-agent:${VERSION} .
rm Dockerfile.agent

# Tag latest
if [ "$VERSION" != "latest" ]; then
    docker tag ${REGISTRY}/zehraguard-core:${VERSION} ${REGISTRY}/zehraguard-core:latest
    docker tag ${REGISTRY}/zehraguard-dashboard:${VERSION} ${REGISTRY}/zehraguard-dashboard:latest
    docker tag ${REGISTRY}/zehraguard-agent:${VERSION} ${REGISTRY}/zehraguard-agent:latest
fi

# Create deployment package
echo -e "\n${YELLOW}Creating deployment package...${NC}"
mkdir -p $BUILD_DIR/deployment
cp -r deployment/* $BUILD_DIR/deployment/
cp docker-compose.yml $BUILD_DIR/

# Update version in deployment files
sed -i "s/latest/${VERSION}/g" $BUILD_DIR/deployment/kubernetes.yaml
sed -i "s/latest/${VERSION}/g" $BUILD_DIR/docker-compose.yml

# Create installation script
cat > $BUILD_DIR/install.sh << 'EOF'
#!/bin/bash

# ZehraGuard InsightX Installation Script

set -e

echo "🛡️  Installing ZehraGuard InsightX..."

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "Please do not run this script as root"
    exit 1
fi

# Check prerequisites
if ! command -v docker &> /dev/null; then
    echo "Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
fi

if ! command -v docker-compose &> /dev/null; then
    echo "Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# Generate random passwords
POSTGRES_PASSWORD=$(openssl rand -base64 32)
REDIS_PASSWORD=$(openssl rand -base64 32)
RABBITMQ_PASSWORD=$(openssl rand -base64 32)
INFLUXDB_TOKEN=$(openssl rand -base64 32)

# Create .env file
cat > .env << EOL
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
REDIS_PASSWORD=${REDIS_PASSWORD}
RABBITMQ_PASSWORD=${RABBITMQ_PASSWORD}
INFLUXDB_TOKEN=${INFLUXDB_TOKEN}
SECRET_KEY=$(openssl rand -base64 32)
EOL

echo "🔐 Generated secure passwords in .env file"

# Create data directories
mkdir -p data/postgres data/redis data/influxdb data/rabbitmq logs

# Set permissions
chmod 700 data/postgres data/redis data/influxdb data/rabbitmq
chmod 755 logs

# Start services
echo "🚀 Starting ZehraGuard InsightX..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 30

# Check if services are running
if docker-compose ps | grep -q "Up"; then
    echo "✅ ZehraGuard InsightX is running!"
    echo ""
    echo "🌐 Access URLs:"
    echo "   Web Dashboard: http://localhost:3000"
    echo "   API Documentation: http://localhost:8000/docs"
    echo "   InfluxDB UI: http://localhost:8086"
    echo ""
    echo "📊 Default credentials:"
    echo "   Admin user: admin"
    echo "   Admin password: Check the logs for generated password"
    echo ""
    echo "📖 Documentation: https://docs.zehraguard.com"
    echo "🆘 Support: support@zehraguard.com"
else
    echo "❌ Some services failed to start. Check logs with: docker-compose logs"
fi
EOF

chmod +x $BUILD_DIR/install.sh

# Create README for deployment
cat > $BUILD_DIR/README.md << 'EOF'
# ZehraGuard InsightX Deployment

## Quick Start

1. **Prerequisites**
   - Docker and Docker Compose
   - At least 8GB RAM
   - 50GB free disk space

2. **Installation**
   ```bash
   ./install.sh
   ```

3. **Access**
   - Web Dashboard: http://localhost:3000
   - API: http://localhost:8000
   - Documentation: http://localhost:8000/docs

## Manual Deployment

### Using Docker Compose
```bash
docker-compose up -d
```

### Using Kubernetes
```bash
kubectl apply -f deployment/kubernetes.yaml
```

## Configuration

### Environment Variables
- `POSTGRES_PASSWORD`: Database password
- `REDIS_PASSWORD`: Redis password
- `SECRET_KEY`: Application secret key
- `DEBUG`: Enable debug mode (default: false)

### Volumes
- `./data/postgres`: PostgreSQL data
- `./data/redis`: Redis data
- `./data/influxdb`: InfluxDB data
- `./logs`: Application logs

## Monitoring

### Health Checks
- API Health: GET /health
- Metrics: GET /metrics (Prometheus format)

### Logs
```bash
docker-compose logs -f
```

## Backup

### Database Backup
```bash
docker-compose exec postgres pg_dump -U zehraguard zehraguard > backup.sql
```

### Full Backup
```bash
tar -czf zehraguard-backup-$(date +%Y%m%d).tar.gz data/ logs/
```

## Support

- Documentation: https://docs.zehraguard.com
- Issues: https://github.com/zehraguard/insightx/issues
- Email: support@zehraguard.com
EOF

# Create archive
echo -e "\n${YELLOW}Creating deployment archive...${NC}"
cd $BUILD_DIR
tar -czf ../zehraguard-insightx-${VERSION}.tar.gz .
cd ..

# Summary
echo -e "\n${GREEN}✅ Build completed successfully!${NC}"
echo -e "${BLUE}Docker Images:${NC}"
docker images | grep zehraguard

echo -e "\n${BLUE}Deployment Package:${NC}"
echo -e "📦 zehraguard-insightx-${VERSION}.tar.gz"

echo -e "\n${BLUE}Next Steps:${NC}"
echo -e "1. Test the deployment: cd build && ./install.sh"
echo -e "2. Push images to registry: docker push ${REGISTRY}/zehraguard-*:${VERSION}"
echo -e "3. Deploy to production using the deployment package"

echo -e "\n${GREEN}🎉 ZehraGuard InsightX build complete!${NC}"
