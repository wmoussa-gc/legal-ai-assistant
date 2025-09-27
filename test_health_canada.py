#!/usr/bin/env python3
"""
Simple test to reproduce the exact s(CASP) syntax error.
"""

import os
import sys
from pathlib import Path

# Add the backend to Python path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from app.services.blawx_parser import BlawxParser
from app.services.scasp_engine import ScaspEngine

def reproduce_error():
    """Reproduce the exact error reported."""
    parser = BlawxParser()
    
    # Load the documents
    data_dir = Path("data")
    documents = []
    
    for blawx_file in data_dir.glob("*.blawx"):
        try:
            doc = parser.parse_file(str(blawx_file))
            documents.append(doc)
            print(f"Loaded: {doc.name}")
        except Exception as e:
            print(f"Failed to load {blawx_file}: {e}")
    
    # Find relevant rules for the Health Canada query
    query_terms = ['Canadian', 'citizen', 'request', 'records', 'Health', 'Canada']
    all_rules = []
    
    for doc in documents:
        relevant_rules = parser.extract_facts_for_query(doc, query_terms)
        all_rules.extend(relevant_rules)
    
    if all_rules:
        program = parser.format_scasp_program(all_rules)
        print(f"\n=== Generated Program ===")
        print(f"Program length: {len(program)} characters")
        
        # Save to file for inspection
        temp_file = Path("/tmp/debug_health_canada.pl")
        with open(temp_file, 'w') as f:
            f.write(program)
        
        print(f"Program saved to: {temp_file}")
        
        # Check specific lines around where the error might be
        lines = program.split('\n')
        if len(lines) >= 30:
            print(f"\n=== Lines 20-30 ===")
            for i, line in enumerate(lines[19:30], 20):
                char_count = len(line)
                print(f"{i:2d}: {line} [len={char_count}]")
                if i == 26:
                    print(f"    Character 71: '{line[70] if len(line) > 70 else 'N/A'}'")
        
        # Test with s(CASP)
        engine = ScaspEngine()
        if engine.scasp_path:
            try:
                result = engine.query(program, "user_query('Can_a_Canadian_citizen_request_records_from_Health_Canada?')")
                print(f"\ns(CASP) Result:")
                print(f"Success: {result.success}")
                if not result.success:
                    print(f"Error: {result.error_message}")
            except Exception as e:
                print(f"Exception during query: {e}")
        else:
            print("s(CASP) not available")
    else:
        print("No relevant rules found")

if __name__ == "__main__":
    reproduce_error()