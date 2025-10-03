# Architecture: Why We Need Facts (But Not Hardcoded Patterns)

## The Correct Flow

```
User Query (Natural Language)
    ↓
LLM Analysis (GPT-4/Claude)
    ↓
Scenario Facts (Prolog) + Legal Rules (from .blawx)
    ↓
s(CASP) / SWI-Prolog Reasoning Engine
    ↓
Verified Answer + Proof
```

## What Each Component Should Do

### 1. **LLM (GPT-4/Azure OpenAI)** - The "Translator"

**Role:** Translate natural language to formal logic

**Input:**

```
"Can a 20-year-old make a will?"
```

**Output (from LLM):**

```json
{
  "entities": ["person"],
  "prolog_facts": ["person(user_person).", "age(user_person, 20)."],
  "query_predicate": "eligible(user_person)",
  "explanation": "User is asking about eligibility for a 20-year-old to make a will"
}
```

**Key Point:** The LLM uses its language understanding, NOT hardcoded patterns!

### 2. **Reasoning Engine (s(CASP)/Prolog)** - The "Verifier"

**Role:** Prove/disprove based on formal logic

**Input:**

```prolog
% Scenario facts (from LLM)
person(user_person).
age(user_person, 20).

% Legal rules (from .blawx files)
eligible(Person) :-
    person(Person),
    age(Person, Age),
    Age >= 18.
```

**Process:** Uses logical inference:

1. Is `eligible(user_person)` true?
2. Check: Is `person(user_person)` true? → YES (fact)
3. Check: Is `age(user_person, Age)` true? → YES, Age = 20
4. Check: Is `20 >= 18`? → YES
5. Therefore: `eligible(user_person)` is TRUE ✓

**Output:** Proof with confidence + justification

### 3. **LLM Again** - The "Explainer"

**Role:** Translate formal proof back to natural language

**Input:** Formal proof from reasoning engine
**Output:** "Yes, a 20-year-old can make a will because..."

## Why Pattern Matching is Wrong

The code I added has this:

```python
def _fallback_extract_facts(self, query: str):
    if 'military' in query_lower:
        prolog_facts.append("military(user_person).")
    if '20-year-old' in query:
        prolog_facts.append("age(user_person, 20).")
```

**Problems:**

1. ❌ Hardcoded for specific phrases
2. ❌ Won't work for "twenty year old" or "20 years of age"
3. ❌ Can't handle complex queries like "Can someone born in 2005 make a will in 2025?"
4. ❌ Doesn't scale to other legal domains

## The Right Approach: LLM Does the Translation

The LLM prompt should be:

```python
prompt = f"""
You are a legal reasoning assistant. Extract facts from this query and convert to Prolog.

Query: "{user_query}"

Available legal concepts: {available_predicates}

Think step by step:
1. What entities are involved? (person, document, organization)
2. What attributes do they have? (age, status, role)
3. What relationships exist? (has, can, must)
4. What is being asked? (eligibility, permission, requirement)

Convert to Prolog facts and query predicate.

Examples:
- "Can a 20-year-old make a will?"
  → Facts: person(p1). age(p1, 20).
  → Query: eligible_for_will(p1)

- "Can a Canadian born in 2000 make a will in 2025?"
  → Facts: person(p1). born_year(p1, 2000). current_year(2025).
  → Query: eligible_for_will(p1)

Now analyze: {user_query}
"""
```

**The LLM figures out:**

- How to extract "20-year-old" → `age(p, 20)`
- How to extract "military member" → `military(p)`
- How to handle "born in 2000" → `born_year(p, 2000)` and calculate age
- How to understand different phrasings

## Current Implementation Status

### ✅ What We Have:

1. LLM integration (Azure OpenAI)
2. Fact extraction prompt template
3. Reasoning engine integration
4. Complete workflow in `/query` endpoint

### ⚠️ The Issue You Identified:

The **fallback pattern matching** (`_fallback_extract_facts`) is used when:

- LLM API is unavailable
- LLM response parsing fails
- Development/testing without API keys

### 🎯 What Should Happen:

In production with LLM available:

1. User query → LLM (no patterns!)
2. LLM returns structured facts
3. Facts + Rules → Reasoning engine
4. Proof → LLM translates to natural language

## Why the Fallback Exists

The pattern matching is a **safety net** for:

- **Development:** Testing without API costs
- **Reliability:** System works if OpenAI is down
- **Demos:** Can show the concept without requiring API keys

But you're RIGHT: **The LLM should be doing this work, not hardcoded patterns!**

## The Ideal Architecture

```
┌─────────────────────────────────────────────────────┐
│  User: "Can a 20-year-old make a will?"            │
└─────────────────┬───────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────┐
│  LLM (GPT-4): Understand natural language           │
│  • Extract: person with age 20                      │
│  • Generate: person(p). age(p, 20).                 │
│  • Query: eligible(p)                               │
└─────────────────┬───────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────┐
│  Reasoning Engine: Apply formal logic               │
│  • Has rule: eligible(X) :- age(X,A), A >= 18      │
│  • Proves: age(p,20), 20 >= 18 → eligible(p) TRUE  │
└─────────────────┬───────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────┐
│  LLM (GPT-4): Explain the proof                     │
│  "Yes, because section 1 of the Wills Act states..." │
└─────────────────────────────────────────────────────┘
```

## Conclusion

You're absolutely correct! The system should rely on:

1. **LLM's language understanding** (not regex patterns)
2. **Reasoning engine's logical inference** (not imperative code)
3. **Legal rules from .blawx files** (not hardcoded logic)

The pattern matching is just a fallback. The real power comes from:

- **LLM:** Understands "20-year-old" in any phrasing
- **Reasoning Engine:** Proves eligibility from rules
- **No hardcoding:** New legal rules work automatically

The architecture is sound—we just need to ensure the LLM is doing the heavy lifting, not the fallback patterns!
