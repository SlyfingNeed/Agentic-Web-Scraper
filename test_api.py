#!/usr/bin/env python3
"""
Test script for the AI-Powered Web Scraper API
"""

import asyncio
import httpx
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_api():
    """Test the API endpoints"""
    
    # API base URL
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient() as client:
        print("Testing AI-Powered Web Scraper API")
        print("=" * 50)
        
        # Test 1: Health check
        print("\n1. Testing health check...")
        try:
            response = await client.get(f"{base_url}/health")
            if response.status_code == 200:
                health_data = response.json()
                print(f"Health check passed: {health_data}")
            else:
                print(f"Health check failed: {response.status_code}")
        except Exception as e:
            print(f"Health check error: {e}")
        
        # Test 2: Root endpoint
        print("\n2. Testing root endpoint...")
        try:
            response = await client.get(f"{base_url}/")
            if response.status_code == 200:
                print(f"Root endpoint: {response.json()}")
            else:
                print(f"Root endpoint failed: {response.status_code}")
        except Exception as e:
            print(f"Root endpoint error: {e}")
        
        # Test 3: Scraping endpoint
        print("\n3. Testing scraping endpoint...")
        
        # Test queries
        test_queries = [
            "Get latest tech news from TechCrunch",
            "Scrape Bitcoin articles from CNN",
            "Get trending posts from Reddit"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n   Test {i}: {query}")
            try:
                payload = {"query": query}
                response = await client.post(
                    f"{base_url}/scrape",
                    json=payload,
                    timeout=60.0  # Longer timeout for scraping
                )
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"   Success: {data.get('message', 'No message')}")
                    print(f"   Items extracted: {len(data.get('data', []))}")
                    
                    # Show first item if available
                    if data.get('data'):
                        first_item = data['data'][0]
                        print(f"   Sample: {first_item.get('title', 'No title')[:50]}...")
                else:
                    print(f"   Failed: {response.status_code}")
                    print(f"   Error: {response.text}")
                    
            except Exception as e:
                print(f"   Error: {e}")

def check_environment():
    """Check if environment is properly set up"""
    print("Environment Check")
    print("=" * 30)
    
    # Check Gemini API key
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key and api_key != "your_gemini_api_key_here":
        print("Gemini API key is set")
    else:
        print("Gemini API key not found or not set properly")
        print("   Please set GEMINI_API_KEY in your .env file")
    
    # Check if required files exist
    required_files = ["main.py", "agent.py", "browser.py", "scraper.py", "requirements.txt"]
    for file in required_files:
        if os.path.exists(file):
            print(f"{file} exists")
        else:
            print(f"{file} missing")

if __name__ == "__main__":
    print("AI-Powered Web Scraper API Test Suite")
    print("=" * 60)
    
    # Check environment first
    check_environment()
    
    print("\n" + "=" * 60)
    print("Make sure the API is running before running tests!")
    print("   Run: python main.py")
    print("=" * 60)
    
    # Ask user if they want to run the tests
    response = input("\nDo you want to run the API tests? (y/n): ").lower().strip()
    
    if response in ['y', 'yes']:
        asyncio.run(test_api())
    else:
        print("Tests skipped. Run the script again when the API is ready.") 