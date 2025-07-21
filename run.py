#!/usr/bin/env python3
"""
BioCheAI Enhanced - Startup Script
"""

import os
import sys
from app import app, db, socketio

def create_tables():
    """Create database tables"""
    with app.app_context():
        db.create_all()
        print("✅ Database tables created")

def main():
    """Main startup function"""
    print("🚀 Starting BioCheAI Enhanced Platform")
    print("=" * 50)
    
    create_tables()
    
    print("🌐 Starting Flask server with SocketIO...")
    print("📡 Data fetching from NCBI, Ensembl, UniProt, GenBank, PubMed enabled")
    print("🛡️ AI Policing and Auto-Repair systems active")
    print("🧠 AI Literature Intelligence with NLP models")
    print("👥 Real-time Collaboration with WebSocket support")
    print("🔧 No-Code Workflow Builder")
    print("🔗 Multi-Modal Data Integration")
    print("📋 Regulatory Compliance (GDPR, HIPAA, FDA, EMA)")
    print("☁️ Cloud Scalability (AWS, GCP, Azure)")
    print("🔗 API available at: http://localhost:5000/api")
    print("📚 Documentation: http://localhost:5000/api/data/repositories")
    
    socketio.run(
        app,
        debug=True,
        host='0.0.0.0',
        port=5000
    )

if __name__ == "__main__":
    main()
