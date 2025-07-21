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
from flask_socketio import SocketIO, emit, join_room, leave_room
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
import networkx as nx
import plotly.graph_objects as go
import plotly.express as px
from transformers import pipeline, AutoTokenizer, AutoModel
import torch
import spacy
import nltk
from collections import defaultdict, Counter
import boto3
from azure.storage.blob import BlobServiceClient
from google.cloud import storage as gcs
import threading
import asyncio

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
limiter = Limiter(
    key_func=get_remote_address,
    app=app
)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

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
    project_id = db.Column(db.String(36), db.ForeignKey('project.id'))
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
    
    # Relationships
    comments = db.relationship('Comment', backref='analysis', lazy=True)
    compliance_reports = db.relationship('ComplianceReport', backref='analysis', lazy=True)
    multimodal_analyses = db.relationship('MultiModalAnalysis', backref='analysis', lazy=True)
    
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

class Project(db.Model):
    """Project model for collaborative research"""
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_public = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    members = db.relationship('ProjectMember', backref='project', lazy=True, cascade='all, delete-orphan')
    analyses = db.relationship('Analysis', backref='project', lazy=True)
    sessions = db.relationship('CollaborationSession', backref='project', lazy=True)

class ProjectMember(db.Model):
    """Project membership model"""
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.String(36), db.ForeignKey('project.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    role = db.Column(db.String(20), default='member')
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('project_id', 'user_id'),)

class CollaborationSession(db.Model):
    """Real-time collaboration session"""
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = db.Column(db.String(36), db.ForeignKey('project.id'), nullable=False)
    analysis_id = db.Column(db.String(36), db.ForeignKey('analysis.id'))
    session_type = db.Column(db.String(50), default='analysis')
    active_users = db.Column(db.JSON, default=list)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    ended_at = db.Column(db.DateTime)

class Comment(db.Model):
    """Comment model for collaborative discussions"""
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    project_id = db.Column(db.String(36), db.ForeignKey('project.id'))
    analysis_id = db.Column(db.String(36), db.ForeignKey('analysis.id'))
    parent_id = db.Column(db.String(36), db.ForeignKey('comment.id'))
    content = db.Column(db.Text, nullable=False)
    comment_type = db.Column(db.String(20), default='general')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    replies = db.relationship('Comment', backref=db.backref('parent', remote_side='Comment.id'), lazy=True)

class Workflow(db.Model):
    """Workflow model for no-code analysis pipelines"""
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    project_id = db.Column(db.String(36), db.ForeignKey('project.id'))
    workflow_definition = db.Column(db.JSON, nullable=False)
    is_template = db.Column(db.Boolean, default=False)
    is_public = db.Column(db.Boolean, default=False)
    version = db.Column(db.String(20), default='1.0')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    executions = db.relationship('WorkflowExecution', backref='workflow', lazy=True)

class WorkflowStep(db.Model):
    """Individual workflow step"""
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_id = db.Column(db.String(36), db.ForeignKey('workflow.id'), nullable=False)
    step_name = db.Column(db.String(100), nullable=False)
    step_type = db.Column(db.String(50), nullable=False)
    step_config = db.Column(db.JSON)
    position_x = db.Column(db.Float, default=0)
    position_y = db.Column(db.Float, default=0)
    order_index = db.Column(db.Integer, default=0)

class WorkflowExecution(db.Model):
    """Workflow execution tracking"""
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_id = db.Column(db.String(36), db.ForeignKey('workflow.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), default='queued')
    input_data = db.Column(db.JSON)
    output_data = db.Column(db.JSON)
    execution_log = db.Column(db.JSON, default=list)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    error_message = db.Column(db.Text)

class LiteratureSource(db.Model):
    """Literature source tracking"""
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(500), nullable=False)
    authors = db.Column(db.JSON)
    journal = db.Column(db.String(200))
    publication_date = db.Column(db.Date)
    doi = db.Column(db.String(100))
    pmid = db.Column(db.String(20))
    abstract = db.Column(db.Text)
    full_text = db.Column(db.Text)
    keywords = db.Column(db.JSON)
    citation_count = db.Column(db.Integer, default=0)
    relevance_score = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    citations = db.relationship('Citation', foreign_keys='Citation.source_id', backref='source', lazy=True)

class Citation(db.Model):
    """Citation relationships between papers"""
    id = db.Column(db.Integer, primary_key=True)
    source_id = db.Column(db.String(36), db.ForeignKey('literature_source.id'), nullable=False)
    cited_source_id = db.Column(db.String(36), db.ForeignKey('literature_source.id'), nullable=False)
    citation_context = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Hypothesis(db.Model):
    """AI-generated hypotheses"""
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    project_id = db.Column(db.String(36), db.ForeignKey('project.id'))
    hypothesis_text = db.Column(db.Text, nullable=False)
    confidence_score = db.Column(db.Float)
    supporting_evidence = db.Column(db.JSON)
    generated_method = db.Column(db.String(50))
    status = db.Column(db.String(20), default='generated')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class KnowledgeGraph(db.Model):
    """Knowledge graph nodes and relationships"""
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    entity_type = db.Column(db.String(50), nullable=False)
    entity_name = db.Column(db.String(200), nullable=False)
    entity_id = db.Column(db.String(100))
    properties = db.Column(db.JSON)
    relationships = db.Column(db.JSON)
    confidence_score = db.Column(db.Float)
    source_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ComplianceReport(db.Model):
    """Compliance reporting and tracking"""
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    analysis_id = db.Column(db.String(36), db.ForeignKey('analysis.id'), nullable=False)
    project_id = db.Column(db.String(36), db.ForeignKey('project.id'))
    report_type = db.Column(db.String(50), nullable=False)
    compliance_score = db.Column(db.Float)
    violations = db.Column(db.JSON)
    recommendations = db.Column(db.JSON)
    status = db.Column(db.String(20), default='draft')
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)
    submitted_at = db.Column(db.DateTime)
    approved_at = db.Column(db.DateTime)

class RegulatorySubmission(db.Model):
    """Regulatory submission tracking"""
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = db.Column(db.String(36), db.ForeignKey('project.id'), nullable=False)
    submission_type = db.Column(db.String(50), nullable=False)
    submission_data = db.Column(db.JSON)
    documents = db.Column(db.JSON)
    status = db.Column(db.String(20), default='draft')
    submission_date = db.Column(db.DateTime)
    response_date = db.Column(db.DateTime)
    approval_status = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class AuditLog(db.Model):
    """Audit trail for compliance"""
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    action = db.Column(db.String(100), nullable=False)
    resource_type = db.Column(db.String(50))
    resource_id = db.Column(db.String(36))
    details = db.Column(db.JSON)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class DataSource(db.Model):
    """Multi-modal data source tracking"""
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(200), nullable=False)
    data_type = db.Column(db.String(50), nullable=False)
    source_format = db.Column(db.String(50))
    file_path = db.Column(db.String(500))
    source_metadata = db.Column(db.JSON)
    schema_info = db.Column(db.JSON)
    quality_metrics = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    integrations = db.relationship('DataIntegration', backref='data_source', lazy=True)

class DataIntegration(db.Model):
    """Multi-modal data integration tracking"""
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(200), nullable=False)
    data_source_id = db.Column(db.String(36), db.ForeignKey('data_source.id'), nullable=False)
    integration_method = db.Column(db.String(50))
    harmonization_rules = db.Column(db.JSON)
    mapping_config = db.Column(db.JSON)
    quality_score = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class MultiModalAnalysis(db.Model):
    """Multi-modal analysis results"""
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    analysis_id = db.Column(db.String(36), db.ForeignKey('analysis.id'), nullable=False)
    integrated_data_sources = db.Column(db.JSON)
    cross_modal_correlations = db.Column(db.JSON)
    integration_quality = db.Column(db.Float)
    insights = db.Column(db.JSON)
    visualizations = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

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


# =========================== AI LITERATURE INTELLIGENCE ENGINE ===========================

class AILiteratureEngine:
    """AI-powered literature intelligence and analysis system"""
    
    def __init__(self):
        self.summarizer = None
        self.nlp = None
        self.knowledge_graph = nx.DiGraph()
        self.initialize_models()
    
    def initialize_models(self):
        """Initialize NLP models"""
        try:
            self.summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
            self.nlp = spacy.load("en_core_web_sm")
        except Exception as e:
            logger.warning(f"Could not load NLP models: {e}")
    
    def search_literature(self, query, sources=['pubmed'], max_results=50):
        """Search literature from multiple sources"""
        results = []
        
        if 'pubmed' in sources:
            pubmed_results = self._search_pubmed(query, max_results)
            results.extend(pubmed_results)
        
        return self._deduplicate_results(results)
    
    def _search_pubmed(self, query, max_results):
        """Search PubMed for literature"""
        import requests
        
        search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        search_params = {
            'db': 'pubmed',
            'term': query,
            'retmax': max_results,
            'retmode': 'json'
        }
        
        try:
            response = requests.get(search_url, params=search_params, timeout=30)
            response.raise_for_status()
            search_result = response.json()
            
            if 'esearchresult' not in search_result:
                return []
            
            ids = search_result['esearchresult']['idlist']
            if not ids:
                return []
            
            fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
            fetch_params = {
                'db': 'pubmed',
                'id': ','.join(ids),
                'rettype': 'abstract',
                'retmode': 'xml'
            }
            
            response = requests.get(fetch_url, params=fetch_params, timeout=30)
            response.raise_for_status()
            
            return self._parse_pubmed_results(response.text)
            
        except Exception as e:
            logger.error(f"PubMed search error: {e}")
            return []
    
    def _parse_pubmed_results(self, xml_text):
        """Parse PubMed XML results"""
        try:
            root = ET.fromstring(xml_text)
            articles = []
            
            for article in root.findall('.//PubmedArticle'):
                pmid_elem = article.find('.//PMID')
                title_elem = article.find('.//ArticleTitle')
                abstract_elem = article.find('.//AbstractText')
                authors_elems = article.findall('.//Author')
                journal_elem = article.find('.//Journal/Title')
                date_elem = article.find('.//PubDate/Year')
                
                authors = []
                for author in authors_elems:
                    lastname = author.find('LastName')
                    forename = author.find('ForeName')
                    if lastname is not None and forename is not None:
                        authors.append(f"{forename.text} {lastname.text}")
                
                article_data = {
                    'pmid': pmid_elem.text if pmid_elem is not None else '',
                    'title': title_elem.text if title_elem is not None else '',
                    'abstract': abstract_elem.text if abstract_elem is not None else '',
                    'authors': authors,
                    'journal': journal_elem.text if journal_elem is not None else '',
                    'year': date_elem.text if date_elem is not None else '',
                    'source': 'pubmed'
                }
                articles.append(article_data)
            
            return articles
        except ET.ParseError:
            return []
    
    def _deduplicate_results(self, results):
        """Remove duplicate articles"""
        seen_titles = set()
        unique_results = []
        
        for result in results:
            title_lower = result.get('title', '').lower()
            if title_lower not in seen_titles and title_lower:
                seen_titles.add(title_lower)
                unique_results.append(result)
        
        return unique_results
    
    def summarize_literature(self, articles, max_length=150):
        """Generate summaries for literature"""
        if not self.summarizer:
            return [{'summary': 'Summarization model not available'} for _ in articles]
        
        summaries = []
        for article in articles:
            try:
                text = article.get('abstract', '') or article.get('title', '')
                if len(text) > 50:
                    summary = self.summarizer(text, max_length=max_length, min_length=30, do_sample=False)
                    summaries.append({
                        'pmid': article.get('pmid'),
                        'title': article.get('title'),
                        'summary': summary[0]['summary_text']
                    })
                else:
                    summaries.append({
                        'pmid': article.get('pmid'),
                        'title': article.get('title'),
                        'summary': text
                    })
            except Exception as e:
                logger.error(f"Summarization error: {e}")
                summaries.append({
                    'pmid': article.get('pmid'),
                    'title': article.get('title'),
                    'summary': 'Summary generation failed'
                })
        
        return summaries
    
    def extract_entities(self, text):
        """Extract biomedical entities from text"""
        if not self.nlp:
            return []
        
        doc = self.nlp(text)
        entities = []
        
        for ent in doc.ents:
            entities.append({
                'text': ent.text,
                'label': ent.label_,
                'start': ent.start_char,
                'end': ent.end_char
            })
        
        return entities
    
    def build_knowledge_graph(self, articles):
        """Build knowledge graph from literature"""
        self.knowledge_graph.clear()
        
        for article in articles:
            text = f"{article.get('title', '')} {article.get('abstract', '')}"
            entities = self.extract_entities(text)
            
            for entity in entities:
                entity_text = entity['text'].lower()
                
                if not self.knowledge_graph.has_node(entity_text):
                    self.knowledge_graph.add_node(entity_text, 
                                                label=entity['label'],
                                                count=1,
                                                articles=[article.get('pmid')])
                else:
                    self.knowledge_graph.nodes[entity_text]['count'] += 1
                    self.knowledge_graph.nodes[entity_text]['articles'].append(article.get('pmid'))
            
            for i, entity1 in enumerate(entities):
                for entity2 in entities[i+1:]:
                    e1_text = entity1['text'].lower()
                    e2_text = entity2['text'].lower()
                    
                    if self.knowledge_graph.has_edge(e1_text, e2_text):
                        self.knowledge_graph[e1_text][e2_text]['weight'] += 1
                    else:
                        self.knowledge_graph.add_edge(e1_text, e2_text, weight=1)
        
        return self.knowledge_graph
    
    def generate_hypotheses(self, query, articles, max_hypotheses=5):
        """Generate research hypotheses from literature analysis"""
        hypotheses = []
        
        entities = []
        for article in articles[:10]:
            text = f"{article.get('title', '')} {article.get('abstract', '')}"
            article_entities = self.extract_entities(text)
            entities.extend(article_entities)
        
        entity_counts = Counter([e['text'].lower() for e in entities])
        top_entities = [entity for entity, count in entity_counts.most_common(10)]
        
        for i, entity1 in enumerate(top_entities[:5]):
            for entity2 in top_entities[i+1:i+3]:
                hypothesis = f"There may be a relationship between {entity1} and {entity2} in the context of {query}"
                hypotheses.append({
                    'hypothesis': hypothesis,
                    'confidence': 0.6 + (len([a for a in articles if entity1 in a.get('abstract', '').lower() and entity2 in a.get('abstract', '').lower()]) * 0.1),
                    'supporting_entities': [entity1, entity2],
                    'method': 'co_occurrence_analysis'
                })
        
        return hypotheses[:max_hypotheses]


# =========================== REAL-TIME COLLABORATION ENGINE ===========================

class CollaborationEngine:
    """Real-time collaboration system"""
    
    def __init__(self, socketio_instance):
        self.socketio = socketio_instance
        self.active_sessions = {}
        self.user_sessions = defaultdict(set)
    
    def create_session(self, project_id, session_type='analysis', analysis_id=None):
        """Create a new collaboration session"""
        session = CollaborationSession(
            project_id=project_id,
            session_type=session_type,
            analysis_id=analysis_id
        )
        db.session.add(session)
        db.session.commit()
        
        self.active_sessions[session.id] = {
            'users': set(),
            'created_at': datetime.utcnow(),
            'last_activity': datetime.utcnow()
        }
        
        return session.id
    
    def join_session(self, session_id, user_id):
        """Add user to collaboration session"""
        if session_id in self.active_sessions:
            self.active_sessions[session_id]['users'].add(user_id)
            self.active_sessions[session_id]['last_activity'] = datetime.utcnow()
            self.user_sessions[user_id].add(session_id)
            
            session = CollaborationSession.query.get(session_id)
            if session:
                active_users = session.active_users or []
                if user_id not in active_users:
                    active_users.append(user_id)
                    session.active_users = active_users
                    db.session.commit()
            
            return True
        return False
    
    def broadcast_to_session(self, session_id, event, data):
        """Broadcast event to all users in session"""
        if session_id in self.active_sessions:
            self.socketio.emit(event, data, room=session_id)


# =========================== NO-CODE WORKFLOW BUILDER ENGINE ===========================

class WorkflowBuilderEngine:
    """No-code workflow builder and execution engine"""
    
    def __init__(self):
        self.step_types = {
            'data_fetch': self._execute_data_fetch,
            'data_filter': self._execute_data_filter,
            'analysis': self._execute_analysis,
            'visualization': self._execute_visualization,
            'export': self._execute_export
        }
    
    def create_workflow(self, name, description, user_id, workflow_definition, project_id=None):
        """Create a new workflow"""
        workflow = Workflow(
            name=name,
            description=description,
            user_id=user_id,
            project_id=project_id,
            workflow_definition=workflow_definition
        )
        db.session.add(workflow)
        db.session.commit()
        return workflow.id
    
    def execute_workflow(self, workflow_id, input_data, user_id):
        """Execute a workflow"""
        workflow = Workflow.query.get(workflow_id)
        if not workflow:
            return {'error': 'Workflow not found'}
        
        execution = WorkflowExecution(
            workflow_id=workflow_id,
            user_id=user_id,
            input_data=input_data,
            status='running'
        )
        db.session.add(execution)
        db.session.commit()
        
        try:
            result = self._execute_workflow_steps(workflow.workflow_definition, input_data, execution.id)
            
            execution.status = 'completed'
            execution.output_data = result
            execution.completed_at = datetime.utcnow()
            db.session.commit()
            
            return result
            
        except Exception as e:
            execution.status = 'failed'
            execution.error_message = str(e)
            execution.completed_at = datetime.utcnow()
            db.session.commit()
            
            return {'error': str(e)}
    
    def _execute_workflow_steps(self, workflow_definition, input_data, execution_id):
        """Execute individual workflow steps"""
        current_data = input_data
        results = {}
        
        steps = sorted(workflow_definition.get('steps', []), key=lambda x: x.get('order', 0))
        
        for step in steps:
            step_type = step.get('type')
            step_config = step.get('config', {})
            step_id = step.get('id')
            
            if step_type in self.step_types:
                try:
                    step_result = self.step_types[step_type](current_data, step_config)
                    results[step_id] = step_result
                    current_data = step_result.get('output', current_data)
                    
                except Exception as e:
                    raise e
            else:
                raise ValueError(f"Unknown step type: {step_type}")
        
        return {
            'final_output': current_data,
            'step_results': results
        }
    
    def _execute_data_fetch(self, input_data, config):
        """Execute data fetching step"""
        repository = config.get('repository')
        params = config.get('params', {})
        
        data_fetching_engine = DataFetchingEngine()
        result = data_fetching_engine.fetch_data(repository, params)
        
        return {'output': result, 'step_type': 'data_fetch'}
    
    def _execute_data_filter(self, input_data, config):
        """Execute data filtering step"""
        filter_type = config.get('filter_type', 'column')
        filter_config = config.get('filter_config', {})
        
        if isinstance(input_data, dict) and 'data' in input_data:
            data = input_data['data']
            
            if filter_type == 'column' and isinstance(data, list):
                column = filter_config.get('column')
                value = filter_config.get('value')
                operator = filter_config.get('operator', 'equals')
                
                filtered_data = []
                for item in data:
                    if isinstance(item, dict) and column in item:
                        if operator == 'equals' and item[column] == value:
                            filtered_data.append(item)
                        elif operator == 'contains' and value in str(item[column]):
                            filtered_data.append(item)
                
                return {'output': {'data': filtered_data}, 'step_type': 'data_filter'}
        
        return {'output': input_data, 'step_type': 'data_filter'}
    
    def _execute_analysis(self, input_data, config):
        """Execute analysis step"""
        analysis_type = config.get('analysis_type', 'basic')
        
        ml_engine = BioCheAIMLEngine()
        
        if analysis_type in ['dna', 'rna', 'protein', 'multiomics']:
            features = ml_engine.extract_features(input_data, analysis_type)
            predictions = ml_engine.predict(features, analysis_type)
            
            return {
                'output': {
                    'features': features,
                    'predictions': predictions
                },
                'step_type': 'analysis'
            }
        
        return {'output': input_data, 'step_type': 'analysis'}
    
    def _execute_visualization(self, input_data, config):
        """Execute visualization step"""
        viz_type = config.get('viz_type', 'scatter')
        
        viz_data = {
            'type': viz_type,
            'data': input_data,
            'config': config
        }
        
        return {'output': viz_data, 'step_type': 'visualization'}
    
    def _execute_export(self, input_data, config):
        """Execute export step"""
        export_format = config.get('format', 'json')
        
        export_data = {
            'format': export_format,
            'data': input_data,
            'exported_at': datetime.utcnow().isoformat()
        }
        
        return {'output': export_data, 'step_type': 'export'}


# =========================== MULTI-MODAL DATA INTEGRATION ENGINE ===========================

class MultiModalEngine:
    """Multi-modal data integration and analysis engine"""
    
    def __init__(self):
        self.supported_formats = {
            'omics': ['csv', 'tsv', 'json', 'fasta', 'fastq'],
            'clinical': ['csv', 'json', 'xml'],
            'imaging': ['dicom', 'nifti', 'png', 'jpg'],
            'literature': ['json', 'xml', 'txt']
        }
    
    def register_data_source(self, name, data_type, source_format, file_path, metadata=None):
        """Register a new data source"""
        data_source = DataSource(
            name=name,
            data_type=data_type,
            source_format=source_format,
            file_path=file_path,
            metadata=metadata or {},
            schema_info=self._analyze_schema(file_path, source_format),
            quality_metrics=self._calculate_quality_metrics(file_path, source_format)
        )
        db.session.add(data_source)
        db.session.commit()
        return data_source.id
    
    def _analyze_schema(self, file_path, source_format):
        """Analyze data schema"""
        try:
            if source_format in ['csv', 'tsv']:
                df = pd.read_csv(file_path, nrows=5)
                return {
                    'columns': list(df.columns),
                    'dtypes': df.dtypes.to_dict(),
                    'shape': df.shape
                }
            elif source_format == 'json':
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, list) and len(data) > 0:
                        return {
                            'keys': list(data[0].keys()) if isinstance(data[0], dict) else [],
                            'type': 'array_of_objects'
                        }
                    elif isinstance(data, dict):
                        return {
                            'keys': list(data.keys()),
                            'type': 'object'
                        }
        except Exception as e:
            logger.error(f"Schema analysis error: {e}")
        
        return {}
    
    def _calculate_quality_metrics(self, file_path, source_format):
        """Calculate data quality metrics"""
        try:
            if source_format in ['csv', 'tsv']:
                df = pd.read_csv(file_path)
                return {
                    'completeness': (1 - df.isnull().sum().sum() / (df.shape[0] * df.shape[1])),
                    'row_count': len(df),
                    'column_count': len(df.columns),
                    'duplicate_rows': df.duplicated().sum()
                }
        except Exception as e:
            logger.error(f"Quality metrics error: {e}")
        
        return {}
    
    def create_integration(self, name, data_source_ids, integration_method='concatenation'):
        """Create data integration"""
        integration = DataIntegration(
            name=name,
            integration_method=integration_method,
            harmonization_rules=self._generate_harmonization_rules(data_source_ids),
            mapping_config=self._generate_mapping_config(data_source_ids),
            quality_score=0.8
        )
        db.session.add(integration)
        db.session.commit()
        return integration.id
    
    def _generate_harmonization_rules(self, data_source_ids):
        """Generate harmonization rules for data integration"""
        rules = {
            'column_mapping': {},
            'value_transformations': {},
            'unit_conversions': {}
        }
        
        common_mappings = {
            'id': ['ID', 'identifier', 'sample_id', 'patient_id'],
            'age': ['Age', 'age_years', 'patient_age'],
            'gender': ['Gender', 'sex', 'patient_gender'],
            'expression': ['expression_level', 'expr', 'value']
        }
        
        for standard_name, variants in common_mappings.items():
            rules['column_mapping'][standard_name] = variants
        
        return rules
    
    def _generate_mapping_config(self, data_source_ids):
        """Generate mapping configuration"""
        return {
            'join_keys': ['id', 'sample_id', 'patient_id'],
            'merge_strategy': 'outer',
            'conflict_resolution': 'latest'
        }


# =========================== REGULATORY COMPLIANCE ENGINE ===========================

class RegulatoryEngine:
    """Regulatory compliance and submission engine"""
    
    def __init__(self):
        self.compliance_frameworks = {
            'gdpr': self._check_gdpr_compliance,
            'hipaa': self._check_hipaa_compliance,
            'fda': self._check_fda_compliance,
            'ema': self._check_ema_compliance
        }
    
    def generate_compliance_report(self, analysis_id, framework_type):
        """Generate compliance report for analysis"""
        analysis = Analysis.query.get(analysis_id)
        if not analysis:
            return {'error': 'Analysis not found'}
        
        if framework_type not in self.compliance_frameworks:
            return {'error': f'Unsupported framework: {framework_type}'}
        
        compliance_check = self.compliance_frameworks[framework_type]
        result = compliance_check(analysis)
        
        report = ComplianceReport(
            analysis_id=analysis_id,
            project_id=analysis.project_id,
            report_type=framework_type,
            compliance_score=result['score'],
            violations=result['violations'],
            recommendations=result['recommendations']
        )
        db.session.add(report)
        db.session.commit()
        
        return {
            'report_id': report.id,
            'compliance_score': result['score'],
            'violations': result['violations'],
            'recommendations': result['recommendations']
        }
    
    def _check_gdpr_compliance(self, analysis):
        """Check GDPR compliance"""
        violations = []
        recommendations = []
        
        data_str = json.dumps(analysis.input_data) if analysis.input_data else ''
        
        if re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', data_str):
            violations.append('Personal email addresses detected')
            recommendations.append('Remove or anonymize email addresses')
        
        if 'consent' not in data_str.lower():
            violations.append('No explicit consent documentation found')
            recommendations.append('Document user consent for data processing')
        
        score = max(0, 1.0 - (len(violations) * 0.3))
        
        return {
            'score': score,
            'violations': violations,
            'recommendations': recommendations
        }
    
    def _check_hipaa_compliance(self, analysis):
        """Check HIPAA compliance"""
        violations = []
        recommendations = []
        
        data_str = json.dumps(analysis.input_data) if analysis.input_data else ''
        
        phi_patterns = [
            r'\b\d{3}-\d{2}-\d{4}\b',
            r'\b\d{3}-\d{3}-\d{4}\b',
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        ]
        
        for pattern in phi_patterns:
            if re.search(pattern, data_str):
                violations.append('Potential PHI detected')
                recommendations.append('Remove or de-identify personal health information')
                break
        
        score = max(0, 1.0 - (len(violations) * 0.4))
        
        return {
            'score': score,
            'violations': violations,
            'recommendations': recommendations
        }
    
    def _check_fda_compliance(self, analysis):
        """Check FDA compliance"""
        violations = []
        recommendations = []
        
        if not analysis.ml_predictions or not analysis.confidence_score:
            violations.append('Insufficient validation metrics')
            recommendations.append('Provide comprehensive validation and confidence metrics')
        
        if analysis.confidence_score and analysis.confidence_score < 0.8:
            violations.append('Low confidence score for regulatory submission')
            recommendations.append('Improve model performance before submission')
        
        score = max(0, 1.0 - (len(violations) * 0.3))
        
        return {
            'score': score,
            'violations': violations,
            'recommendations': recommendations
        }
    
    def _check_ema_compliance(self, analysis):
        """Check EMA compliance"""
        violations = []
        recommendations = []
        
        if not analysis.results or 'methodology' not in str(analysis.results):
            violations.append('Insufficient methodology documentation')
            recommendations.append('Document analysis methodology thoroughly')
        
        score = max(0, 1.0 - (len(violations) * 0.3))
        
        return {
            'score': score,
            'violations': violations,
            'recommendations': recommendations
        }


# =========================== CLOUD SCALABILITY ENGINE ===========================

class CloudEngine:
    """Cloud scalability and distributed computing engine"""
    
    def __init__(self):
        self.cloud_providers = {
            'aws': self._setup_aws,
            'gcp': self._setup_gcp,
            'azure': self._setup_azure
        }
        self.active_instances = {}
    
    def setup_cloud_provider(self, provider, credentials):
        """Setup cloud provider connection"""
        if provider not in self.cloud_providers:
            return {'error': f'Unsupported provider: {provider}'}
        
        try:
            client = self.cloud_providers[provider](credentials)
            return {'status': 'success', 'client': client}
        except Exception as e:
            return {'error': str(e)}
    
    def _setup_aws(self, credentials):
        """Setup AWS connection"""
        return boto3.client('ec2', 
                          aws_access_key_id=credentials.get('access_key'),
                          aws_secret_access_key=credentials.get('secret_key'),
                          region_name=credentials.get('region', 'us-east-1'))
    
    def _setup_gcp(self, credentials):
        """Setup GCP connection"""
        return gcs.Client.from_service_account_json(credentials.get('service_account_path'))
    
    def _setup_azure(self, credentials):
        """Setup Azure connection"""
        return BlobServiceClient(account_url=credentials.get('account_url'),
                               credential=credentials.get('credential'))
    
    def scale_analysis(self, analysis_id, target_instances=2):
        """Scale analysis across multiple cloud instances"""
        analysis = Analysis.query.get(analysis_id)
        if not analysis:
            return {'error': 'Analysis not found'}
        
        scaling_result = {
            'analysis_id': analysis_id,
            'target_instances': target_instances,
            'status': 'scaled',
            'instances': []
        }
        
        for i in range(target_instances):
            instance_id = f"instance_{i}_{analysis_id}"
            scaling_result['instances'].append({
                'id': instance_id,
                'status': 'running',
                'progress': 0
            })
        
        return scaling_result
    
    def upload_to_cloud(self, file_path, provider='aws', bucket_name='biocheai-data'):
        """Upload file to cloud storage"""
        try:
            if provider == 'aws':
                s3_client = boto3.client('s3')
                s3_client.upload_file(file_path, bucket_name, os.path.basename(file_path))
                return {'status': 'success', 'url': f's3://{bucket_name}/{os.path.basename(file_path)}'}
            
            return {'error': 'Provider not implemented'}
        except Exception as e:
            return {'error': str(e)}


# Initialize all engines
ml_engine = BioCheAIMLEngine()
ai_police = AIPoliceEngine()
auto_repair_engine = AutoRepairEngine()
data_fetching_engine = DataFetchingEngine()
literature_engine = AILiteratureEngine()
collaboration_engine = CollaborationEngine(socketio)
workflow_engine = WorkflowBuilderEngine()
multimodal_engine = MultiModalEngine()
regulatory_engine = RegulatoryEngine()
cloud_engine = CloudEngine()

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
        access_token = create_access_token(identity=str(user.id))
        
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
            
            access_token = create_access_token(identity=str(user.id))
            
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
        user_id = int(get_jwt_identity())
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
        user_id = int(get_jwt_identity())
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
        user_id = int(get_jwt_identity())
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
        user_id = int(get_jwt_identity())
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
        user_id = int(get_jwt_identity())
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


# =========================== NEW API ENDPOINTS FOR ADVANCED FEATURES ===========================

@app.route('/api/literature/search', methods=['POST'])
@jwt_required()
@limiter.limit("20 per hour")
def search_literature():
    """Search literature using AI intelligence"""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        query = data.get('query')
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        sources = data.get('sources', ['pubmed'])
        max_results = data.get('max_results', 20)
        
        results = literature_engine.search_literature(query, sources, max_results)
        
        return jsonify({
            'status': 'success',
            'query': query,
            'results': results,
            'total_found': len(results)
        })
        
    except Exception as e:
        logger.error(f"Literature search error: {str(e)}")
        return jsonify({'error': 'Literature search failed'}), 500

@app.route('/api/literature/summarize', methods=['POST'])
@jwt_required()
@limiter.limit("10 per hour")
def summarize_literature():
    """Generate AI summaries for literature"""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        articles = data.get('articles', [])
        if not articles:
            return jsonify({'error': 'Articles are required'}), 400
        
        max_length = data.get('max_length', 150)
        summaries = literature_engine.summarize_literature(articles, max_length)
        
        return jsonify({
            'status': 'success',
            'summaries': summaries
        })
        
    except Exception as e:
        logger.error(f"Literature summarization error: {str(e)}")
        return jsonify({'error': 'Summarization failed'}), 500

@app.route('/api/literature/hypotheses', methods=['POST'])
@jwt_required()
@limiter.limit("5 per hour")
def generate_hypotheses():
    """Generate research hypotheses from literature"""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        query = data.get('query')
        articles = data.get('articles', [])
        max_hypotheses = data.get('max_hypotheses', 5)
        
        if not query or not articles:
            return jsonify({'error': 'Query and articles are required'}), 400
        
        hypotheses = literature_engine.generate_hypotheses(query, articles, max_hypotheses)
        
        for hyp in hypotheses:
            hypothesis = Hypothesis(
                user_id=user_id,
                hypothesis_text=hyp['hypothesis'],
                confidence_score=hyp['confidence'],
                supporting_evidence=hyp.get('supporting_entities', []),
                generated_method=hyp.get('method', 'ai_analysis')
            )
            db.session.add(hypothesis)
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'hypotheses': hypotheses
        })
        
    except Exception as e:
        logger.error(f"Hypothesis generation error: {str(e)}")
        return jsonify({'error': 'Hypothesis generation failed'}), 500

@app.route('/api/projects', methods=['POST'])
@jwt_required()
@limiter.limit("10 per hour")
def create_project():
    """Create a new collaborative project"""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        name = data.get('name')
        if not name:
            return jsonify({'error': 'Project name is required'}), 400
        
        project = Project(
            name=name,
            description=data.get('description'),
            owner_id=user_id,
            is_public=data.get('is_public', False)
        )
        db.session.add(project)
        db.session.commit()
        
        member = ProjectMember(
            project_id=project.id,
            user_id=user_id,
            role='owner'
        )
        db.session.add(member)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'project_id': project.id,
            'name': project.name
        }), 201
        
    except Exception as e:
        logger.error(f"Project creation error: {str(e)}")
        return jsonify({'error': 'Project creation failed'}), 500

@app.route('/api/projects', methods=['GET'])
@jwt_required()
def get_user_projects():
    """Get user's projects"""
    try:
        user_id = int(get_jwt_identity())
        
        projects = db.session.query(Project).join(ProjectMember).filter(
            ProjectMember.user_id == user_id
        ).all()
        
        project_list = []
        for project in projects:
            member = ProjectMember.query.filter_by(
                project_id=project.id, 
                user_id=user_id
            ).first()
            
            project_list.append({
                'id': project.id,
                'name': project.name,
                'description': project.description,
                'role': member.role if member else 'viewer',
                'created_at': project.created_at.isoformat(),
                'member_count': len(project.members)
            })
        
        return jsonify({
            'projects': project_list,
            'total': len(project_list)
        })
        
    except Exception as e:
        logger.error(f"Get projects error: {str(e)}")
        return jsonify({'error': 'Failed to get projects'}), 500

@app.route('/api/collaboration/sessions', methods=['POST'])
@jwt_required()
def create_collaboration_session():
    """Create a new collaboration session"""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        project_id = data.get('project_id')
        if not project_id:
            return jsonify({'error': 'Project ID is required'}), 400
        
        session_id = collaboration_engine.create_session(
            project_id=project_id,
            session_type=data.get('session_type', 'analysis'),
            analysis_id=data.get('analysis_id')
        )
        
        return jsonify({
            'status': 'success',
            'session_id': session_id
        }), 201
        
    except Exception as e:
        logger.error(f"Collaboration session error: {str(e)}")
        return jsonify({'error': 'Session creation failed'}), 500

@app.route('/api/workflows', methods=['POST'])
@jwt_required()
@limiter.limit("20 per hour")
def create_workflow():
    """Create a new workflow"""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        name = data.get('name')
        workflow_definition = data.get('workflow_definition')
        
        if not name or not workflow_definition:
            return jsonify({'error': 'Name and workflow definition are required'}), 400
        
        workflow_id = workflow_engine.create_workflow(
            name=name,
            description=data.get('description'),
            user_id=user_id,
            workflow_definition=workflow_definition,
            project_id=data.get('project_id')
        )
        
        return jsonify({
            'status': 'success',
            'workflow_id': workflow_id
        }), 201
        
    except Exception as e:
        logger.error(f"Workflow creation error: {str(e)}")
        return jsonify({'error': 'Workflow creation failed'}), 500

@app.route('/api/workflows/<workflow_id>/execute', methods=['POST'])
@jwt_required()
@limiter.limit("10 per hour")
def execute_workflow(workflow_id):
    """Execute a workflow"""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        input_data = data.get('input_data', {})
        
        result = workflow_engine.execute_workflow(workflow_id, input_data, user_id)
        
        return jsonify({
            'status': 'success',
            'result': result
        })
        
    except Exception as e:
        logger.error(f"Workflow execution error: {str(e)}")
        return jsonify({'error': 'Workflow execution failed'}), 500

@app.route('/api/workflow-templates', methods=['GET'])
@jwt_required()
def get_workflow_templates():
    """Get available workflow templates"""
    templates = [
        {
            'id': 'basic_analysis',
            'name': 'Basic Genomic Analysis',
            'description': 'Fetch data, run analysis, generate visualization',
            'steps': [
                {'type': 'data_fetch', 'name': 'Fetch Genomic Data'},
                {'type': 'analysis', 'name': 'Run ML Analysis'},
                {'type': 'visualization', 'name': 'Generate Plots'},
                {'type': 'export', 'name': 'Export Results'}
            ]
        },
        {
            'id': 'literature_review',
            'name': 'Literature Review Pipeline',
            'description': 'Search literature, summarize, generate hypotheses',
            'steps': [
                {'type': 'literature_search', 'name': 'Search PubMed'},
                {'type': 'summarization', 'name': 'Generate Summaries'},
                {'type': 'hypothesis_generation', 'name': 'Generate Hypotheses'},
                {'type': 'export', 'name': 'Export Report'}
            ]
        }
    ]
    
    return jsonify({
        'templates': templates,
        'total': len(templates)
    })

@app.route('/api/data-sources', methods=['POST'])
@jwt_required()
def register_data_source():
    """Register a new data source"""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        name = data.get('name')
        data_type = data.get('data_type')
        source_format = data.get('source_format')
        file_path = data.get('file_path')
        
        if not all([name, data_type, source_format, file_path]):
            return jsonify({'error': 'All fields are required'}), 400
        
        source_id = multimodal_engine.register_data_source(
            name=name,
            data_type=data_type,
            source_format=source_format,
            file_path=file_path,
            metadata=data.get('metadata')
        )
        
        return jsonify({
            'status': 'success',
            'data_source_id': source_id
        }), 201
        
    except Exception as e:
        logger.error(f"Data source registration error: {str(e)}")
        return jsonify({'error': 'Data source registration failed'}), 500

@app.route('/api/data-integration', methods=['POST'])
@jwt_required()
def create_data_integration():
    """Create multi-modal data integration"""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        name = data.get('name')
        data_source_ids = data.get('data_source_ids', [])
        
        if not name or not data_source_ids:
            return jsonify({'error': 'Name and data source IDs are required'}), 400
        
        integration_id = multimodal_engine.create_integration(
            name=name,
            data_source_ids=data_source_ids,
            integration_method=data.get('integration_method', 'concatenation')
        )
        
        return jsonify({
            'status': 'success',
            'integration_id': integration_id
        }), 201
        
    except Exception as e:
        logger.error(f"Data integration error: {str(e)}")
        return jsonify({'error': 'Data integration failed'}), 500

@app.route('/api/compliance/reports', methods=['POST'])
@jwt_required()
def generate_compliance_report():
    """Generate compliance report"""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        analysis_id = data.get('analysis_id')
        framework_type = data.get('framework_type')
        
        if not analysis_id or not framework_type:
            return jsonify({'error': 'Analysis ID and framework type are required'}), 400
        
        result = regulatory_engine.generate_compliance_report(analysis_id, framework_type)
        
        return jsonify({
            'status': 'success',
            'result': result
        })
        
    except Exception as e:
        logger.error(f"Compliance report error: {str(e)}")
        return jsonify({'error': 'Compliance report generation failed'}), 500

@app.route('/api/cloud/scale', methods=['POST'])
@jwt_required()
@limiter.limit("5 per hour")
def scale_analysis():
    """Scale analysis to cloud instances"""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        analysis_id = data.get('analysis_id')
        target_instances = data.get('target_instances', 2)
        
        if not analysis_id:
            return jsonify({'error': 'Analysis ID is required'}), 400
        
        result = cloud_engine.scale_analysis(analysis_id, target_instances)
        
        return jsonify({
            'status': 'success',
            'result': result
        })
        
    except Exception as e:
        logger.error(f"Cloud scaling error: {str(e)}")
        return jsonify({'error': 'Cloud scaling failed'}), 500

@socketio.on('join_session')
def handle_join_session(data):
    """Handle user joining collaboration session"""
    session_id = data.get('session_id')
    user_id = data.get('user_id')
    
    if session_id and user_id:
        join_room(session_id)
        collaboration_engine.join_session(session_id, user_id)
        
        emit('user_joined', {
            'user_id': user_id,
            'session_id': session_id,
            'timestamp': datetime.utcnow().isoformat()
        }, room=session_id)

@socketio.on('leave_session')
def handle_leave_session(data):
    """Handle user leaving collaboration session"""
    session_id = data.get('session_id')
    user_id = data.get('user_id')
    
    if session_id and user_id:
        leave_room(session_id)
        collaboration_engine.leave_session(session_id, user_id)
        
        emit('user_left', {
            'user_id': user_id,
            'session_id': session_id,
            'timestamp': datetime.utcnow().isoformat()
        }, room=session_id)

@socketio.on('analysis_update')
def handle_analysis_update(data):
    """Handle real-time analysis updates"""
    session_id = data.get('session_id')
    analysis_data = data.get('analysis_data')
    user_id = data.get('user_id')
    
    if session_id and analysis_data:
        emit('analysis_updated', {
            'user_id': user_id,
            'analysis_data': analysis_data,
            'timestamp': datetime.utcnow().isoformat()
        }, room=session_id, include_self=False)

@socketio.on('comment_added')
def handle_comment_added(data):
    """Handle new comment in collaboration session"""
    session_id = data.get('session_id')
    comment_data = data.get('comment_data')
    user_id = data.get('user_id')
    
    if session_id and comment_data:
        comment = Comment(
            user_id=user_id,
            project_id=comment_data.get('project_id'),
            analysis_id=comment_data.get('analysis_id'),
            content=comment_data.get('content'),
            comment_type=comment_data.get('type', 'general')
        )
        db.session.add(comment)
        db.session.commit()
        
        emit('comment_received', {
            'comment_id': comment.id,
            'user_id': user_id,
            'content': comment.content,
            'timestamp': comment.created_at.isoformat()
        }, room=session_id)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)

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
        