# ZehraGuard InsightX - Production Test and Deployment Guide

## 🚀 Production Deployment Steps

### 1. Prerequisites Check
Ensure you have the following installed:
- Docker 20.10+ and Docker Compose 2.0+
- Python 3.9+ (for development)
- Node.js 16+ (for dashboard development)
- Go 1.21+ (for agents)
- At least 8GB RAM and 50GB storage

### 2. Build for Production
```bash
# Build all components
./build.sh v1.0.0

# This creates:
# - Docker images for core, dashboard, and agents
# - Deployment package: zehraguard-insightx-v1.0.0.tar.gz
```

### 3. Quick Start (Local Testing)
```bash
# Extract deployment package
tar -xzf zehraguard-insightx-v1.0.0.tar.gz
cd build

# Install (creates .env with secure passwords)
./install.sh

# Access the system
open http://localhost:3000  # Dashboard
open http://localhost:8000/docs  # API Documentation
```

### 4. Production Deployment Options

#### Option A: Docker Compose (Recommended for single server)
```bash
# Copy environment file and customize
cp .env.example .env
nano .env  # Update passwords and settings

# Deploy
docker-compose up -d

# Monitor
docker-compose logs -f
```

#### Option B: Kubernetes (Recommended for clusters)
```bash
# Update kubernetes.yaml with your settings
nano deployment/kubernetes.yaml

# Deploy
kubectl apply -f deployment/kubernetes.yaml

# Monitor
kubectl get pods -n zehraguard
kubectl logs -n zehraguard -l app=zehraguard-core
```

### 5. Initial Configuration

#### Create Admin User
```bash
# Connect to running container
docker-compose exec zehraguard-core python -c "
from core.database import Database
import asyncio

async def create_admin():
    db = Database()
    # Admin user creation logic here
    print('Admin user created')

asyncio.run(create_admin())
"
```

#### Configure SIEM Integrations
1. Access dashboard: http://localhost:3000
2. Navigate to Settings > Integrations
3. Configure your SIEM endpoints:
   - Splunk HEC
   - Azure Sentinel
   - IBM QRadar
   - Wazuh

### 6. Agent Deployment

#### Install on Windows Endpoints
```powershell
# Download agent
Invoke-WebRequest -Uri "https://releases.zehraguard.com/agents/windows/behavioral_agent.exe" -OutFile "behavioral_agent.exe"

# Configure
./behavioral_agent.exe --config config.json

# Install as service
./behavioral_agent.exe --install-service
```

#### Install on Linux Endpoints  
```bash
# Download agent
wget https://releases.zehraguard.com/agents/linux/behavioral_agent

# Configure
./behavioral_agent --config config.json

# Install as systemd service
sudo ./behavioral_agent --install-service
```

#### Install on macOS Endpoints
```bash
# Download agent
curl -O https://releases.zehraguard.com/agents/macos/behavioral_agent

# Configure and install
./behavioral_agent --config config.json --install
```

### 7. Testing the Deployment

#### Health Checks
```bash
# API Health
curl http://localhost:8000/health

# Service Status
docker-compose ps

# View logs
docker-compose logs zehraguard-core
```

#### Generate Test Data
```bash
# Create test users
curl -X POST http://localhost:8000/api/v1/users \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test001",
    "username": "test.user",
    "email": "test@company.com",
    "department": "testing",
    "role": "test_user",
    "start_date": "2024-01-01T00:00:00Z",
    "access_level": "standard"
  }'

# Simulate behavioral data
python scripts/generate_test_data.py
```

#### Verify Alert Generation
1. Monitor dashboard for incoming alerts
2. Check SIEM integration (if configured)
3. Verify email notifications (if configured)

### 8. Monitoring and Maintenance

#### Prometheus Metrics
- Available at: http://localhost:9090/metrics
- Key metrics:
  - `zehraguard_alerts_total`
  - `zehraguard_users_monitored`
  - `zehraguard_ml_predictions_total`
  - `zehraguard_api_requests_duration`

#### Log Management
```bash
# View application logs
docker-compose logs -f zehraguard-core

# View specific service logs
docker-compose logs -f postgres
docker-compose logs -f redis
docker-compose logs -f influxdb
```

#### Backup Procedures
```bash
# Database backup
docker-compose exec postgres pg_dump -U zehraguard zehraguard > backup_$(date +%Y%m%d).sql

# Full system backup
tar -czf zehraguard_backup_$(date +%Y%m%d).tar.gz data/ logs/ .env
```

### 9. Security Hardening

#### SSL/TLS Configuration
1. Generate SSL certificates:
```bash
# Self-signed (for testing)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ssl/private.key -out ssl/certificate.crt

# Let's Encrypt (for production)
certbot certonly --webroot -w /var/www/html -d yourdomain.com
```

2. Update nginx configuration to use SSL
3. Redirect HTTP to HTTPS

#### Firewall Configuration
```bash
# Allow only necessary ports
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP (for redirect)
sudo ufw allow 443   # HTTPS
sudo ufw enable
```

#### Database Security
1. Change default passwords
2. Restrict database access to localhost
3. Enable SSL for database connections
4. Regular security updates

### 10. Performance Tuning

#### Database Optimization
```sql
-- Create additional indexes for performance
CREATE INDEX CONCURRENTLY idx_data_events_timestamp_user 
ON data_events(timestamp, user_id);

CREATE INDEX CONCURRENTLY idx_threat_alerts_created_status 
ON threat_alerts(created_at, status);

-- Analyze tables
ANALYZE;
```

#### Redis Configuration
```redis
# In redis.conf
maxmemory 2gb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
```

#### Application Scaling
```yaml
# In docker-compose.yml - scale core service
services:
  zehraguard-core:
    deploy:
      replicas: 3
    # Add load balancer
```

### 11. Troubleshooting

#### Common Issues

**Services won't start:**
```bash
# Check ports
netstat -tulpn | grep ":8000\|:5432\|:6379"

# Check Docker resources
docker system df
docker system prune  # Clean up if needed
```

**High memory usage:**
```bash
# Monitor resources
docker stats

# Adjust ML model parameters in .env
ANOMALY_THRESHOLD=0.9  # Reduce sensitivity
```

**Database connection issues:**
```bash
# Test connection
docker-compose exec postgres psql -U zehraguard -d zehraguard -c "SELECT 1;"

# Check logs
docker-compose logs postgres
```

**Agent connection issues:**
```bash
# Test connectivity from agent
curl -v http://your-server:8000/health

# Check firewall
telnet your-server 8000
```

### 12. Support and Documentation

- **Documentation**: https://docs.zehraguard.com
- **API Reference**: http://localhost:8000/docs
- **Community**: https://community.zehraguard.com
- **Enterprise Support**: support@zehraguard.com
- **Security Issues**: security@zehraguard.com

### 13. Compliance and Auditing

#### GDPR Compliance
- Data retention policies configured
- User consent mechanisms
- Data deletion procedures
- Privacy by design architecture

#### SOC 2 Controls
- Access control and authentication
- System monitoring and logging
- Incident response procedures
- Change management processes

#### Audit Reports
```bash
# Generate compliance report
curl "http://localhost:8000/api/v1/reports/compliance?start_date=2024-01-01&end_date=2024-12-31&compliance_type=gdpr"
```

## ✅ Deployment Checklist

- [ ] Prerequisites installed
- [ ] Build script executed successfully  
- [ ] Environment variables configured
- [ ] SSL certificates generated
- [ ] Database initialized
- [ ] Admin user created
- [ ] SIEM integrations configured
- [ ] Agents deployed to endpoints
- [ ] Health checks passing
- [ ] Monitoring configured
- [ ] Backup procedures tested
- [ ] Security hardening applied
- [ ] Performance tuned
- [ ] Documentation reviewed
- [ ] Team trained on system usage

---

**🛡️ ZehraGuard InsightX is now ready for production!**

For additional support, contact our technical team at support@zehraguard.com or visit our documentation at https://docs.zehraguard.com.
