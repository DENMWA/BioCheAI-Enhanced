#!/usr/bin/env python3
"""
Script to check the database status and debug project fetching issues
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User, Project

def check_database():
    with app.app_context():
        print("=== Database Status Check ===")
        
        demo_user = User.query.filter_by(username='demo').first()
        if demo_user:
            print(f"✅ Demo user found: {demo_user.username} (ID: {demo_user.id})")
        else:
            print("❌ Demo user not found!")
            return
        
        all_projects = Project.query.all()
        print(f"\n📊 Total projects in database: {len(all_projects)}")
        
        for project in all_projects:
            print(f"  - Project: {project.name} (ID: {project.id})")
            print(f"    Owner ID: {project.owner_id}")
            print(f"    Created: {project.created_at}")
            print(f"    Public: {project.is_public}")
        
        demo_projects = Project.query.filter_by(owner_id=demo_user.id).all()
        print(f"\n👤 Projects owned by demo user: {len(demo_projects)}")
        
        for project in demo_projects:
            print(f"  - {project.name}: {project.description}")
        
        print(f"\n🔍 Testing API logic for user {demo_user.id}:")
        
        user_projects = Project.query.filter_by(owner_id=demo_user.id).all()
        public_projects = Project.query.filter_by(is_public=True).all()
        
        all_accessible = list({p.id: p for p in user_projects + public_projects}.values())
        
        print(f"  - User's own projects: {len(user_projects)}")
        print(f"  - Public projects: {len(public_projects)}")
        print(f"  - Total accessible: {len(all_accessible)}")
        
        for project in all_accessible:
            print(f"    * {project.name} (Owner: {project.owner_id}, Public: {project.is_public})")

if __name__ == '__main__':
    check_database()
