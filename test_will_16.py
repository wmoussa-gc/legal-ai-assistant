#!/usr/bin/env python3
"""
Test the will act scenario with a 16-year-old query.
"""

import sys
from pathlib import Path

# Add the backend to Python path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from app.services.blawx_parser import BlawxParser
from app.services.scasp_engine import ScaspEngine

def test_will_act_16_year_old():
    """Test the specific 16-year-old will scenario."""
    parser = BlawxParser()
    
    # Load the Wills Act document
    try:
        wills_doc = parser.parse_file("data/admin_wills-act.blawx")
        print(f"Loaded: {wills_doc.name}")
        print(f"Provisions: {len(wills_doc.provisions)}")
        print(f"Rules: {len(wills_doc.scasp_rules)}")
        
        # Print some provisions to understand the content
        print("\n=== Legal Provisions ===")
        for i, provision in enumerate(wills_doc.provisions[:5]):
            print(f"{i+1}. {provision.title}: {provision.text}")
        
        # Print some s(CASP) rules to understand the logic
        print(f"\n=== s(CASP) Rules (first 10) ===")
        for i, rule in enumerate(wills_doc.scasp_rules[:10]):
            print(f"{i+1}. {rule.rule_type}: {rule.rule_text[:80]}...")
        
        # Look for age-related rules
        age_rules = [rule for rule in wills_doc.scasp_rules if 'age' in rule.rule_text.lower() or '16' in rule.rule_text or '18' in rule.rule_text]
        print(f"\n=== Age-related Rules ({len(age_rules)}) ===")
        for rule in age_rules:
            print(f"- {rule.rule_type}: {rule.rule_text}")
        
        # Test query processing for 16-year-old
        query_terms = ['16', 'years', 'old', 'make', 'will', 'military', 'active']
        relevant_rules = parser.extract_facts_for_query(wills_doc, query_terms)
        
        print(f"\n=== Relevant Rules for '16 year old will' ({len(relevant_rules)}) ===")
        for rule in relevant_rules:
            print(f"- {rule.rule_type}: {rule.rule_text[:100]}...")
        
        if relevant_rules:
            program = parser.format_scasp_program(relevant_rules)
            
            # Save program for inspection
            with open("/tmp/wills_act_16.pl", "w") as f:
                f.write(program)
            print(f"\nProgram saved to: /tmp/wills_act_16.pl")
            print(f"Program length: {len(program)} characters")
            
            # Test with s(CASP)
            engine = ScaspEngine()
            if engine.scasp_path:
                # Test different query formulations
                queries = [
                    "eligible(sixteen_year_old)",
                    "can_make_will(person_aged_16)",
                    "military(person)",
                    "age(person, 16)"
                ]
                
                for query in queries:
                    print(f"\n--- Testing query: {query} ---")
                    result = engine.query(program, query, timeout=10)
                    print(f"Success: {result.success}")
                    if result.success and result.answers:
                        for i, answer in enumerate(result.answers):
                            print(f"  Answer {i+1}: {answer.solution}")
                            print(f"  Justification: {answer.justification}")
                            print(f"  Confidence: {answer.confidence}")
                    elif not result.success:
                        print(f"  Error: {result.error_message}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

def analyze_wills_act_logic():
    """Analyze the actual legal logic in the Wills Act."""
    print("\n" + "="*60)
    print("WILLS ACT LEGAL ANALYSIS")
    print("="*60)
    
    print("""
The Wills Act contains two key provisions:

1. "A person over the age of 18 may make a will."
2. "An active military member over the age of 14 may make a will."

For a 16-year-old:
- NOT eligible under rule 1 (need to be over 18)
- POTENTIALLY eligible under rule 2 (if active military AND over 14)

The system should ask: "Are you an active military member?"

If YES → Can make a will (high confidence)
If NO → Cannot make a will (high confidence)
If UNKNOWN → Lower confidence answer

The issue might be:
1. The s(CASP) rules don't properly encode this logic
2. The query doesn't match the predicate structure
3. The fallback system isn't handling this specific case well
""")

if __name__ == "__main__":
    test_will_act_16_year_old()
    analyze_wills_act_logic()