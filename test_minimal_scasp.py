#!/usr/bin/env python3
"""
Test s(CASP) with minimal program to ensure basic functionality.
"""

import sys
from pathlib import Path

# Add the backend to Python path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from app.services.scasp_engine import ScaspEngine

def test_minimal_scasp():
    """Test with a minimal s(CASP) program."""
    
    # Very simple program
    simple_program = """
% Facts
person(alice).
person(bob).
age(alice, 25).
age(bob, 16).

% Rules
adult(X) :- person(X), age(X, Age), Age >= 18.

% Query will be added by the engine
"""
    
    engine = ScaspEngine()
    
    if not engine.scasp_path:
        print("s(CASP) not found")
        return
    
    print("Testing minimal s(CASP) program...")
    print("Program:")
    print(simple_program)
    
    # Test query
    result = engine.query(simple_program.strip(), "adult(X)")
    
    print(f"\nQuery: adult(X)")
    print(f"Success: {result.success}")
    
    if result.success:
        print(f"Answers: {len(result.answers)}")
        for i, answer in enumerate(result.answers):
            print(f"  {i+1}: {answer.solution}")
    else:
        print(f"Error: {result.error_message}")

def test_with_blawx_predicates():
    """Test with some Blawx-style predicates."""
    
    blawx_program = """
% Simple Blawx-style program
blawx_category(person).
person(alice).
person(bob).

% Test eligibility
eligible(X) :- person(X).
"""
    
    engine = ScaspEngine()
    
    if not engine.scasp_path:
        print("s(CASP) not found")
        return
    
    print("\n" + "="*50)
    print("Testing Blawx-style predicates...")
    print("Program:")
    print(blawx_program)
    
    result = engine.query(blawx_program.strip(), "eligible(X)")
    
    print(f"\nQuery: eligible(X)")
    print(f"Success: {result.success}")
    
    if result.success:
        print(f"Answers: {len(result.answers)}")
        for i, answer in enumerate(result.answers):
            print(f"  {i+1}: {answer.solution}")
    else:
        print(f"Error: {result.error_message}")

if __name__ == "__main__":
    test_minimal_scasp()
    test_with_blawx_predicates()