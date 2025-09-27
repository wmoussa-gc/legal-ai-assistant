#!/usr/bin/env python3
"""
Create a simplified legal rule system for testing.
"""

import sys
from pathlib import Path

# Add the backend to Python path  
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from app.services.scasp_engine import ScaspEngine

def create_simplified_legal_rules():
    """Create simplified legal rules that work with s(CASP)."""
    
    legal_program = """
% Legal Categories
person(citizen).
person(adult).
government_institution(health_canada).
government_institution(revenue_agency).

% Legal Facts  
canadian_citizen(citizen).
age_requirement(adult, 18).
access_right(citizen, government_record).

% Access to Information Rules
can_request_records(Person, Institution) :-
    canadian_citizen(Person),
    government_institution(Institution).

% Health Canada specific rules
health_canada_request(Person) :-
    canadian_citizen(Person),
    government_institution(health_canada).

% General eligibility
eligible_for_access(Person) :-
    canadian_citizen(Person).
"""
    
    return legal_program

def test_legal_queries():
    """Test various legal queries."""
    
    engine = ScaspEngine()
    if not engine.scasp_path:
        print("s(CASP) not found")
        return
    
    program = create_simplified_legal_rules()
    print("Simplified Legal Rule System:")
    print("=" * 50)
    print(program)
    print("=" * 50)
    
    # Test queries
    queries = [
        "can_request_records(citizen, health_canada)",
        "health_canada_request(citizen)", 
        "eligible_for_access(citizen)",
        "canadian_citizen(X)"
    ]
    
    for query in queries:
        print(f"\nTesting: {query}")
        result = engine.query(program, query)
        
        if result.success:
            print(f"  ✅ SUCCESS - Found {len(result.answers)} answer(s)")
            for i, answer in enumerate(result.answers[:3]):  # Show first 3
                if answer.solution:
                    print(f"    {i+1}: {answer.solution}")
                else:
                    print(f"    {i+1}: Yes (no variables to bind)")
        else:
            print(f"  ❌ FAILED: {result.error_message}")

if __name__ == "__main__":
    test_legal_queries()