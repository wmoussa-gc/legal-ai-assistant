#!/usr/bin/env python3
"""
Test demonstrating the missing facts issue in the Legal AI Assistant.

The system has legal RULES but no FACTS about the specific scenario being queried.
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from backend.app.services.blawx_parser import BlawxParser
from backend.app.services.scasp_engine import ScaspEngine


def test_without_facts():
    """Demonstrate that queries fail without facts."""
    print("=" * 80)
    print("TEST 1: Query WITHOUT facts (current problem)")
    print("=" * 80)
    
    # Load the Wills Act document
    parser = BlawxParser()
    doc = parser.parse_file("data/admin_wills-act.blawx")
    
    print(f"\n✅ Loaded document: {doc.name}")
    print(f"   - Provisions: {len(doc.provisions)}")
    print(f"   - Rules: {len(doc.scasp_rules)}")
    
    # Get the rules (but no facts about a specific person)
    rules_program = parser.format_scasp_program(doc.scasp_rules)
    
    print(f"\n📋 Rules loaded (first 500 chars):")
    print(rules_program[:500])
    print("...")
    
    # Try to query: "Can John make a will?"
    query = "person(john), holds(wa_1, eligible, john)"
    
    print(f"\n❓ Query: {query}")
    print("   Translation: 'Can John make a will?'")
    
    engine = ScaspEngine()
    result = engine.query(rules_program, query, timeout=10)
    
    print(f"\n❌ Result: SUCCESS={result.success}")
    if not result.success:
        print(f"   Error: {result.error_message}")
    print("\n💡 PROBLEM: We have RULES but no FACTS about John!")
    print("   We need to tell the system: john is a person, john is 20 years old, etc.")


def test_with_facts():
    """Demonstrate that queries work when facts are provided."""
    print("\n\n" + "=" * 80)
    print("TEST 2: Query WITH facts (the solution)")
    print("=" * 80)
    
    # Load the Wills Act document
    parser = BlawxParser()
    doc = parser.parse_file("data/admin_wills-act.blawx")
    
    # Get the rules
    rules_program = parser.format_scasp_program(doc.scasp_rules)
    
    # ADD FACTS about the specific scenario
    scenario_facts = """
% Facts about our specific scenario
person(john).
age(john, 20).

% Connect to Blawx's representation
holds(user, person, john).

% Define eligible predicate simply
eligible(Person) :- 
    person(Person), 
    age(Person, Age), 
    Age >= 18.
"""
    
    # Combine rules with facts
    complete_program = scenario_facts + "\n" + rules_program
    
    print(f"\n✅ Added scenario facts:")
    print(scenario_facts)
    
    # Now query
    query = "eligible(john)"
    
    print(f"\n❓ Query: {query}")
    print("   Translation: 'Is John eligible to make a will?'")
    
    engine = ScaspEngine()
    result = engine.query(complete_program, query, timeout=10)
    
    print(f"\n✅ Result: SUCCESS={result.success}")
    if result.success:
        print(f"   Answers: {len(result.answers)}")
        for i, answer in enumerate(result.answers):
            print(f"\n   Answer {i+1}:")
            print(f"   - Solution: {answer.solution}")
            print(f"   - Confidence: {answer.confidence}")
            print(f"   - Justification:")
            for j, step in enumerate(answer.justification[:5]):  # First 5 steps
                print(f"     {j+1}. {step}")


def test_simple_example():
    """Test with a completely simplified example."""
    print("\n\n" + "=" * 80)
    print("TEST 3: Simplified example")
    print("=" * 80)
    
    # Very simple legal rule
    simple_program = """
% Legal rule: A person 18 or older can make a will
can_make_will(Person) :-
    person(Person),
    age(Person, Age),
    Age >= 18.

% Facts about John
person(john).
age(john, 20).

% Facts about Sarah (too young)
person(sarah).
age(sarah, 16).
"""
    
    print("📋 Simple legal program:")
    print(simple_program)
    
    engine = ScaspEngine()
    
    # Test 1: Can John make a will?
    print("\n❓ Query 1: can_make_will(john)")
    result1 = engine.query(simple_program, "can_make_will(john)", timeout=5)
    print(f"   Result: SUCCESS={result1.success}")
    
    # Test 2: Can Sarah make a will?
    print("\n❓ Query 2: can_make_will(sarah)")
    result2 = engine.query(simple_program, "can_make_will(sarah)", timeout=5)
    print(f"   Result: SUCCESS={result2.success}")
    print(f"   (Should be false or no answer because Sarah is 16)")


def main():
    """Run all tests."""
    print("\n" + "🔍 " * 20)
    print("DEMONSTRATING THE MISSING FACTS PROBLEM")
    print("🔍 " * 20)
    
    test_without_facts()
    test_with_facts()
    test_simple_example()
    
    print("\n\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print("""
The legal AI assistant has RULES (from .blawx files) but needs FACTS about
the specific scenario in each user query.

For example:
- User asks: "Can a 20-year-old make a will?"
- System has: RULE "a person 18+ can make a will"
- System needs: FACTS "john is a person", "john is 20 years old"

THE SOLUTION:
1. Extract entities and values from the user's natural language question
2. Generate Prolog facts that represent the scenario
3. Combine these facts with the legal rules
4. Query the combined program

This is what the LLM service should do automatically!
""")


if __name__ == "__main__":
    main()
