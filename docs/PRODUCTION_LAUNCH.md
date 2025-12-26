# 🎬 YouTube AI Content Creator - Production Deployment

## 🚀 Quick Start (5 Minutes)

### 1. Clone and Setup
```bash
git clone <your-repo>
cd youtube-ai-content-creator
chmod +x start.sh
./start.sh
```

### 2. Configure Environment
Edit `.env` file with your API keys:
```env
OPENAI_API_KEY=sk-your-openai-key
YOUTUBE_API_KEY=your-youtube-api-key
GOOGLE_CLOUD_PROJECT=your-gcp-project
GOOGLE_CLOUD_STORAGE_BUCKET=your-bucket
SECRET_KEY=your-secure-secret-key-32-chars-min
```

### 3. Access Your Application
- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🔑 Required API Keys

### OpenAI API Key
1. Go to https://platform.openai.com/api-keys
2. Create new secret key
3. Copy to `OPENAI_API_KEY` in `.env`

### YouTube API Key
1. Go to https://console.cloud.google.com/
2. Enable YouTube Data API v3
3. Create credentials (API Key)
4. Copy to `YOUTUBE_API_KEY` in `.env`

### Google Cloud Setup
1. Create GCP project
2. Create Cloud Storage bucket
3. Set up service account (optional)
4. Update `GOOGLE_CLOUD_PROJECT` and `GOOGLE_CLOUD_STORAGE_BUCKET`

## 🌐 Production Deployment

### Docker Deployment
```bash
docker build -t youtube-ai-creator .
docker run -p 8000:8000 --env-file .env youtube-ai-creator
```

### Google Cloud Run
```bash
gcloud run deploy youtube-ai-creator \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## 📊 Core Features

✅ **Content Generation**: AI-powered video scripts and ideas  
✅ **YouTube Integration**: Channel analytics and video management  
✅ **Monetization Tracking**: Revenue analytics and optimization  
✅ **Content Scheduling**: Automated posting and management  
✅ **Performance Analytics**: Detailed insights and reporting  

## 🔧 API Endpoints

### Content Management
- `POST /api/v1/content-ideas` - Create content idea
- `GET /api/v1/content-ideas` - List content ideas
- `POST /api/v1/content-ideas/{id}/generate` - Generate content
- `POST /api/v1/videos` - Create video
- `GET /api/v1/videos` - List videos

### Analytics
- `GET /api/v1/analytics/overview` - Channel overview
- `GET /api/v1/analytics/revenue` - Revenue analytics
- `GET /api/v1/analytics/performance` - Performance metrics

### Upload & Media
- `POST /api/v1/upload/url` - Generate upload URL
- `POST /api/v1/videos/{id}/thumbnail` - Generate thumbnail
- `POST /api/v1/videos/{id}/audio` - Generate audio

## 💰 Monetization Features

### Revenue Tracking
- Ad revenue monitoring
- Sponsorship tracking
- Affiliate commission tracking
- Multi-stream revenue analytics

### Optimization
- Content performance analysis
- Audience engagement metrics
- Revenue per video calculations
- Growth trend analysis

## 🛠️ Maintenance

### Database Backup
```bash
# SQLite backup
cp youtube_ai.db youtube_ai_backup_$(date +%Y%m%d).db

# PostgreSQL backup
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql
```

### Log Monitoring
```bash
# View application logs
tail -f logs/app.log

# Check error logs
grep ERROR logs/app.log
```

### Health Monitoring
```bash
# Check application health
curl http://localhost:8000/health

# Monitor performance
curl http://localhost:8000/metrics
```

## 🔒 Security

### Environment Variables
- Never commit `.env` files
- Use strong SECRET_KEY (32+ characters)
- Rotate API keys regularly
- Use environment-specific configurations

### API Security
- Rate limiting enabled
- Input validation on all endpoints
- Error handling without sensitive data exposure
- CORS properly configured

## 📈 Scaling

### Horizontal Scaling
```bash
# Multiple workers
uvicorn main:app --workers 4

# Load balancer setup
# Configure nginx or cloud load balancer
```

### Database Scaling
```bash
# PostgreSQL with connection pooling
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db?pool_size=20&max_overflow=30
```

### Caching
```bash
# Redis caching
REDIS_URL=redis://localhost:6379/0
```

## 🚨 Troubleshooting

### Common Issues

**1. API Key Errors**
```
Error: Invalid API key
Solution: Check API key format and permissions
```

**2. Database Connection**
```
Error: Database connection failed
Solution: Verify DATABASE_URL and database server status
```

**3. Google Cloud Permissions**
```
Error: Access denied to Cloud Storage
Solution: Check service account permissions and bucket access
```

### Debug Mode
```bash
# Enable debug mode
export DEBUG=true
python run_production.py
```

### Log Analysis
```bash
# Check specific errors
grep "ERROR" logs/app.log | tail -20

# Monitor API requests
grep "POST\|GET" logs/app.log | tail -50
```

## 📞 Support

### Documentation
- API Docs: `/docs` endpoint
- Health Check: `/health` endpoint
- Metrics: `/metrics` endpoint

### Monitoring
- Application logs in `logs/` directory
- Database queries logged in debug mode
- Performance metrics available via API

## 🎯 Next Steps

1. **Set up monitoring**: Configure application monitoring
2. **Backup strategy**: Implement automated backups
3. **CI/CD pipeline**: Set up automated deployments
4. **Custom domain**: Configure custom domain and SSL
5. **Advanced features**: Add custom AI models and integrations

---

## 🏁 Ready to Launch!

Your YouTube AI Content Creator is now production-ready. Start creating AI-powered content and tracking your monetization success!

**Quick Test:**
```bash
curl -X POST http://localhost:8000/api/v1/content-ideas \
  -H "Content-Type: application/json" \
  -d '{"title":"My First AI Video","category":"tutorial","priority":8}'
```

🚀 **Happy Creating!**