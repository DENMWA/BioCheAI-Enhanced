#!/usr/bin/env python3
"""
Script to create a demo project for testing Gantt chart functionality
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User, Project
from datetime import datetime

def create_demo_project():
    with app.app_context():
        demo_user = User.query.filter_by(username='demo').first()
        if not demo_user:
            print("❌ Demo user not found! Please run create_demo_user.py first.")
            return
        
        existing_project = Project.query.filter_by(name='Gantt Chart Demo Project').first()
        if existing_project:
            print("✅ Demo project already exists!")
            print(f"Project ID: {existing_project.id}")
            print(f"Project Name: {existing_project.name}")
            print(f"Owner: {existing_project.owner.username}")
            return
        
        demo_project = Project(
            name='Gantt Chart Demo Project',
            description='Demo project to test the Gantt chart and project management features in BioCheAI Enhanced platform.',
            owner_id=demo_user.id,
            is_public=False,
            created_at=datetime.utcnow()
        )
        
        db.session.add(demo_project)
        db.session.commit()
        
        print("✅ Demo project created successfully!")
        print(f"Project ID: {demo_project.id}")
        print(f"Project Name: {demo_project.name}")
        print(f"Owner: {demo_project.owner.username}")
        print(f"Description: {demo_project.description}")
        print("\nYou can now access the Gantt charts by:")
        print("1. Login with demo/demo123")
        print("2. Navigate to Projects")
        print("3. Click 'Manage' on the demo project to access Gantt charts!")

if __name__ == '__main__':
    create_demo_project()
