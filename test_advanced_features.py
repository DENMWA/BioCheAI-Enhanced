#!/usr/bin/env python3
"""
Test script for BioCheAI advanced features
"""

import requests
import json

BASE_URL = "http://localhost:5000/api"

def test_advanced_features():
    """Test advanced features"""
    print("🧪 Testing BioCheAI Advanced Features")
    print("=" * 50)
    
    login_data = {"username": "testuser", "password": "testpass123"}
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if response.status_code != 200:
        print("❌ Login failed")
        return
    
    token = response.json()['access_token']
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n📚 Testing AI Literature Intelligence...")
    lit_search = {
        "query": "CRISPR gene editing",
        "sources": ["pubmed"],
        "max_results": 5
    }
    response = requests.post(f"{BASE_URL}/literature/search", json=lit_search, headers=headers)
    if response.status_code == 200:
        print("✅ Literature search successful")
        results = response.json()
        print(f"   Found {len(results.get('results', []))} papers")
    else:
        print(f"⚠️ Literature search: {response.status_code}")
    
    print("\n👥 Testing Collaboration Features...")
    project_data = {
        "name": "Test Research Project",
        "description": "Testing collaboration features",
        "is_public": False
    }
    response = requests.post(f"{BASE_URL}/projects", json=project_data, headers=headers)
    if response.status_code == 201:
        print("✅ Project creation successful")
        project = response.json()
        print(f"   Project ID: {project['project']['id']}")
    else:
        print(f"⚠️ Project creation: {response.status_code}")
    
    print("\n🔧 Testing No-Code Workflow Builder...")
    response = requests.get(f"{BASE_URL}/workflow-templates", headers=headers)
    if response.status_code == 200:
        templates = response.json()
        print("✅ Workflow templates retrieved")
        print(f"   Available templates: {len(templates.get('templates', []))}")
    else:
        print(f"⚠️ Workflow templates: {response.status_code}")
    
    print("\n📋 Testing Regulatory Compliance...")
    response = requests.get(f"{BASE_URL}/compliance/frameworks", headers=headers)
    if response.status_code == 200:
        frameworks = response.json()
        print("✅ Compliance frameworks retrieved")
        print(f"   Available frameworks: {len(frameworks.get('frameworks', []))}")
    else:
        print(f"⚠️ Compliance frameworks: {response.status_code}")
    
    print("\n🎉 Advanced features testing completed!")

if __name__ == "__main__":
    try:
        test_advanced_features()
    except requests.exceptions.ConnectionError:
        print("❌ Server not running. Start with: python run.py")
    except Exception as e:
        print(f"❌ Test error: {str(e)}")
