# YouTube AI Platform - Production Deployment Guide

## 🚀 Quick Start

### 1. Initial Setup
```bash
# Make setup script executable and run it
chmod +x scripts/setup_production.sh
./scripts/setup_production.sh
```

### 2. Configure Environment
```bash
# Edit the .env file with your actual API keys
nano .env
```

### 3. Deploy to Production
```bash
# Choose your deployment method:
./scripts/production_launcher.sh local          # Local Docker deployment
./scripts/production_launcher.sh docker-compose # Docker Compose deployment
./scripts/production_launcher.sh gcloud         # Google Cloud deployment
./scripts/production_launcher.sh github         # GitHub Actions deployment
```

---

## 📋 Prerequisites

### Required Software
- **Docker** (v20.10+)
- **Docker Compose** (v2.0+)
- **Python 3.12**
- **Node.js 18+** (for frontend)
- **Git** (for GitHub deployment)

### Required API Keys
- OpenAI API Key
- YouTube API credentials
- Google Cloud credentials (for GCloud deployment)
- GitHub access token (for GitHub deployment)

---

## 🏗️ Deployment Options

### 1. Local Deployment (Docker)
**Best for:** Development, testing, local production simulation

```bash
./scripts/production_launcher.sh local
```

**What it does:**
- Builds Docker images for backend and mini app
- Starts containers on local ports
- Runs frontend with npm
- Performs health checks
- Provides service URLs

**Service URLs:**
- Backend API: http://localhost:8000
- Frontend: http://localhost:3000
- Mini App: http://localhost:8080

### 2. Docker Compose Deployment
**Best for:** Production-like environment, easy scaling

```bash
./scripts/production_launcher.sh docker-compose
```

**What it does:**
- Creates docker-compose.yml with all services
- Sets up Nginx reverse proxy
- Configures health checks and logging
- Manages service dependencies

**Features:**
- Automatic service restart
- Load balancing with Nginx
- Centralized logging
- Volume persistence

### 3. Google Cloud Deployment
**Best for:** Production, scalability, managed infrastructure

```bash
./scripts/production_launcher.sh gcloud
```

**Prerequisites:**
```bash
# Install Google Cloud CLI
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Authenticate and set project
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

**What it does:**
- Builds and pushes Docker image to Google Container Registry
- Deploys to Google Cloud Run
- Sets environment variables from .env file
- Provides public service URL

### 4. GitHub Actions Deployment
**Best for:** CI/CD, automated deployments

```bash
./scripts/production_launcher.sh github
```

**Prerequisites:**
- GitHub repository with secrets configured
- GitHub Actions workflow file (.github/workflows/deploy.yml)

**What it does:**
- Pushes code to trigger GitHub Actions
- Runs tests and builds
- Deploys to configured environment
- Provides deployment status

### GitHub Secrets & Cloud Run Env Mapping
The GitHub workflow injects secrets directly into Cloud Run environment variables. Configure these in your repo secrets:

Required secrets:
- `GCP_SA_KEY`, `GCP_PROJECT_ID`, `GCS_BUCKET`
- `DATABASE_URL`, `OPENAI_API_KEY`, `SECRET_KEY`, `ADMIN_SECRET_KEY`
- `PAYMENT_SHOPIER_API_KEY`, `PAYMENT_SHOPIER_API_SECRET`
- `PAYMENT_SHOPIER_PERSONAL_ACCESS_TOKEN`, `PAYMENT_SHOPIER_WEBHOOK_TOKEN`

Optional secrets:
- `PAYMENT_STRIPE_SECRET_KEY`, `PAYMENT_STRIPE_PUBLISHABLE_KEY`
- `PAYMENT_PAYONEER_API_KEY`, `PAYMENT_PAYONEER_SECRET_KEY`, `PAYMENT_PAYONEER_PROGRAM_ID`
- `YOUTUBE_API_KEY`
- YouTube overrides: `YOUTUBE_DATABASE_URL`, `YOUTUBE_OPENAI_API_KEY`, `YOUTUBE_SECRET_KEY`, `YOUTUBE_ADMIN_SECRET_KEY`, `YOUTUBE_PAYMENT_*`

Non-secret runtime env vars are set in `.github/workflows/deploy.yml`, including:
`SHOPIER_APP_MODE`, `SHOPIER_ALLOW_MOCK`, `DATA_DIR`, `REVENUE_REAL_ONLY`,
`VIDEO_PIPELINE_ALLOW_PLACEHOLDERS`, `BIZOP_AUTO_SYNC`, `OPS_RATE_LIMIT_SECONDS`, `CLOUD_RUN_SERVICE`.

---

## 🔧 Configuration

### Environment Variables
Copy `config/env.full.example` to `.env` and configure (use `config/env.template` for a minimal base):

```bash
# Core settings
ENVIRONMENT=production
SECRET_KEY=your-super-secret-key
DATABASE_URL=your-database-url
# Optional Cloud SQL
# CLOUD_SQL_INSTANCE=project:region:instance
# DATABASE_URL=postgresql+asyncpg://USER:PASSWORD@/DBNAME?host=/cloudsql/project:region:instance

# AI Services
OPENAI_API_KEY=sk-your-openai-key
GEMINI_API_KEY=your-gemini-key
GROQ_API_KEY=your-groq-key

# YouTube API
YOUTUBE_CLIENT_ID=your-client-id
YOUTUBE_CLIENT_SECRET=your-client-secret
YOUTUBE_REFRESH_TOKEN=your-refresh-token

# Payment Services
STRIPE_API_KEY=sk-your-stripe-key
PAYONEER_CUSTOMER_ID=your-payoneer-id

# BizOp ingestion (Alexandria Protocol data)
BIZOP_AUTO_SYNC=true
# BIZOP_DATA_ROOT=/app/docs
```

### Service Configuration

#### Backend (Port 8000)
- FastAPI application
- Health endpoint: `/health`
- API documentation: `/docs`
- Database: SQLite (local) or PostgreSQL (production)

#### Frontend (Port 3000)
- Next.js application
- Static build for production
- API integration with backend

#### Mini App (Port 8080)
- Cash generation focus
- High-CPM content strategy
- Independent deployment

#### BizOp Catalog (Backend)
- Auto-ingests `docs/alexandria_protocol/*.json` and `docs/rankedopportunities.csv`
- Endpoints:
  - `GET /api/bizop/opportunities`
  - `POST /api/bizop/refresh`
  - `GET /api/bizop/sources`

#### Nginx (Port 80/443)
- Reverse proxy
- SSL termination
- Load balancing
- Static file serving

---

## 📊 Monitoring & Health Checks

### Health Monitoring
```bash
# Start continuous health monitoring
./scripts/production_launcher.sh monitor

# Check current status
./scripts/production_launcher.sh status
```

### Health Endpoints
- Backend: `http://localhost:8000/health`
- Mini App: `http://localhost:8080/health`
- Frontend: `http://localhost:3000`

### Logs
```bash
# View backend logs
docker logs youtube-income-commander-prod -f

# View mini app logs
docker logs youtube-income-commander-mini -f

# View all logs (Docker Compose)
docker-compose logs -f
```

---

## 🔄 Management Commands

### Start Services
```bash
# Local deployment
./scripts/production_launcher.sh local

# Docker Compose
docker-compose up -d

# Individual services
docker-compose up -d backend
docker-compose up -d frontend
docker-compose up -d mini-app
```

### Stop Services
```bash
# Stop all services
docker-compose down

# Stop specific service
docker-compose stop backend

# Stop local deployment
docker stop youtube-income-commander-prod youtube-income-commander-mini
```

### Restart Services
```bash
# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart backend

# Restart with rebuild
docker-compose up -d --build
```

### Update Services
```bash
# Pull latest code
git pull origin main

# Rebuild and restart
./scripts/production_launcher.sh local
# or
docker-compose up -d --build
```

---

## 🛠️ Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Check what's using the port
lsof -i :8000
lsof -i :3000
lsof -i :8080

# Kill process or change port in .env
```

#### 2. Docker Permission Issues
```bash
# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

#### 3. Environment Variables Not Loading
```bash
# Check .env file exists and has correct format
cat .env

# Validate environment variables
./scripts/production_launcher.sh local
```

#### 4. Health Check Failures
```bash
# Check service logs
docker logs youtube-income-commander-prod

# Check if services are running
docker ps

# Restart services
docker-compose restart
```

### Debug Mode
```bash
# Run with debug logging
DEBUG=true ./scripts/production_launcher.sh local

# Check deployment logs
tail -f deployment.log
```

---

## 🔒 Security Considerations

### Production Security
1. **Use strong SECRET_KEY**
2. **Enable HTTPS** (SSL certificates)
3. **Configure CORS** properly
4. **Use environment variables** for secrets
5. **Regular security updates**
6. **Monitor access logs**

### SSL Configuration
```bash
# Generate SSL certificates
mkdir -p ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ssl/nginx.key -out ssl/nginx.crt

# Update nginx.conf for SSL
```

### Firewall Configuration
```bash
# Allow only necessary ports
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 22
sudo ufw enable
```

---

## 📈 Scaling

### Horizontal Scaling
```bash
# Scale backend services
docker-compose up -d --scale backend=3

# Scale with load balancer
docker-compose up -d --scale backend=5 --scale frontend=2
```

### Vertical Scaling
- Increase container resources in docker-compose.yml
- Use larger instance types in cloud deployments
- Optimize application performance

### Database Scaling
- Use managed database services
- Implement connection pooling
- Add read replicas for read-heavy workloads

---

## 💰 Cost Optimization

### Local Development
- Use local deployment for development
- Minimize cloud resource usage during development

### Cloud Optimization
- Use spot instances where possible
- Implement auto-scaling
- Monitor and optimize resource usage
- Use reserved instances for predictable workloads

---

## 📞 Support

### Getting Help
1. Check the logs: `docker-compose logs`
2. Verify configuration: `./scripts/production_launcher.sh status`
3. Review this documentation
4. Check GitHub issues

### Emergency Procedures
```bash
# Emergency stop all services
docker-compose down

# Emergency restart
./scripts/production_launcher.sh local

# Rollback to previous version
git checkout HEAD~1
./scripts/production_launcher.sh local
```

---

## 🎯 Success Metrics

### Deployment Success
- ✅ All services healthy
- ✅ Health checks passing
- ✅ Services responding on expected ports
- ✅ No error logs

### Performance Metrics
- Response time < 200ms
- Uptime > 99.9%
- Error rate < 0.1%
- Resource utilization < 80%

### Business Metrics
- Revenue generation from mini app
- User engagement on main platform
- Content creation pipeline efficiency
- ROI on AI-generated content

---

**Ready to deploy? Run `./scripts/setup_production.sh` to get started!** 
