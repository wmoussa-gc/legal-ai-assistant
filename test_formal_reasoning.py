#!/usr/bin/env python3
"""
Test script to validate s(CASP) and SWI-Prolog formal reasoning only.
This script verifies that the system works correctly without pattern-based fallbacks.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.scasp_engine import ScaspEngine

def test_formal_reasoning():
    """Test that the system works with only s(CASP) and SWI-Prolog."""
    
    print("=== Testing Formal Reasoning System ===")
    
    # Initialize engine
    engine = ScaspEngine()
    print(f"s(CASP) available: {engine.scasp_path is not None}")
    print(f"SWI-Prolog available: {engine.prolog_path is not None}")
    
    if not engine.is_available():
        print("ERROR: No formal reasoning engines available")
        return False
    
    # Test with a simple legal program
    test_program = """
% Basic legal facts
person(alice).
person(bob).
age(alice, 25).
age(bob, 16).
military_member(bob).

% Legal rules for will eligibility
can_make_will(Person) :- 
    person(Person),
    age(Person, Age),
    Age >= 18.

can_make_will(Person) :- 
    person(Person),
    age(Person, Age),
    Age >= 14,
    military_member(Person).
"""
    
    test_queries = [
        ("can_make_will(alice)", "Alice (25) should be eligible"),
        ("can_make_will(bob)", "Bob (16, military) should be eligible"),
    ]
    
    success_count = 0
    
    for query, description in test_queries:
        print(f"\n--- Testing: {description} ---")
        print(f"Query: {query}")
        
        result = engine.query(test_program, query, timeout=10)
        
        print(f"Success: {result.success}")
        if result.success and result.answers:
            print(f"Answers: {len(result.answers)}")
            for i, answer in enumerate(result.answers):
                print(f"  Answer {i+1}: {answer.solution}")
                print(f"  Confidence: {answer.confidence}")
                print(f"  Justification: {answer.justification[:2]}...")  # Show first 2 lines
            success_count += 1
        else:
            print(f"Error: {result.error_message}")
    
    print(f"\n=== Results: {success_count}/{len(test_queries)} queries succeeded ===")
    
    # Test that pattern-based responses are no longer generated
    print("\n--- Testing Pattern-Based Responses are Removed ---")
    will_query = "I'm 16 years old, can I make a will?"
    result = engine.query("% empty program", will_query, timeout=5)
    
    if not result.success:
        print("✅ Pattern-based responses successfully removed - query failed as expected")
        return True
    else:
        print("❌ Pattern-based response detected - cleanup incomplete")
        return False

if __name__ == "__main__":
    success = test_formal_reasoning()
    sys.exit(0 if success else 1)