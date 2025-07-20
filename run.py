#!/usr/bin/env python3
"""
BioCheAI Enhanced - Startup Script
"""

import os
import sys
from app import app, db

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
    
    print("🌐 Starting Flask server...")
    print("📡 Data fetching from NCBI, Ensembl, UniProt, GenBank, PubMed enabled")
    print("🛡️ AI Policing and Auto-Repair systems active")
    print("🔗 API available at: http://localhost:5000/api")
    print("📚 Documentation: http://localhost:5000/api/data/repositories")
    
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5000,
        threaded=True
    )

if __name__ == "__main__":
    main()
