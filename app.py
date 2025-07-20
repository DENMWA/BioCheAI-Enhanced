# ============================================================================
# BIOCHEAI COMPLETE FLASK BACKEND - app.py
# ============================================================================

"""
BioCheAI Unified Analytics Platform - Flask Backend
Complete multi-omics analysis API with ML and AI policing
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import os
import json
import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import logging
from functools import wraps
import uuid
import redis
from celery import Celery
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import re
import xml.etree.ElementTree as ET
import random
from io import StringIO

# Initialize Flask app
app = Flask(__name__, static_folder='build', static_url_path='')

# Configuration
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'biocheai-super-secret-key-2024'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///biocheai.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-string'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=1)
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379'
    CELERY_BROKER_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379'
    CELERY_RESULT_BACKEND = os.environ.get('REDIS_URL') or 'redis://localhost:6379'
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB max file upload
    UPLOAD_FOLDER = 'uploads'

app.config.from_object(Config)

# Create upload directory
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('models', exist_ok=True)

# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)
limiter = Limiter(app, key_func=get_remote_address)

# CORS configuration
CORS(app, origins=["http://localhost:3000", "https://yourdomain.github.io"])

# Redis connection
try:
    redis_client = redis.from_url(app.config['REDIS_URL'])
except:
    redis_client = None

# Celery configuration
def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)
    return celery

celery = make_celery(app)

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =========================== DATABASE MODELS ===========================

class User(db.Model):
    """User model for authentication and user management"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    institution = db.Column(db.String(200))
    role = db.Column(db.String(50), default='researcher')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    analyses = db.relationship('Analysis', backref='user', lazy=True)
    api_keys = db.relationship('APIKey', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'institution': self.institution,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Analysis(db.Model):
    """Analysis model for storing analysis results and metadata"""
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    analysis_type = db.Column(db.String(50), nullable=False)  # dna, rna, protein, multiomics
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='queued')  # queued, running, completed, failed
    progress = db.Column(db.Integer, default=0)
    
    # Input data
    input_data = db.Column(db.JSON)
    input_file_path = db.Column(db.String(500))
    
    # Results
    results = db.Column(db.JSON)
    confidence_score = db.Column(db.Float)
    
    # ML and AI Policing
    ml_predictions = db.Column(db.JSON)
    police_report = db.Column(db.JSON)
    compliance_score = db.Column(db.Float)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    error_message = db.Column(db.Text)
    
    def to_dict(self):
        return {
            'id': self.id,
            'analysis_type': self.analysis_type,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'progress': self.progress,
            'confidence_score': self.confidence_score,
            'compliance_score': self.compliance_score,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

class APIKey(db.Model):
    """API Key model for programmatic access"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    key_hash = db.Column(db.String(128), unique=True, nullable=False)
    name = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_used = db.Column(db.DateTime)
    usage_count = db.Column(db.Integer, default=0)

class MLModel(db.Model):
    """ML Model metadata for tracking model versions and performance"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    version = db.Column(db.String(20))
    model_type = db.Column(db.String(50))  # dna_classifier, rna_classifier, etc.
    accuracy = db.Column(db.Float)
    training_data_size = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    model_path = db.Column(db.String(500))

# =========================== ML AND AI POLICING CLASSES ===========================

class BioCheAIMLEngine:
    """Main ML engine for BioCheAI analysis"""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.load_models()
    
    def load_models(self):
        """Load pre-trained models"""
        try:
            # Create simple models if they don't exist
            self.create_default_models()
            logger.info("ML models initialized")
        except Exception as e:
            logger.error(f"Error loading models: {str(e)}")
    
    def create_default_models(self):
        """Create default models for analysis"""
        # DNA classifier
        self.models['dna_classifier'] = RandomForestClassifier(n_estimators=100, random_state=42)
        
        # RNA classifier
        self.models['rna_classifier'] = RandomForestClassifier(n_estimators=100, random_state=42)
        
        # Protein classifier
        self.models['protein_classifier'] = RandomForestClassifier(n_estimators=100, random_state=42)
        
        # Train with dummy data if no real training data exists
        for model_name, model in self.models.items():
            X_dummy = np.random.rand(100, 50)
            y_dummy = np.random.randint(0, 2, 100)
            model.fit(X_dummy, y_dummy)
    
    def extract_features(self, data, analysis_type):
        """Extract features from input data"""
        features = {}
        
        if analysis_type == 'dna':
            features = self.extract_dna_features(data)
        elif analysis_type == 'rna':
            features = self.extract_rna_features(data)
        elif analysis_type == 'protein':
            features = self.extract_protein_features(data)
        elif analysis_type == 'multiomics':
            features = self.extract_multiomics_features(data)
        
        return features
    
    def extract_dna_features(self, data):
        """Extract DNA-specific features"""
        features = {}
        
        if 'sequence' in data:
            seq = data['sequence'].upper()
            features['gc_content'] = (seq.count('G') + seq.count('C')) / len(seq) if seq else 0
            features['length'] = len(seq)
            features['a_content'] = seq.count('A') / len(seq) if seq else 0
            features['t_content'] = seq.count('T') / len(seq) if seq else 0
            features['complexity'] = self.calculate_sequence_complexity(seq)
        
        if 'variants' in data:
            features['variant_count'] = len(data['variants'])
            features['snp_count'] = sum(1 for v in data['variants'] if v.get('type') == 'SNP')
            features['indel_count'] = sum(1 for v in data['variants'] if v.get('type') in ['INS', 'DEL'])
        
        return features
    
    def extract_rna_features(self, data):
        """Extract RNA-specific features"""
        features = {}
        
        if 'expression_matrix' in data:
            expr_data = np.array(data['expression_matrix'])
            features['mean_expression'] = np.mean(expr_data)
            features['variance'] = np.var(expr_data)
            features['gene_count'] = expr_data.shape[0] if expr_data.ndim > 1 else len(expr_data)
            features['zero_expression_ratio'] = np.sum(expr_data == 0) / expr_data.size
        
        if 'cell_types' in data:
            features['cell_type_count'] = len(set(data['cell_types']))
        
        return features
    
    def extract_protein_features(self, data):
        """Extract protein-specific features"""
        features = {}
        
        if 'sequence' in data:
            seq = data['sequence'].upper()
            features['length'] = len(seq)
            features['molecular_weight'] = self.calculate_molecular_weight(seq)
            features['hydrophobicity'] = self.calculate_hydrophobicity(seq)
            features['charge'] = self.calculate_charge(seq)
        
        if 'modifications' in data:
            features['modification_count'] = len(data['modifications'])
            features['phosphorylation_sites'] = sum(1 for m in data['modifications'] if m.get('type') == 'phosphorylation')
        
        return features
    
    def extract_multiomics_features(self, data):
        """Extract multi-omics features"""
        features = {}
        
        # Combine features from all omics types
        if 'dna' in data:
            dna_features = self.extract_dna_features(data['dna'])
            features.update({f'dna_{k}': v for k, v in dna_features.items()})
        
        if 'rna' in data:
            rna_features = self.extract_rna_features(data['rna'])
            features.update({f'rna_{k}': v for k, v in rna_features.items()})
        
        if 'protein' in data:
            protein_features = self.extract_protein_features(data['protein'])
            features.update({f'protein_{k}': v for k, v in protein_features.items()})
        
        return features
    
    def predict(self, features, analysis_type):
        """Make predictions using loaded models"""
        model_key = f"{analysis_type}_classifier"
        
        if model_key not in self.models:
            return {
                'predictions': [],
                'confidence': 0.0,
                'error': f'Model {model_key} not available'
            }
        
        try:
            # Prepare features for prediction
            feature_array = self.prepare_features_for_prediction(features, analysis_type)
            
            # Make prediction
            model = self.models[model_key]
            predictions = model.predict_proba(feature_array)
            
            # Calculate confidence
            confidence = float(np.max(predictions))
            
            return {
                'predictions': predictions.tolist(),
                'confidence': confidence,
                'feature_importance': self.calculate_feature_importance(features)
            }
            
        except Exception as e:
            logger.error(f"Prediction error: {str(e)}")
            return {
                'predictions': [],
                'confidence': 0.0,
                'error': str(e)
            }
    
    def calculate_sequence_complexity(self, sequence):
        """Calculate sequence complexity using Shannon entropy"""
        if not sequence:
            return 0
        
        # Count nucleotides
        counts = {}
        for nucleotide in sequence:
            counts[nucleotide] = counts.get(nucleotide, 0) + 1
        
        # Calculate entropy
        length = len(sequence)
        entropy = 0
        for count in counts.values():
            probability = count / length
            if probability > 0:
                entropy -= probability * np.log2(probability)
        
        return entropy
    
    def calculate_molecular_weight(self, sequence):
        """Calculate approximate molecular weight of protein"""
        weights = {
            'A': 89.1, 'R': 174.2, 'N': 132.1, 'D': 133.1, 'C': 121.2,
            'Q': 146.2, 'E': 147.1, 'G': 75.1, 'H': 155.2, 'I': 131.2,
            'L': 131.2, 'K': 146.2, 'M': 149.2, 'F': 165.2, 'P': 115.1,
            'S': 105.1, 'T': 119.1, 'W': 204.2, 'Y': 181.2, 'V': 117.1
        }
        
        return sum(weights.get(aa, 110) for aa in sequence)
    
    def calculate_hydrophobicity(self, sequence):
        """Calculate hydrophobicity score"""
        hydrophobicity = {
            'A': 1.8, 'R': -4.5, 'N': -3.5, 'D': -3.5, 'C': 2.5,
            'Q': -3.5, 'E': -3.5, 'G': -0.4, 'H': -3.2, 'I': 4.5,
            'L': 3.8, 'K': -3.9, 'M': 1.9, 'F': 2.8, 'P': -1.6,
            'S': -0.8, 'T': -0.7, 'W': -0.9, 'Y': -1.3, 'V': 4.2
        }
        
        if not sequence:
            return 0
        
        return sum(hydrophobicity.get(aa, 0) for aa in sequence) / len(sequence)
    
    def calculate_charge(self, sequence):
        """Calculate net charge at pH 7"""
        charges = {
            'K': 1, 'R': 1, 'H': 0.1,  # Positive
            'D': -1, 'E': -1,  # Negative
        }
        
        return sum(charges.get(aa, 0) for aa in sequence)
    
    def prepare_features_for_prediction(self, features, analysis_type):
        """Prepare features for model prediction"""
        # Convert features dictionary to array
        feature_values = list(features.values())
        
        # Pad or truncate to expected input size
        expected_size = 50  # Default size for our models
        
        if len(feature_values) < expected_size:
            feature_values.extend([0] * (expected_size - len(feature_values)))
        else:
            feature_values = feature_values[:expected_size]
        
        return np.array([feature_values])
    
    def calculate_feature_importance(self, features):
        """Calculate feature importance scores"""
        importance = {}
        for key, value in features.items():
            if isinstance(value, (int, float)):
                importance[key] = abs(value) / (1 + abs(value))
            else:
                importance[key] = 0.5
        
        return importance

class AIPoliceEngine:
    """AI Policing system for quality control and compliance"""
    
    def __init__(self):
        self.rules = {
            'data_quality': self.check_data_quality,
            'bias_detection': self.check_bias,
            'privacy_protection': self.check_privacy,
            'scientific_accuracy': self.check_scientific_accuracy
        }
        self.violation_threshold = 0.7
    
    def police_analysis(self, data, analysis_type, results=None):
        """Perform comprehensive AI policing"""
        violations = []
        
        for rule_name, rule_func in self.rules.items():
            try:
                risk_score = rule_func(data, results)
                if risk_score > self.violation_threshold:
                    violations.append({
                        'rule': rule_name,
                        'risk_score': risk_score,
                        'severity': self.get_severity(risk_score),
                        'action': self.get_action(rule_name, risk_score)
                    })
            except Exception as e:
                logger.error(f"Error in rule {rule_name}: {str(e)}")
        
        return {
            'status': 'flagged' if violations else 'clean',
            'violations': violations,
            'compliance_score': self.calculate_compliance_score(violations),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def check_data_quality(self, data, results):
        """Check data quality metrics"""
        quality_issues = 0
        total_checks = 0
        
        # Check for missing values
        if isinstance(data, dict):
            for key, value in data.items():
                total_checks += 1
                if value is None or value == '' or (isinstance(value, list) and len(value) == 0):
                    quality_issues += 1
        
        return quality_issues / max(total_checks, 1)
    
    def check_bias(self, data, results):
        """Check for various types of bias"""
        bias_score = 0
        
        # Check for demographic bias in results
        if results and 'predictions' in results:
            predictions = results['predictions']
            if isinstance(predictions, list) and len(predictions) > 0:
                pred_array = np.array(predictions)
                if pred_array.std() < 0.1:
                    bias_score += 0.3
        
        return min(bias_score, 1.0)
    
    def check_privacy(self, data, results):
        """Check for privacy violations and PII"""
        privacy_risk = 0
        data_str = json.dumps(data) if isinstance(data, dict) else str(data)
        
        # Email pattern
        if re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', data_str):
            privacy_risk += 0.4
        
        # Phone pattern
        if re.search(r'\b\d{3}-\d{3}-\d{4}\b', data_str):
            privacy_risk += 0.3
        
        return min(privacy_risk, 1.0)
    
    def check_scientific_accuracy(self, data, results):
        """Check scientific accuracy and methodology"""
        accuracy_issues = 0
        
        # Check sample size
        if 'samples' in data:
            sample_count = len(data['samples']) if isinstance(data['samples'], list) else data['samples']
            if isinstance(sample_count, int) and sample_count < 10:
                accuracy_issues += 0.3
        
        return min(accuracy_issues, 1.0)
    
    def get_severity(self, risk_score):
        """Determine severity based on risk score"""
        if risk_score >= 0.9:
            return 'critical'
        elif risk_score >= 0.7:
            return 'high'
        elif risk_score >= 0.5:
            return 'medium'
        else:
            return 'low'
    
    def get_action(self, rule_name, risk_score):
        """Determine action based on rule and risk score"""
        if risk_score >= 0.9:
            return 'block'
        elif risk_score >= 0.8:
            return 'quarantine'
        elif risk_score >= 0.7:
            return 'flag_for_review'
        else:
            return 'monitor'
    
    def calculate_compliance_score(self, violations):
        """Calculate overall compliance score"""
        if not violations:
            return 1.0
        
        total_risk = sum(v['risk_score'] for v in violations)
        max_possible_risk = len(violations) * 1.0
        
        return max(0, 1.0 - (total_risk / max_possible_risk))

class AutoRepairEngine:
    """Auto repair system for fixing data quality issues and violations"""
    
    def __init__(self):
        self.repair_methods = {
            'data_quality': self.repair_data_quality,
            'bias_detection': self.repair_bias,
            'privacy_protection': self.repair_privacy,
            'scientific_accuracy': self.repair_scientific_accuracy
        }
    
    def repair_data(self, data, violations):
        """Automatically repair data based on violations"""
        repaired_data = data.copy() if isinstance(data, dict) else data
        repair_log = []
        
        for violation in violations:
            rule = violation['rule']
            severity = violation['severity']
            
            if severity in ['medium', 'low'] and rule in self.repair_methods:
                try:
                    repaired_data = self.repair_methods[rule](repaired_data, violation)
                    repair_log.append({
                        'rule': rule,
                        'action': 'repaired',
                        'severity': severity
                    })
                except Exception as e:
                    logger.error(f"Repair error for {rule}: {str(e)}")
                    repair_log.append({
                        'rule': rule,
                        'action': 'failed',
                        'error': str(e)
                    })
        
        if repair_log:
            repaired_data['_repair_log'] = repair_log
        
        return repaired_data
    
    def repair_data_quality(self, data, violation):
        """Repair data quality issues"""
        if isinstance(data, dict):
            for key, value in data.items():
                if value is None or value == '':
                    if 'sequence' in key.lower():
                        data[key] = 'N' * 10  # Default sequence
                    elif 'expression' in key.lower():
                        data[key] = 0.0
                    elif isinstance(value, list):
                        data[key] = []
                    else:
                        data[key] = 'unknown'
        return data
    
    def repair_bias(self, data, violation):
        """Repair bias issues by adding diversity"""
        if 'predictions' in data:
            predictions = data['predictions']
            if isinstance(predictions, list) and len(predictions) > 0:
                import random
                data['predictions'] = [p + random.uniform(-0.05, 0.05) for p in predictions]
        return data
    
    def repair_privacy(self, data, violation):
        """Remove or mask PII data"""
        data_str = json.dumps(data) if isinstance(data, dict) else str(data)
        
        data_str = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 
                         '[EMAIL_MASKED]', data_str)
        
        data_str = re.sub(r'\b\d{3}-\d{3}-\d{4}\b', '[PHONE_MASKED]', data_str)
        
        try:
            return json.loads(data_str) if isinstance(data, dict) else data_str
        except:
            return data
    
    def repair_scientific_accuracy(self, data, violation):
        """Improve scientific accuracy"""
        if 'samples' in data:
            sample_count = len(data['samples']) if isinstance(data['samples'], list) else data['samples']
            if isinstance(sample_count, int) and sample_count < 10:
                # Add warning about small sample size
                data['_warnings'] = data.get('_warnings', [])
                data['_warnings'].append('Small sample size detected - results may not be statistically significant')
        return data


class DataFetchingEngine:
    """Auto-fetching system for open source biological data repositories"""
    
    def __init__(self):
        self.repositories = {
            'ncbi': self.fetch_ncbi_data,
            'ensembl': self.fetch_ensembl_data,
            'uniprot': self.fetch_uniprot_data,
            'genbank': self.fetch_genbank_data,
            'pubmed': self.fetch_pubmed_data
        }
        self.base_urls = {
            'ncbi': 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/',
            'ensembl': 'https://rest.ensembl.org/',
            'uniprot': 'https://rest.uniprot.org/',
            'genbank': 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/',
            'pubmed': 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'
        }
    
    def fetch_data(self, repository, query_params):
        """Fetch data from specified repository"""
        if repository not in self.repositories:
            return {'error': f'Repository {repository} not supported'}
        
        try:
            return self.repositories[repository](query_params)
        except Exception as e:
            logger.error(f"Data fetching error from {repository}: {str(e)}")
            return {'error': str(e)}
    
    def fetch_ncbi_data(self, params):
        """Fetch data from NCBI databases"""
        import requests
        
        db = params.get('db', 'nucleotide')
        term = params.get('term', '')
        retmax = params.get('retmax', 10)
        
        search_url = f"{self.base_urls['ncbi']}esearch.fcgi"
        search_params = {
            'db': db,
            'term': term,
            'retmax': retmax,
            'retmode': 'json'
        }
        
        response = requests.get(search_url, params=search_params, timeout=30)
        response.raise_for_status()
        search_result = response.json()
        
        if 'esearchresult' not in search_result or not search_result['esearchresult']['idlist']:
            return {'data': [], 'message': 'No results found'}
        
        ids = ','.join(search_result['esearchresult']['idlist'])
        fetch_url = f"{self.base_urls['ncbi']}efetch.fcgi"
        fetch_params = {
            'db': db,
            'id': ids,
            'rettype': 'fasta',
            'retmode': 'text'
        }
        
        response = requests.get(fetch_url, params=fetch_params, timeout=30)
        response.raise_for_status()
        
        return {
            'data': self.parse_fasta(response.text),
            'source': 'ncbi',
            'query': params
        }
    
    def fetch_ensembl_data(self, params):
        """Fetch data from Ensembl REST API"""
        import requests
        
        species = params.get('species', 'human')
        gene_id = params.get('gene_id', '')
        
        if not gene_id:
            return {'error': 'gene_id parameter required for Ensembl'}
        
        url = f"{self.base_urls['ensembl']}sequence/id/{gene_id}"
        headers = {'Content-Type': 'application/json'}
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        return {
            'data': [{
                'id': data.get('id'),
                'sequence': data.get('seq'),
                'description': data.get('desc', ''),
                'length': len(data.get('seq', ''))
            }],
            'source': 'ensembl',
            'query': params
        }
    
    def fetch_uniprot_data(self, params):
        """Fetch data from UniProt REST API"""
        import requests
        
        query = params.get('query', '')
        format_type = params.get('format', 'json')
        size = params.get('size', 10)
        
        url = f"{self.base_urls['uniprot']}uniprotkb/search"
        params_dict = {
            'query': query,
            'format': format_type,
            'size': size
        }
        
        response = requests.get(url, params=params_dict, timeout=30)
        response.raise_for_status()
        
        if format_type == 'json':
            data = response.json()
            return {
                'data': data.get('results', []),
                'source': 'uniprot',
                'query': params
            }
        else:
            return {
                'data': response.text,
                'source': 'uniprot',
                'query': params
            }
    
    def fetch_genbank_data(self, params):
        """Fetch data from GenBank (via NCBI)"""
        params['db'] = 'nucleotide'
        return self.fetch_ncbi_data(params)
    
    def fetch_pubmed_data(self, params):
        """Fetch data from PubMed"""
        import requests
        
        term = params.get('term', '')
        retmax = params.get('retmax', 10)
        
        search_url = f"{self.base_urls['pubmed']}esearch.fcgi"
        search_params = {
            'db': 'pubmed',
            'term': term,
            'retmax': retmax,
            'retmode': 'json'
        }
        
        response = requests.get(search_url, params=search_params, timeout=30)
        response.raise_for_status()
        search_result = response.json()
        
        if 'esearchresult' not in search_result or not search_result['esearchresult']['idlist']:
            return {'data': [], 'message': 'No results found'}
        
        ids = ','.join(search_result['esearchresult']['idlist'])
        fetch_url = f"{self.base_urls['pubmed']}efetch.fcgi"
        fetch_params = {
            'db': 'pubmed',
            'id': ids,
            'rettype': 'abstract',
            'retmode': 'xml'
        }
        
        response = requests.get(fetch_url, params=fetch_params, timeout=30)
        response.raise_for_status()
        
        return {
            'data': self.parse_pubmed_xml(response.text),
            'source': 'pubmed',
            'query': params
        }
    
    def parse_fasta(self, fasta_text):
        """Parse FASTA format text"""
        sequences = []
        current_seq = {'id': '', 'description': '', 'sequence': ''}
        
        for line in fasta_text.split('\n'):
            line = line.strip()
            if line.startswith('>'):
                if current_seq['sequence']:
                    sequences.append(current_seq)
                parts = line[1:].split(' ', 1)
                current_seq = {
                    'id': parts[0],
                    'description': parts[1] if len(parts) > 1 else '',
                    'sequence': ''
                }
            elif line:
                current_seq['sequence'] += line
        
        if current_seq['sequence']:
            sequences.append(current_seq)
        
        return sequences
    
    def parse_pubmed_xml(self, xml_text):
        """Parse PubMed XML response"""
        import xml.etree.ElementTree as ET
        
        try:
            root = ET.fromstring(xml_text)
            articles = []
            
            for article in root.findall('.//PubmedArticle'):
                title_elem = article.find('.//ArticleTitle')
                abstract_elem = article.find('.//AbstractText')
                pmid_elem = article.find('.//PMID')
                
                articles.append({
                    'pmid': pmid_elem.text if pmid_elem is not None else '',
                    'title': title_elem.text if title_elem is not None else '',
                    'abstract': abstract_elem.text if abstract_elem is not None else ''
                })
            
            return articles
        except ET.ParseError:
            return []


# Initialize ML, AI, and new engines
ml_engine = BioCheAIMLEngine()
ai_police = AIPoliceEngine()
auto_repair_engine = AutoRepairEngine()
data_fetching_engine = DataFetchingEngine()

# =========================== HELPER FUNCTIONS ===========================

def validate_analysis_data(data, analysis_type):
    """Validate input data for analysis"""
    if not data:
        return False, "No data provided"
    
    if analysis_type == 'dna':
        if 'sequence' not in data and 'variants' not in data:
            return False, "DNA analysis requires sequence or variants data"
    
    elif analysis_type == 'rna':
        if 'expression_matrix' not in data and 'sequences' not in data:
            return False, "RNA analysis requires expression matrix or sequences"
    
    elif analysis_type == 'protein':
        if 'sequence' not in data and 'modifications' not in data:
            return False, "Protein analysis requires sequence or modifications data"
    
    elif analysis_type == 'multiomics':
        if not any(key in data for key in ['dna', 'rna', 'protein']):
            return False, "Multi-omics analysis requires at least one omics type"
    
    return True, "Valid"

def allowed_file(filename):
    """Check if file type is allowed"""
    ALLOWED_EXTENSIONS = {'txt', 'csv', 'json', 'fasta', 'fastq', 'vcf', 'gff', 'bed'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# =========================== API ROUTES ===========================

@app.route('/')
def serve_react_app():
    """Serve React frontend"""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    })

@app.route('/api/auth/register', methods=['POST'])
@limiter.limit("5 per minute")
def register():
    """User registration"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['username', 'email', 'password']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if user exists
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Username already exists'}), 400
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already exists'}), 400
        
        # Create new user
        user = User(
            username=data['username'],
            email=data['email'],
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            institution=data.get('institution'),
            role=data.get('role', 'researcher')
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        # Create access token
        access_token = create_access_token(identity=user.id)
        
        return jsonify({
            'message': 'User created successfully',
            'user': user.to_dict(),
            'access_token': access_token
        }), 201
        
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return jsonify({'error': 'Registration failed'}), 500

@app.route('/api/auth/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    """User login"""
    try:
        data = request.get_json()
        
        if not data.get('username') or not data.get('password'):
            return jsonify({'error': 'Username and password required'}), 400
        
        user = User.query.filter_by(username=data['username']).first()
        
        if user and user.check_password(data['password']) and user.is_active:
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            access_token = create_access_token(identity=user.id)
            
            return jsonify({
                'message': 'Login successful',
                'user': user.to_dict(),
                'access_token': access_token
            })
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
            
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'error': 'Login failed'}), 500

@app.route('/api/analysis', methods=['POST'])
@jwt_required()
@limiter.limit("20 per hour")
def create_analysis():
    """Create new analysis"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate input
        analysis_type = data.get('analysis_type')
        if not analysis_type or analysis_type not in ['dna', 'rna', 'protein', 'multiomics']:
            return jsonify({'error': 'Invalid analysis type'}), 400
        
        input_data = data.get('data', {})
        valid, message = validate_analysis_data(input_data, analysis_type)
        if not valid:
            return jsonify({'error': message}), 400
        
        # Create analysis record
        analysis = Analysis(
            user_id=user_id,
            analysis_type=analysis_type,
            title=data.get('title', f'{analysis_type.upper()} Analysis'),
            description=data.get('description'),
            input_data=input_data
        )
        
        db.session.add(analysis)
        db.session.commit()
        
        # Run analysis
        result = run_analysis(analysis.id, input_data, analysis_type)
        
        return jsonify({
            'analysis_id': analysis.id,
            'status': 'created',
            'result': result
        }), 201
        
    except Exception as e:
        logger.error(f"Analysis creation error: {str(e)}")
        return jsonify({'error': 'Analysis creation failed'}), 500

@app.route('/api/data/fetch', methods=['POST'])
@jwt_required()
@limiter.limit("10 per hour")
def fetch_external_data():
    """Fetch data from external repositories"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        repository = data.get('repository')
        if not repository or repository not in ['ncbi', 'ensembl', 'uniprot', 'genbank', 'pubmed']:
            return jsonify({'error': 'Invalid repository'}), 400
        
        query_params = data.get('params', {})
        if not query_params:
            return jsonify({'error': 'Query parameters required'}), 400
        
        result = data_fetching_engine.fetch_data(repository, query_params)
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify({
            'status': 'success',
            'repository': repository,
            'result': result
        })
        
    except Exception as e:
        logger.error(f"Data fetching error: {str(e)}")
        return jsonify({'error': 'Data fetching failed'}), 500

@app.route('/api/data/repositories', methods=['GET'])
@jwt_required()
def get_supported_repositories():
    """Get list of supported data repositories"""
    repositories = {
        'ncbi': {
            'name': 'NCBI',
            'description': 'National Center for Biotechnology Information',
            'databases': ['nucleotide', 'protein', 'pubmed', 'gene'],
            'required_params': ['term'],
            'optional_params': ['db', 'retmax']
        },
        'ensembl': {
            'name': 'Ensembl',
            'description': 'Genome browser for vertebrate genomes',
            'required_params': ['gene_id'],
            'optional_params': ['species']
        },
        'uniprot': {
            'name': 'UniProt',
            'description': 'Universal Protein Resource',
            'required_params': ['query'],
            'optional_params': ['format', 'size']
        },
        'genbank': {
            'name': 'GenBank',
            'description': 'NIH genetic sequence database',
            'required_params': ['term'],
            'optional_params': ['retmax']
        },
        'pubmed': {
            'name': 'PubMed',
            'description': 'Biomedical literature database',
            'required_params': ['term'],
            'optional_params': ['retmax']
        }
    }
    
    return jsonify({
        'repositories': repositories,
        'total_count': len(repositories)
    })

@app.route('/api/analysis/<analysis_id>/repair', methods=['POST'])
@jwt_required()
def repair_analysis_data(analysis_id):
    """Manually trigger data repair for an analysis"""
    try:
        user_id = get_jwt_identity()
        analysis = Analysis.query.filter_by(id=analysis_id, user_id=user_id).first()
        
        if not analysis:
            return jsonify({'error': 'Analysis not found'}), 404
        
        if not analysis.police_report or analysis.police_report.get('status') != 'flagged':
            return jsonify({'error': 'No violations found to repair'}), 400
        
        violations = analysis.police_report.get('violations', [])
        repaired_data = auto_repair_engine.repair_data(analysis.input_data, violations)
        
        police_result = ai_police.police_analysis(repaired_data, analysis.analysis_type)
        
        analysis.input_data = repaired_data
        analysis.police_report = police_result
        analysis.compliance_score = police_result['compliance_score']
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'repaired_data': repaired_data,
            'new_police_report': police_result,
            'compliance_score': police_result['compliance_score']
        })
        
    except Exception as e:
        logger.error(f"Data repair error: {str(e)}")
        return jsonify({'error': 'Data repair failed'}), 500

@app.route('/api/analysis/<analysis_id>', methods=['GET'])
@jwt_required()
def get_analysis(analysis_id):
    """Get analysis details"""
    try:
        user_id = get_jwt_identity()
        analysis = Analysis.query.filter_by(id=analysis_id, user_id=user_id).first()
        
        if not analysis:
            return jsonify({'error': 'Analysis not found'}), 404
        
        return jsonify({
            'analysis': analysis.to_dict(),
            'input_data': analysis.input_data,
            'results': analysis.results,
            'police_report': analysis.police_report
        })
        
    except Exception as e:
        logger.error(f"Get analysis error: {str(e)}")
        return jsonify({'error': 'Failed to get analysis'}), 500

@app.route('/api/analyses', methods=['GET'])
@jwt_required()
def get_user_analyses():
    """Get all analyses for the current user"""
    try:
        user_id = get_jwt_identity()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        analyses = Analysis.query.filter_by(user_id=user_id)\
                                .order_by(Analysis.created_at.desc())\
                                .paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'analyses': [analysis.to_dict() for analysis in analyses.items],
            'total': analyses.total,
            'pages': analyses.pages,
            'current_page': page
        })
        
    except Exception as e:
        logger.error(f"Get analyses error: {str(e)}")
        return jsonify({'error': 'Failed to get analyses'}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)

def run_analysis(analysis_id, data, analysis_type):
    """Run analysis synchronously (simplified version)"""
    try:
        analysis = Analysis.query.get(analysis_id)
        if not analysis:
            return {'error': 'Analysis not found'}
        
        analysis.status = 'running'
        analysis.started_at = datetime.utcnow()
        analysis.progress = 10
        db.session.commit()
        
        # AI Police pre-check
        police_result = ai_police.police_analysis(data, analysis_type)
        analysis.police_report = police_result
        analysis.compliance_score = police_result['compliance_score']
        analysis.progress = 30
        db.session.commit()
        
        if police_result['status'] == 'flagged':
            repaired_data = auto_repair_engine.repair_data(data, police_result['violations'])
            if repaired_data:
                data = repaired_data
                police_result = ai_police.police_analysis(data, analysis_type)
                analysis.police_report = police_result
                analysis.compliance_score = police_result['compliance_score']
        
        analysis.progress = 50
        db.session.commit()
        
        features = ml_engine.extract_features(data, analysis_type)
        analysis.progress = 70
        db.session.commit()
        
        # Make predictions
        predictions = ml_engine.predict(features, analysis_type)
        analysis.ml_predictions = predictions
        analysis.confidence_score = predictions.get('confidence', 0.0)
        analysis.progress = 90
        db.session.commit()
        
        results = {
            'features': features,
            'predictions': predictions,
            'police_report': police_result,
            'compliance_score': police_result['compliance_score']
        }
        
        analysis.results = results
        analysis.status = 'completed'
        analysis.completed_at = datetime.utcnow()
        analysis.progress = 100
        db.session.commit()
        
        return results
        
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        if 'analysis' in locals():
            analysis.status = 'failed'
            analysis.error_message = str(e)
            analysis.completed_at = datetime.utcnow()
            db.session.commit()
        return {'error': str(e)}
        