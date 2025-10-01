# Deployment Guide - Travel Cost Estimator

This guide provides step-by-step instructions for deploying the Travel Cost Estimator application to various platforms.

## 🚀 Frontend Deployment (Vercel)

### Prerequisites
- Vercel account
- GitHub repository with the project

### Steps
1. **Connect Repository**
   ```bash
   # Install Vercel CLI
   npm i -g vercel
   
   # Login to Vercel
   vercel login
   
   # Deploy from project root
   vercel
   ```

2. **Configure Build Settings**
   - Framework Preset: Vite
   - Build Command: `npm run build`
   - Output Directory: `dist`
   - Install Command: `npm install`

3. **Environment Variables** (Optional)
   ```
   VITE_API_URL=https://your-backend-url.com
   ```

### Alternative: Netlify
1. Connect GitHub repository
2. Build settings:
   - Build command: `npm run build`
   - Publish directory: `dist`
3. Deploy

## 🖥️ Backend Deployment (Railway)

### Prerequisites
- Railway account
- GitHub repository

### Steps
1. **Connect Repository**
   - Go to Railway dashboard
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository
   - Select the `backend` folder

2. **Configure Environment Variables**
   ```bash
   GROK_API_KEY=your_grok_api_key
   SERP_API_KEY=your_serp_api_key
   GOOGLE_MAPS_API_KEY=your_google_maps_api_key
   ```

3. **Deploy**
   - Railway will automatically detect the Python app
   - It will use the `Procfile` for deployment
   - The app will be available at the provided URL

### Alternative: Heroku
1. **Install Heroku CLI**
   ```bash
   # Install Heroku CLI
   # Follow instructions at https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **Deploy**
   ```bash
   cd backend
   
   # Login to Heroku
   heroku login
   
   # Create Heroku app
   heroku create your-app-name
   
   # Set environment variables
   heroku config:set GROK_API_KEY=your_key
   heroku config:set SERP_API_KEY=your_key
   heroku config:set GOOGLE_MAPS_API_KEY=your_key
   
   # Deploy
   git push heroku main
   ```

## 🐳 Docker Deployment

### Frontend Dockerfile
```dockerfile
# Frontend Dockerfile
FROM node:18-alpine

WORKDIR /app
COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=0 /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Backend Dockerfile
```dockerfile
# Backend Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose
```yaml
# docker-compose.yml
version: '3.8'

services:
  frontend:
    build: .
    ports:
      - "3000:80"
    depends_on:
      - backend

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - GROK_API_KEY=${GROK_API_KEY}
      - SERP_API_KEY=${SERP_API_KEY}
      - GOOGLE_MAPS_API_KEY=${GOOGLE_MAPS_API_KEY}
```

### Deploy with Docker
```bash
# Build and run
docker-compose up --build

# Or deploy to cloud
docker-compose -f docker-compose.prod.yml up -d
```

## ☁️ Cloud Platform Deployment

### AWS (Elastic Beanstalk)
1. **Install EB CLI**
   ```bash
   pip install awsebcli
   ```

2. **Initialize EB**
   ```bash
   cd backend
   eb init
   eb create production
   ```

3. **Deploy**
   ```bash
   eb deploy
   ```

### Google Cloud Platform
1. **Install gcloud CLI**
2. **Deploy to App Engine**
   ```bash
   cd backend
   gcloud app deploy
   ```

### Azure
1. **Install Azure CLI**
2. **Deploy to App Service**
   ```bash
   az webapp up --name your-app-name --resource-group your-rg
   ```

## 🔧 Production Configuration

### Environment Variables
```bash
# Required for production
GROK_API_KEY=your_production_grok_key
SERP_API_KEY=your_production_serp_key
GOOGLE_MAPS_API_KEY=your_production_maps_key

# Optional optimizations
API_TIMEOUT=60
AGENT_TIMEOUT=120
MAX_CONCURRENT_AGENTS=10
CACHE_TTL=7200
```

### Performance Optimizations
1. **Enable Caching**
   ```python
   # In backend/services/config.py
   CACHE_TTL = 7200  # 2 hours
   ```

2. **Database Connection Pooling**
   ```python
   # Add to requirements.txt
   asyncpg==0.29.0
   ```

3. **Rate Limiting**
   ```python
   # Add rate limiting middleware
   from slowapi import Limiter
   ```

### Security Considerations
1. **HTTPS Only**
   - Configure SSL certificates
   - Redirect HTTP to HTTPS

2. **CORS Configuration**
   ```python
   # In main.py
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["https://your-frontend-domain.com"],
       allow_credentials=True,
       allow_methods=["GET", "POST"],
       allow_headers=["*"],
   )
   ```

3. **API Key Security**
   - Store keys in environment variables
   - Use secret management services
   - Rotate keys regularly

## 📊 Monitoring and Logging

### Application Monitoring
1. **Health Checks**
   ```bash
   curl https://your-backend-url.com/health
   ```

2. **Logging Configuration**
   ```python
   import logging
   
   logging.basicConfig(
       level=logging.INFO,
       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
   )
   ```

3. **Error Tracking**
   - Integrate Sentry for error monitoring
   - Set up alerts for critical failures

### Performance Monitoring
1. **Response Time Tracking**
2. **Agent Performance Metrics**
3. **API Usage Analytics**

## 🔄 CI/CD Pipeline

### GitHub Actions
```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-node@v2
        with:
          node-version: '18'
      - run: npm install
      - run: npm run build
      - run: npm run deploy

  deploy-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - run: pip install -r backend/requirements.txt
      - run: cd backend && python -m pytest
      - run: cd backend && python main.py
```

## 🚨 Troubleshooting

### Common Issues

1. **CORS Errors**
   - Check CORS configuration in backend
   - Verify frontend URL in allowed origins

2. **API Key Issues**
   - Verify environment variables are set
   - Check API key permissions and quotas

3. **Build Failures**
   - Check Node.js and Python versions
   - Verify all dependencies are installed

4. **Performance Issues**
   - Monitor API response times
   - Check database connection limits
   - Optimize agent timeout settings

### Debug Mode
```bash
# Enable debug logging
export DEBUG=true
export LOG_LEVEL=debug

# Run with debug mode
python main.py --debug
```

## 📈 Scaling Considerations

### Horizontal Scaling
1. **Load Balancer**: Use nginx or cloud load balancer
2. **Multiple Instances**: Deploy multiple backend instances
3. **Database Scaling**: Use managed database services

### Vertical Scaling
1. **Increase Resources**: More CPU/memory for agents
2. **Optimize Code**: Profile and optimize slow operations
3. **Caching**: Implement Redis for response caching

---

**Ready to deploy your AI-powered travel planning system! 🚀**
