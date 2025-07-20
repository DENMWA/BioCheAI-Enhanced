#!/usr/bin/env python3
"""
Test script for BioCheAI enhanced features
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000/api"

def test_registration_and_login():
    """Test user registration and login"""
    print("🔐 Testing user registration and login...")
    
    register_data = {
        "username": "testuser",
        "email": "test@example.com", 
        "password": "testpass123",
        "first_name": "Test",
        "last_name": "User"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
    if response.status_code == 201:
        print("✅ User registration successful")
        token = response.json()['access_token']
        return token
    else:
        login_data = {
            "username": "testuser",
            "password": "testpass123"
        }
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            print("✅ User login successful")
            return response.json()['access_token']
        else:
            print(f"❌ Authentication failed: {response.text}")
            return None

def test_data_fetching(token):
    """Test data fetching from repositories"""
    print("\n📡 Testing data fetching...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    ncbi_data = {
        "repository": "ncbi",
        "params": {
            "term": "insulin human",
            "db": "protein",
            "retmax": 2
        }
    }
    
    response = requests.post(f"{BASE_URL}/data/fetch", json=ncbi_data, headers=headers)
    if response.status_code == 200:
        print("✅ NCBI data fetching successful")
        result = response.json()
        print(f"   Found {len(result['result']['data'])} sequences")
    else:
        print(f"❌ NCBI fetching failed: {response.text}")
    
    response = requests.get(f"{BASE_URL}/data/repositories", headers=headers)
    if response.status_code == 200:
        repos = response.json()['repositories']
        print(f"✅ Repository list retrieved: {len(repos)} repositories available")
    else:
        print(f"❌ Repository list failed: {response.text}")

def test_analysis_with_repair(token):
    """Test analysis creation with AI policing and repair"""
    print("\n🧬 Testing analysis with AI policing and repair...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    analysis_data = {
        "analysis_type": "dna",
        "title": "Test DNA Analysis",
        "data": {
            "sequence": "ATCGATCG",  # Short sequence (will trigger quality issues)
            "samples": 5,  # Small sample size (will trigger accuracy issues)
            "contact_email": "researcher@university.edu"  # PII (will trigger privacy issues)
        }
    }
    
    response = requests.post(f"{BASE_URL}/analysis", json=analysis_data, headers=headers)
    if response.status_code == 201:
        analysis_id = response.json()['analysis_id']
        print(f"✅ Analysis created: {analysis_id}")
        
        response = requests.get(f"{BASE_URL}/analysis/{analysis_id}", headers=headers)
        if response.status_code == 200:
            analysis = response.json()
            police_report = analysis.get('police_report', {})
            print(f"   Police status: {police_report.get('status', 'unknown')}")
            print(f"   Compliance score: {police_report.get('compliance_score', 0):.2f}")
            print(f"   Violations found: {len(police_report.get('violations', []))}")
            
            if police_report.get('status') == 'flagged':
                print("\n🔧 Testing manual repair...")
                response = requests.post(f"{BASE_URL}/analysis/{analysis_id}/repair", headers=headers)
                if response.status_code == 200:
                    repair_result = response.json()
                    new_score = repair_result['compliance_score']
                    print(f"✅ Repair successful - New compliance score: {new_score:.2f}")
                else:
                    print(f"❌ Repair failed: {response.text}")
        
    else:
        print(f"❌ Analysis creation failed: {response.text}")

def main():
    """Run all tests"""
    print("🚀 BioCheAI Enhanced Features Test Suite")
    print("=" * 50)
    
    token = test_registration_and_login()
    if not token:
        print("❌ Cannot proceed without authentication")
        return
    
    print("\n⚠️  Note: Data fetching tests require internet connection")
    print("⚠️  Server must be running on localhost:5000")
    
    try:
        test_data_fetching(token)
        
        test_analysis_with_repair(token)
        
        print("\n🎉 All tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Server not running. Start the server with: python app.py")
    except Exception as e:
        print(f"\n❌ Test error: {str(e)}")

if __name__ == "__main__":
    main()
