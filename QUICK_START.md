# BioCheAI Enhanced - Quick Start Guide

## 🚀 Get Started in 3 Minutes

### Step 1: Install & Launch
```bash
# Clone and setup
git clone <your-repo-url>
cd biocheai-enhanced

# Install dependencies
pip install -r requirements.txt

# Launch the platform
python run.py
```

### Step 2: Test the Platform
```bash
# Run comprehensive tests
python test_new_features.py
python test_advanced_features.py
```

### Step 3: Access the Platform
- **API Base**: `http://localhost:5000/api`
- **Health Check**: `http://localhost:5000/health`
- **Documentation**: `http://localhost:5000/api/data/repositories`

## 🧪 Quick API Test

### 1. Register User
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "researcher",
    "email": "researcher@university.edu",
    "password": "secure123",
    "first_name": "Research",
    "last_name": "Scientist"
  }'
```

### 2. Login & Get Token
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "researcher",
    "password": "secure123"
  }'
```

### 3. Fetch Data from NCBI
```bash
curl -X POST http://localhost:5000/api/data/fetch \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "repository": "ncbi",
    "params": {
      "term": "insulin human",
      "db": "protein",
      "retmax": 5
    }
  }'
```

### 4. Create Analysis with AI Policing
```bash
curl -X POST http://localhost:5000/api/analysis \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "analysis_type": "protein",
    "title": "Insulin Analysis",
    "data": {
      "sequence": "MALWMRLLPLLALLALWGPDPAAAFVNQHLCGSHLVEALYLVCGERGFFYTPKTRREAEDLQVGQVELGGGPGAGSLQPLALEGSLQKRGIVEQCCTSICSLYQLENYCN",
      "samples": 100
    }
  }'
```

## 🎯 Key Features to Try

### 📚 AI Literature Intelligence
```bash
# Search literature
curl -X POST http://localhost:5000/api/literature/search \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"query": "CRISPR gene editing", "max_results": 10}'
```

### 👥 Collaboration
```bash
# Create project
curl -X POST http://localhost:5000/api/projects \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"name": "Cancer Research", "description": "Multi-omics analysis"}'
```

### 🔧 Workflow Builder
```bash
# Get templates
curl -X GET http://localhost:5000/api/workflow-templates \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 📋 Compliance Check
```bash
# Get frameworks
curl -X GET http://localhost:5000/api/compliance/frameworks \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🔍 What You'll See

### ✅ Successful Launch Output
```
🚀 Starting BioCheAI Enhanced Platform
==================================================
✅ Database tables created
🌐 Starting Flask server with SocketIO...
📡 Data fetching from NCBI, Ensembl, UniProt, GenBank, PubMed enabled
🛡️ AI Policing and Auto-Repair systems active
🧠 AI Literature Intelligence with NLP models
👥 Real-time Collaboration with WebSocket support
🔧 No-Code Workflow Builder
🔗 Multi-Modal Data Integration
📋 Regulatory Compliance (GDPR, HIPAA, FDA, EMA)
☁️ Cloud Scalability (AWS, GCP, Azure)
```

### ✅ Successful Test Output
```
🚀 BioCheAI Enhanced Features Test Suite
==================================================
🔐 Testing user registration and login...
✅ User registration successful
📡 Testing data fetching...
✅ NCBI data fetching successful
   Found 2 sequences
🧬 Testing analysis with AI policing and repair...
✅ Analysis created: <analysis-id>
   Police status: clean
   Compliance score: 1.00
🎉 All tests completed!
```

## 🚨 Troubleshooting

### Common Issues & Solutions

#### Port 5000 in use?
```bash
# Kill existing process
lsof -i :5000
kill -9 <PID>
```

#### Missing dependencies?
```bash
# Reinstall requirements
pip install --upgrade -r requirements.txt
```

#### Database issues?
```bash
# Reset database
rm -f instance/database.db
python run.py
```

#### NLP model warnings?
```bash
# Install tf-keras for transformer models
pip install tf-keras
```

## 🎉 You're Ready!

BioCheAI Enhanced is now running with:
- **6 Advanced Feature Categories** fully operational
- **50+ API Endpoints** ready for use
- **Real-time Collaboration** via WebSocket
- **AI-Powered Analysis** with auto-repair
- **Multi-Modal Data Integration** capabilities
- **Regulatory Compliance** built-in

Start building the future of life sciences research! 🧬🚀
</quick_start>
