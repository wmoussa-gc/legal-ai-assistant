#!/usr/bin/env python3
"""
Debug script to test s(CASP) rule parsing and generation.
"""

import os
import sys
import tempfile
from pathlib import Path

# Add the backend to Python path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from app.services.blawx_parser import BlawxParser
from app.services.scasp_engine import ScaspEngine

def test_blawx_parsing():
    """Test parsing of .blawx files."""
    parser = BlawxParser()
    
    # Test with the existing file
    blawx_file = "data/admin_wills-act.blawx"
    
    try:
        print(f"Parsing {blawx_file}...")
        doc = parser.parse_file(blawx_file)
        
        print(f"Document: {doc.name}")
        print(f"Total rules: {len(doc.scasp_rules)}")
        
        # Show first few rules
        for i, rule in enumerate(doc.scasp_rules[:5]):
            print(f"\nRule {i+1} ({rule.rule_type}):")
            print(f"  Text: {rule.rule_text[:100]}...")
            print(f"  Variables: {rule.variables}")
            print(f"  Predicates: {rule.predicates}")
        
        # Test formatting
        print(f"\n=== Testing program formatting ===")
        program = parser.format_scasp_program(doc.scasp_rules)
        
        # Save to temp file to inspect
        temp_file = Path(tempfile.gettempdir()) / "debug_scasp_program.pl"
        with open(temp_file, 'w') as f:
            f.write(program)
        
        print(f"Program written to: {temp_file}")
        print(f"Program length: {len(program)} characters")
        print(f"First 500 chars:\n{program[:500]}")
        
        return doc, program
        
    except Exception as e:
        print(f"Error parsing file: {e}")
        import traceback
        traceback.print_exc()
        return None, None

def test_scasp_engine(program: str):
    """Test s(CASP) engine with the program."""
    if not program:
        return
        
    print(f"\n=== Testing s(CASP) Engine ===")
    
    engine = ScaspEngine()
    
    if not engine.scasp_path:
        print("s(CASP) not found, using mock engine")
        return
    
    # Try a simple query
    simple_query = "person(X)"
    
    try:
        result = engine.query(program, simple_query, timeout=10)
        print(f"Query: {simple_query}")
        print(f"Success: {result.success}")
        
        if result.success:
            print(f"Answers: {len(result.answers)}")
            for answer in result.answers:
                print(f"  Solution: {answer.solution}")
        else:
            print(f"Error: {result.error_message}")
            
    except Exception as e:
        print(f"Engine error: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main debug function."""
    print("=== Legal AI Assistant s(CASP) Debug ===")
    
    # Test parsing
    doc, program = test_blawx_parsing()
    
    # Test engine
    test_scasp_engine(program)

if __name__ == "__main__":
    main()