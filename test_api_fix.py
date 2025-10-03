#!/usr/bin/env python3
"""
Test the API endpoint with a simple query to verify the fix.
"""

import requests
import json

def test_query(query_text):
    """Test a query against the API."""
    url = "http://localhost:8000/query"
    
    payload = {
        "query": query_text,
        "context": None,
        "user_location": None
    }
    
    print("=" * 80)
    print(f"Testing query: {query_text}")
    print("=" * 80)
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ SUCCESS!")
            print(f"Answer: {result.get('answer', 'N/A')[:200]}...")
            print(f"Confidence: {result.get('confidence', 'N/A')}")
            print(f"Confidence Level: {result.get('confidence_level', 'N/A')}")
            
            if result.get('formal_verification'):
                fv = result['formal_verification']
                print(f"\nFormal Verification:")
                print(f"  Query: {fv.get('query_executed', 'N/A')}")
                print(f"  Success: {fv.get('success', 'N/A')}")
                if fv.get('error_message'):
                    print(f"  Error: {fv['error_message'][:200]}")
        else:
            print(f"\n❌ FAILED!")
            print(f"Response: {response.text[:500]}")
            
    except requests.exceptions.RequestException as e:
        print(f"\n❌ REQUEST FAILED: {e}")


def main():
    print("\n" + "🧪 " * 20)
    print("TESTING API ENDPOINT AFTER FIX")
    print("🧪 " * 20)
    
    test_queries = [
        "Can a 20-year-old make a will?",
        "Can a 16-year-old make a will?",
        "Can an active military member aged 15 make a will?",
        "What are the requirements for making a will?",
    ]
    
    for query in test_queries:
        test_query(query)
        print("\n")
    
    print("\n" + "=" * 80)
    print("DONE")
    print("=" * 80)


if __name__ == "__main__":
    main()
