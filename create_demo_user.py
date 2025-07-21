#!/usr/bin/env python3
"""
Script to create a demo user account for testing BioCheAI Enhanced
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User
from werkzeug.security import generate_password_hash

def create_demo_user():
    with app.app_context():
        existing_user = User.query.filter_by(username='demo').first()
        if existing_user:
            print("Demo user already exists!")
            print("Username: demo")
            print("Password: demo123")
            return
        
        demo_user = User(
            username='demo',
            email='demo@biocheai.com',
            first_name='Demo',
            last_name='User',
            password_hash=generate_password_hash('demo123')
        )
        
        db.session.add(demo_user)
        db.session.commit()
        
        print("✅ Demo user created successfully!")
        print("Username: demo")
        print("Password: demo123")
        print("Email: demo@biocheai.com")
        print("\nYou can now login with these credentials to test the Gantt charts!")

if __name__ == '__main__':
    create_demo_user()
