# BioCheAI Enhanced - Deployment & Launch Guide

## 🚀 Quick Start (Local Development)

### Prerequisites
- Python 3.8+ (recommended: Python 3.12)
- Git
- 4GB+ RAM (8GB+ recommended for AI features)
- Internet connection (for data fetching from external repositories)

### 1. Clone and Setup
```bash
# Clone the repository
git clone <your-repo-url>
cd biocheai-enhanced

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Launch Application
```bash
# Start the BioCheAI Enhanced platform
python run.py
```

The application will be available at `http://localhost:5000` with:
- 🔗 API endpoints at `/api/*`
- 📚 Documentation at `/api/data/repositories`
- 🌐 WebSocket support for real-time collaboration
- 🧠 AI-powered features ready

### 3. Test the Installation
```bash
# Run core features test
python test_new_features.py

# Run advanced features test
python test_advanced_features.py
```

## 🏗️ Production Deployment Options

### Option 1: Docker Deployment (Recommended)

#### Create Dockerfile
```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 biocheai && chown -R biocheai:biocheai /app
USER biocheai

# Expose port
EXPOSE 5000

# Start application
CMD ["python", "run.py"]
```

#### Build and Run
```bash
# Build Docker image
docker build -t biocheai-enhanced .

# Run container
docker run -d \
  --name biocheai \
  -p 5000:5000 \
  -e FLASK_ENV=production \
  biocheai-enhanced
```

### Option 2: Cloud Deployment

#### AWS Deployment (Using ECS)
```bash
# Install AWS CLI and configure credentials
aws configure

# Create ECR repository
aws ecr create-repository --repository-name biocheai-enhanced

# Build and push Docker image
docker build -t biocheai-enhanced .
docker tag biocheai-enhanced:latest <account-id>.dkr.ecr.<region>.amazonaws.com/biocheai-enhanced:latest
docker push <account-id>.dkr.ecr.<region>.amazonaws.com/biocheai-enhanced:latest

# Deploy using ECS (create task definition and service)
```

#### Google Cloud Platform (Cloud Run)
```bash
# Install gcloud CLI and authenticate
gcloud auth login

# Build and deploy
gcloud builds submit --tag gcr.io/<project-id>/biocheai-enhanced
gcloud run deploy biocheai-enhanced \
  --image gcr.io/<project-id>/biocheai-enhanced \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 5000
```

#### Azure Container Instances
```bash
# Install Azure CLI and login
az login

# Create resource group
az group create --name biocheai-rg --location eastus

# Deploy container
az container create \
  --resource-group biocheai-rg \
  --name biocheai-enhanced \
  --image biocheai-enhanced:latest \
  --ports 5000 \
  --dns-name-label biocheai-app
```

### Option 3: Traditional Server Deployment

#### Using Gunicorn (Production WSGI Server)
```bash
# Install Gunicorn
pip install gunicorn eventlet

# Create gunicorn configuration
cat > gunicorn.conf.py << EOF
bind = "0.0.0.0:5000"
workers = 4
worker_class = "eventlet"
worker_connections = 1000
timeout = 120
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
EOF

# Start with Gunicorn
gunicorn --config gunicorn.conf.py app:app
```

#### Using Nginx Reverse Proxy
```nginx
# /etc/nginx/sites-available/biocheai
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket support for real-time collaboration
    location /socket.io/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## ⚙️ Environment Configuration

### Environment Variables
```bash
# Create .env file
cat > .env << EOF
# Flask Configuration
FLASK_ENV=production
SECRET_KEY=your-super-secret-key-here
DATABASE_URL=sqlite:///biocheai.db

# JWT Configuration
JWT_SECRET_KEY=your-jwt-secret-key

# Redis Configuration (for real-time features)
REDIS_URL=redis://localhost:6379/0

# Cloud Provider Credentials (optional)
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
GCP_PROJECT_ID=your-gcp-project
AZURE_STORAGE_CONNECTION_STRING=your-azure-connection

# External API Keys (optional)
NCBI_API_KEY=your-ncbi-api-key
PUBMED_API_KEY=your-pubmed-api-key
EOF
```

### Database Configuration

#### SQLite (Default - Development)
```python
# Already configured in app.py
DATABASE_URL = 'sqlite:///biocheai.db'
```

#### PostgreSQL (Production Recommended)
```bash
# Install PostgreSQL adapter
pip install psycopg2-binary

# Update DATABASE_URL in .env
DATABASE_URL=postgresql://username:password@localhost:5432/biocheai
```

#### MySQL (Alternative)
```bash
# Install MySQL adapter
pip install PyMySQL

# Update DATABASE_URL in .env
DATABASE_URL=mysql+pymysql://username:password@localhost:3306/biocheai
```

## 🔧 Advanced Configuration

### Redis Setup (For Real-time Features)
```bash
# Install Redis
sudo apt-get install redis-server  # Ubuntu/Debian
brew install redis                  # macOS

# Start Redis
redis-server

# Test Redis connection
redis-cli ping
```

### Celery Setup (For Background Tasks)
```bash
# Start Celery worker (in separate terminal)
celery -A app.celery worker --loglevel=info

# Start Celery beat (for scheduled tasks)
celery -A app.celery beat --loglevel=info
```

### SSL/HTTPS Configuration
```bash
# Generate SSL certificate (Let's Encrypt)
sudo certbot --nginx -d your-domain.com

# Or use self-signed certificate for testing
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes
```

## 📊 Monitoring & Logging

### Application Monitoring
```python
# Add to app.py for production monitoring
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    file_handler = RotatingFileHandler('logs/biocheai.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
```

### Health Check Endpoint
```python
# Already included in app.py
@app.route('/health')
def health_check():
    return {'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()}
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Import Errors
```bash
# Solution: Install missing dependencies
pip install -r requirements.txt

# For NLP models warning:
pip install tf-keras
```

#### 2. Database Connection Issues
```bash
# Reset database
rm -f instance/database.db
python run.py  # Will recreate tables
```

#### 3. Port Already in Use
```bash
# Find process using port 5000
lsof -i :5000

# Kill process
kill -9 <PID>
```

#### 4. Memory Issues with AI Models
```bash
# Reduce TensorFlow memory usage
export TF_FORCE_GPU_ALLOW_GROWTH=true
export TF_CPP_MIN_LOG_LEVEL=2
```

#### 5. WebSocket Connection Issues
```bash
# Check if eventlet is installed
pip install eventlet

# Verify Redis is running
redis-cli ping
```

### Performance Optimization

#### 1. Database Optimization
```sql
-- Create indexes for better performance
CREATE INDEX idx_analysis_user_id ON analysis(user_id);
CREATE INDEX idx_analysis_created_at ON analysis(created_at);
CREATE INDEX idx_project_owner_id ON project(owner_id);
```

#### 2. Caching Configuration
```python
# Add Redis caching for API responses
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'redis'})

@cache.cached(timeout=300)
def expensive_operation():
    # Cached for 5 minutes
    pass
```

## 🔐 Security Considerations

### Production Security Checklist
- [ ] Change default SECRET_KEY and JWT_SECRET_KEY
- [ ] Enable HTTPS/SSL certificates
- [ ] Configure proper CORS settings
- [ ] Set up rate limiting (already included)
- [ ] Enable database connection encryption
- [ ] Configure firewall rules
- [ ] Set up monitoring and alerting
- [ ] Regular security updates
- [ ] Backup strategy implementation

### API Security
```python
# Already implemented in app.py:
# - JWT authentication
# - Rate limiting
# - Input validation
# - SQL injection protection (SQLAlchemy ORM)
# - XSS protection (Flask built-in)
```

## 📈 Scaling Considerations

### Horizontal Scaling
```yaml
# docker-compose.yml for multi-instance deployment
version: '3.8'
services:
  biocheai:
    build: .
    ports:
      - "5000-5002:5000"
    environment:
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis
      - postgres
    deploy:
      replicas: 3

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"

  postgres:
    image: postgres:13
    environment:
      POSTGRES_DB: biocheai
      POSTGRES_USER: biocheai
      POSTGRES_PASSWORD: secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### Load Balancing
```nginx
# Nginx load balancer configuration
upstream biocheai_backend {
    server 127.0.0.1:5000;
    server 127.0.0.1:5001;
    server 127.0.0.1:5002;
}

server {
    listen 80;
    location / {
        proxy_pass http://biocheai_backend;
    }
}
```

## 🎯 Feature-Specific Deployment Notes

### AI Literature Intelligence
- Requires internet access for PubMed/NCBI APIs
- Downloads transformer models on first use (~500MB)
- Consider pre-downloading models in Docker image

### Real-time Collaboration
- Requires Redis for WebSocket session management
- Configure sticky sessions for load balancing
- Monitor WebSocket connection limits

### Cloud Scalability
- Configure cloud provider credentials
- Set up auto-scaling policies
- Monitor cloud resource usage and costs

### Regulatory Compliance
- Ensure data encryption at rest and in transit
- Configure audit logging
- Set up compliance monitoring dashboards

BioCheAI Enhanced is now ready for deployment across any environment from local development to enterprise-scale production! 🚀
