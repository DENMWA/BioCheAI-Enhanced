# BioCheAI Enhanced - Complete Multi-Omics Analysis Platform

## New Features Added

### 🔄 Auto-Fetching from Open Source Repositories
- **NCBI Integration**: Fetch sequences, genes, and literature
- **Ensembl API**: Access genome data and annotations  
- **UniProt**: Retrieve protein information
- **GenBank**: Access genetic sequence database
- **PubMed**: Fetch biomedical literature

### 🛡️ Enhanced AI Policing & Auto-Repair
- **Comprehensive Detection**: Data quality, bias, privacy, scientific accuracy
- **Automatic Repair**: Self-healing for medium/low severity issues
- **Compliance Scoring**: Real-time compliance monitoring
- **Manual Repair**: API endpoint for manual data repair

## API Endpoints

### Data Fetching
- `POST /api/data/fetch` - Fetch data from external repositories
- `GET /api/data/repositories` - List supported repositories

### Analysis & Repair  
- `POST /api/analysis/<id>/repair` - Manually repair analysis data
- `GET /api/analysis/<id>` - Get analysis details
- `GET /api/analyses` - List user analyses

## Usage Examples

### Fetch NCBI Data
```json
POST /api/data/fetch
{
  "repository": "ncbi",
  "params": {
    "term": "BRCA1 human",
    "db": "nucleotide",
    "retmax": 5
  }
}
```

### Fetch UniProt Data
```json
POST /api/data/fetch
{
  "repository": "uniprot", 
  "params": {
    "query": "gene:BRCA1 AND organism:9606",
    "format": "json",
    "size": 10
  }
}
```

### Repair Analysis Data
```json
POST /api/analysis/{analysis_id}/repair
```

## Installation

```bash
pip install -r requirements.txt
python app.py
```

## Features

✅ **AI Policing System** - Comprehensive quality control
✅ **Auto-Repair Engine** - Self-healing data validation  
✅ **Multi-Repository Fetching** - NCBI, Ensembl, UniProt, GenBank, PubMed
✅ **Real-time Compliance** - Continuous monitoring and scoring
✅ **RESTful API** - Complete API for all operations
✅ **User Management** - JWT authentication and authorization
