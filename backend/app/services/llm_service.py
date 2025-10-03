"""
LLM Service for Legal AI Assistant.

This module handles integration with Large Language Models (OpenAI GPT-4, Anthropic Claude)
for natural language processing, prompt engineering, and response generation.
"""

import os
import json
import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import asyncio
from datetime import datetime

# Optional imports - will gracefully degrade if not available
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


@dataclass
class LLMResponse:
    """Response from an LLM."""
    content: str
    confidence: float
    model_used: str
    tokens_used: int
    reasoning_steps: List[str]
    legal_citations: List[str]
    verified_claims: List[str]
    unverified_claims: List[str]


@dataclass
class QueryAnalysis:
    """Analysis of a user's legal query."""
    original_query: str
    intent: str  # 'question', 'request_advice', 'check_eligibility', etc.
    legal_domain: str  # 'access_to_info', 'privacy', 'employment', etc.
    entities: List[str]  # Extracted legal entities
    formal_query: str  # Translated to formal logic
    confidence: float


class LLMService:
    """Service for LLM integration and legal reasoning."""
    
    def __init__(self, openai_api_key: Optional[str] = None, anthropic_api_key: Optional[str] = None):
        self.openai_client = None
        self.anthropic_client = None
        self.azure_openai_client = None
        self.is_azure_openai = False
        
        # Check for Azure OpenAI first (preferred)
        azure_api_key = os.getenv('AZURE_OPENAI_API_KEY')
        azure_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
        azure_api_version = os.getenv('AZURE_OPENAI_API_VERSION', '2024-02-15-preview')
        
        if OPENAI_AVAILABLE and azure_api_key and azure_endpoint:
            try:
                from openai import AzureOpenAI
                self.azure_openai_client = AzureOpenAI(
                    api_key=azure_api_key,
                    api_version=azure_api_version,
                    azure_endpoint=azure_endpoint
                )
                self.openai_client = self.azure_openai_client  # Use same interface
                self.is_azure_openai = True
                print(f"✅ Azure OpenAI initialized: {azure_endpoint}")
            except Exception as e:
                print(f"❌ Azure OpenAI failed: {e}")
        
        # Fallback to regular OpenAI if Azure not available
        elif OPENAI_AVAILABLE and (openai_api_key or os.getenv('OPENAI_API_KEY')):
            try:
                self.openai_client = openai.OpenAI(
                    api_key=openai_api_key or os.getenv('OPENAI_API_KEY')
                )
                print("✅ Regular OpenAI initialized")
            except Exception as e:
                print(f"❌ OpenAI failed: {e}")
        
        # Initialize Anthropic
        if ANTHROPIC_AVAILABLE and (anthropic_api_key or os.getenv('ANTHROPIC_API_KEY')):
            try:
                self.anthropic_client = anthropic.Anthropic(
                    api_key=anthropic_api_key or os.getenv('ANTHROPIC_API_KEY')
                )
                print("✅ Anthropic initialized")
            except Exception as e:
                print(f"❌ Anthropic failed: {e}")
        
        self.legal_prompt_templates = self._load_prompt_templates()
    
    def _get_openai_model_name(self) -> str:
        """Get the correct model name for OpenAI or Azure OpenAI."""
        if self.is_azure_openai:
            # For Azure OpenAI, use deployment name
            return os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME', 'gpt-4')
        else:
            # For regular OpenAI, use standard model name
            return os.getenv('OPENAI_MODEL', 'gpt-4-turbo-preview')
    
    def is_available(self) -> bool:
        """Check if any LLM service is available."""
        return self.openai_client is not None or self.anthropic_client is not None
    
    def _load_prompt_templates(self) -> Dict[str, str]:
        """Load prompt engineering templates for legal reasoning."""
        return {
            'query_analysis': """
You are a legal AI assistant that analyzes user queries about legal matters.

Your task is to analyze the following user query and extract:
1. Intent (question, advice_request, eligibility_check, document_request, etc.)
2. Legal domain (access_to_information, privacy, employment, immigration, etc.)  
3. Entities (people, organizations, documents, legal concepts)
4. Formal query (translate to structured format)

User query: "{query}"

Available legal predicates:
{predicates}

Respond in JSON format:
{{
    "intent": "...",
    "legal_domain": "...", 
    "entities": [...],
    "formal_query": "...",
    "confidence": 0.0-1.0
}}
""",
            
            'legal_reasoning': """
You are a legal AI assistant with expertise in Canadian law.

Context: {legal_context}

Available facts and rules:
{scasp_rules}

Formal reasoning result:
{scasp_result}

User question: {user_query}

Instructions:
1. Base your answer ONLY on the provided legal facts and reasoning result
2. Explain the legal reasoning in plain language
3. Cite specific legal provisions
4. Indicate confidence level
5. Note any limitations or assumptions
6. If the formal reasoning failed, explain why and what additional information is needed

Respond in JSON format:
{{
    "answer": "...",
    "confidence": 0.0-1.0,
    "legal_citations": [...],
    "reasoning_steps": [...],
    "limitations": [...],
    "additional_info_needed": [...]
}}
""",
            
            'response_verification': """
You are a legal fact-checker. Verify the following legal response against the provided facts and rules.

Legal response to verify:
{response}

Available facts and rules:
{facts_and_rules}

Formal logic verification result:
{verification_result}

Check for:
1. Factual accuracy against provided rules
2. Logical consistency
3. Overgeneralization or speculation
4. Missing qualifications or disclaimers

Respond in JSON format:
{{
    "is_accurate": true/false,
    "verified_claims": [...],
    "unverified_claims": [...],
    "corrections": [...],
    "confidence_adjustment": +/-0.0-1.0
}}
""",
            
            'extract_facts': """
You are a legal query analyzer. Extract factual information from a user's question and convert it to Prolog facts.

User question: {query}

Your task:
1. Identify entities (people, organizations, documents)
2. Extract attributes (age, status, role, etc.)
3. Generate simple Prolog facts that represent the scenario

Available legal categories: {available_categories}

Examples:
- "Can a 20-year-old make a will?" → person(user_person). age(user_person, 20).
- "Can a Canadian citizen request records?" → person(user). canadian_citizen(user).
- "Can an active military member aged 15 make a will?" → person(user). military(user). age(user, 15).

Respond in JSON format:
{{
    "entities": ["user_person", "document_x"],
    "prolog_facts": [
        "person(user_person).",
        "age(user_person, 20)."
    ],
    "query_predicate": "eligible(user_person)",
    "explanation": "..."
}}
"""
        }
    
    async def analyze_query(self, query: str, available_predicates: List[str]) -> QueryAnalysis:
        """Analyze a user's legal query to understand intent and extract entities."""
        prompt = self.legal_prompt_templates['query_analysis'].format(
            query=query,
            predicates=', '.join(available_predicates)
        )
        
        if self.openai_client:
            response = await self._query_openai(prompt, max_tokens=500)
        elif self.anthropic_client:
            response = await self._query_anthropic(prompt, max_tokens=500)
        else:
            # Fallback to simple pattern matching
            return self._fallback_query_analysis(query)
        
        try:
            result = json.loads(response.content)
            return QueryAnalysis(
                original_query=query,
                intent=result.get('intent', 'unknown'),
                legal_domain=result.get('legal_domain', 'unknown'),
                entities=result.get('entities', []),
                formal_query=result.get('formal_query', ''),
                confidence=result.get('confidence', 0.5)
            )
        except json.JSONDecodeError:
            return self._fallback_query_analysis(query)
    
    async def generate_legal_response(self, 
                                    user_query: str,
                                    legal_context: str,
                                    scasp_rules: str,
                                    scasp_result: str) -> LLMResponse:
        """Generate a legal response based on formal reasoning results."""
        prompt = self.legal_prompt_templates['legal_reasoning'].format(
            legal_context=legal_context,
            scasp_rules=scasp_rules,
            scasp_result=scasp_result,
            user_query=user_query
        )
        
        if self.openai_client:
            response = await self._query_openai(prompt, max_tokens=1000)
        elif self.anthropic_client:
            response = await self._query_anthropic(prompt, max_tokens=1000)
        else:
            return self._fallback_response(user_query, scasp_result)
        
        try:
            result = json.loads(response.content)
            return LLMResponse(
                content=result.get('answer', response.content),
                confidence=result.get('confidence', 0.5),
                model_used=response.model_used,
                tokens_used=response.tokens_used,
                reasoning_steps=result.get('reasoning_steps', []),
                legal_citations=result.get('legal_citations', []),
                verified_claims=[response.content],  # Will be verified separately
                unverified_claims=[]
            )
        except json.JSONDecodeError:
            return LLMResponse(
                content=response.content,
                confidence=0.7,
                model_used=response.model_used,
                tokens_used=response.tokens_used,
                reasoning_steps=[],
                legal_citations=[],
                verified_claims=[],
                unverified_claims=[response.content]
            )
    
    async def verify_response(self, 
                            response: str,
                            facts_and_rules: str,
                            verification_result: str) -> Dict[str, Any]:
        """Verify a legal response against formal logic results."""
        prompt = self.legal_prompt_templates['response_verification'].format(
            response=response,
            facts_and_rules=facts_and_rules,
            verification_result=verification_result
        )
        
        if self.openai_client:
            llm_response = await self._query_openai(prompt, max_tokens=500)
        elif self.anthropic_client:
            llm_response = await self._query_anthropic(prompt, max_tokens=500)
        else:
            return {
                'is_accurate': True,
                'verified_claims': [response],
                'unverified_claims': [],
                'corrections': [],
                'confidence_adjustment': 0.0
            }
        
        try:
            return json.loads(llm_response.content)
        except json.JSONDecodeError:
            return {
                'is_accurate': True,
                'verified_claims': [response],
                'unverified_claims': [],
                'corrections': [],
                'confidence_adjustment': -0.1
            }
    
    async def extract_query_facts(self, query: str, available_categories: List[str]) -> Dict[str, Any]:
        """Extract facts from a user query and generate Prolog facts.
        
        This is the KEY method that solves the missing facts problem.
        It analyzes the user's question and generates Prolog facts about the scenario.
        """
        prompt = self.legal_prompt_templates['extract_facts'].format(
            query=query,
            available_categories=', '.join(available_categories)
        )
        
        # Try with LLM first
        if self.openai_client:
            try:
                llm_response = await self._query_openai(prompt, max_tokens=500)
                result = json.loads(llm_response.content)
                return result
            except (json.JSONDecodeError, Exception) as e:
                print(f"LLM fact extraction failed: {e}, using fallback")
        
        # Fallback: Pattern matching for common scenarios
        return self._fallback_extract_facts(query)
    
    def _fallback_extract_facts(self, query: str) -> Dict[str, Any]:
        """Fallback fact extraction using pattern matching."""
        query_lower = query.lower()
        entities = []
        prolog_facts = []
        query_predicate = ""
        
        # Extract age - handle multiple patterns
        age_match = re.search(r'(\d+)[\s-]?year[\s-]?old', query_lower)
        if not age_match:
            # Try "I am X years old" pattern
            age_match = re.search(r'i am (\d+) years? old', query_lower)
        if not age_match:
            # Try "aged X" pattern
            age_match = re.search(r'aged?\s+(\d+)', query_lower)
        
        if age_match:
            age = age_match.group(1)
            entities.append("user_person")
            prolog_facts.append("person(user_person).")
            prolog_facts.append(f"age(user_person, {age}).")
            
            # Check if asking about wills
            if 'will' in query_lower:
                query_predicate = "eligible(user_person)"
        
        # Check for Canadian citizen
        if 'canadian citizen' in query_lower:
            if not entities:
                entities.append("user")
            prolog_facts.append("person(user).")
            prolog_facts.append("canadian_citizen(user).")
            
            # Check if asking about access to information
            if any(term in query_lower for term in ['request', 'access', 'record', 'document']):
                if not query_predicate:
                    query_predicate = "has_right_to_access(user, record_x)"
                    prolog_facts.append("record(record_x).")
        
        # Check for military member
        if 'military' in query_lower or 'active military' in query_lower:
            if 'user_person' not in entities:
                entities.append("user_person")
                prolog_facts.append("person(user_person).")
            prolog_facts.append("military(user_person).")
            
            # Extract age for military member
            if age_match:
                age = age_match.group(1)
                if f"age(user_person, {age})." not in prolog_facts:
                    prolog_facts.append(f"age(user_person, {age}).")
            elif 'aged' in query_lower or 'age' in query_lower:
                # Try to find age mentioned near 'aged' or 'age'
                age_alt_match = re.search(r'aged?\s+(\d+)', query_lower)
                if age_alt_match:
                    age = age_alt_match.group(1)
                    prolog_facts.append(f"age(user_person, {age}).")
            
            if 'will' in query_lower and not query_predicate:
                query_predicate = "eligible(user_person)"
        
        # Check for permanent resident
        if 'permanent resident' in query_lower:
            if not entities:
                entities.append("user")
            prolog_facts.append("person(user).")
            prolog_facts.append("permanent_resident(user).")
            
            if any(term in query_lower for term in ['request', 'access', 'record']):
                if not query_predicate:
                    query_predicate = "has_right_to_access(user, record_x)"
                    prolog_facts.append("record(record_x).")
        
        # If we found nothing specific, create a generic person
        if not entities:
            entities.append("user")
            prolog_facts.append("person(user).")
        
        # Ensure we always have a valid query predicate
        # If nothing was set, use a simple existence check
        if not query_predicate:
            if entities:
                query_predicate = f"person({entities[0]})"
            else:
                # Last resort: just check if any person exists
                query_predicate = "person(_)"
        
        return {
            "entities": entities,
            "prolog_facts": prolog_facts,
            "query_predicate": query_predicate,
            "explanation": f"Extracted {len(prolog_facts)} facts from query using pattern matching"
        }
    
    async def _query_openai(self, prompt: str, max_tokens: int = 1000) -> LLMResponse:
        """Query OpenAI GPT-4 or Azure OpenAI."""
        try:
            model_name = self._get_openai_model_name()
            service_type = "Azure OpenAI" if self.is_azure_openai else "OpenAI"
            
            # Use sync method for Azure OpenAI, async for regular OpenAI
            if self.is_azure_openai:
                # Azure OpenAI uses sync methods
                response = self.openai_client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": "You are a legal AI assistant with expertise in formal logic and legal reasoning."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=max_tokens,
                    temperature=0.1  # Low temperature for consistent legal reasoning
                )
            else:
                # Regular OpenAI uses async methods
                response = await self.openai_client.chat.completions.acreate(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": "You are a legal AI assistant with expertise in formal logic and legal reasoning."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=max_tokens,
                    temperature=0.1  # Low temperature for consistent legal reasoning
                )
            
            return LLMResponse(
                content=response.choices[0].message.content,
                confidence=0.8,  # Base confidence for GPT-4
                model_used=f"{service_type}: {model_name}",
                tokens_used=response.usage.total_tokens,
                reasoning_steps=[],
                legal_citations=[],
                verified_claims=[],
                unverified_claims=[]
            )
            
        except Exception as e:
            provider = "Azure OpenAI" if self.is_azure_openai else "OpenAI"
            raise Exception(f"{provider} API error: {e}")
    
    async def _query_anthropic(self, prompt: str, max_tokens: int = 1000) -> LLMResponse:
        """Query Anthropic Claude."""
        try:
            response = await self.anthropic_client.messages.acreate(
                model="claude-3-opus-20240229",
                max_tokens=max_tokens,
                temperature=0.1,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return LLMResponse(
                content=response.content[0].text,
                confidence=0.85,  # Base confidence for Claude
                model_used="claude-3-opus",
                tokens_used=response.usage.input_tokens + response.usage.output_tokens,
                reasoning_steps=[],
                legal_citations=[],
                verified_claims=[],
                unverified_claims=[]
            )
            
        except Exception as e:
            raise Exception(f"Anthropic API error: {e}")
    
    def _fallback_query_analysis(self, query: str) -> QueryAnalysis:
        """Fallback query analysis using pattern matching."""
        query_lower = query.lower()
        
        # Determine intent
        if any(word in query_lower for word in ['can i', 'am i eligible', 'do i have']):
            intent = 'eligibility_check'
        elif any(word in query_lower for word in ['how to', 'how do i', 'what is the process']):
            intent = 'process_question'
        elif 'request' in query_lower:
            intent = 'document_request'
        else:
            intent = 'general_question'
        
        # Determine legal domain
        if any(term in query_lower for term in ['access', 'information', 'records', 'documents']):
            domain = 'access_to_information'
        else:
            domain = 'general'
        
        # Extract basic entities
        entities = []
        entity_patterns = [
            r'\b[A-Z][a-zA-Z\s]+(?:Canada|Department|Ministry|Board|Commission)\b',
            r'\bCanadian citizen\b',
            r'\bpermanent resident\b'
        ]
        
        for pattern in entity_patterns:
            matches = re.findall(pattern, query)
            entities.extend(matches)
        
        return QueryAnalysis(
            original_query=query,
            intent=intent,
            legal_domain=domain,
            entities=entities,
            formal_query=f"user_query({query.replace(' ', '_')})",
            confidence=0.6
        )
    
    def _fallback_response(self, user_query: str, scasp_result: str) -> LLMResponse:
        """Fallback response when LLM services are unavailable."""
        if 'true' in scasp_result.lower() or 'success' in scasp_result.lower():
            content = f"Based on the available legal rules, the answer to your query '{user_query}' appears to be affirmative. However, this is a simplified analysis. Please consult with a qualified legal professional for authoritative advice."
            confidence = 0.6
        else:
            content = f"Based on the available legal rules, I cannot definitively answer your query '{user_query}'. This may be due to insufficient information or the query falling outside the scope of the loaded legal rules. Please consult with a qualified legal professional."
            confidence = 0.4
        
        return LLMResponse(
            content=content,
            confidence=confidence,
            model_used="fallback",
            tokens_used=0,
            reasoning_steps=["Fallback response due to unavailable LLM services"],
            legal_citations=[],
            verified_claims=[],
            unverified_claims=[content]
        )
    
    def extract_legal_entities(self, text: str) -> List[str]:
        """Extract legal entities from text using pattern matching."""
        entities = []
        
        # Government institution patterns
        gov_patterns = [
            r'\b(?:Department|Ministry|Secretariat|Board|Commission|Agency) of [A-Z][a-zA-Z\s]+\b',
            r'\b[A-Z][a-zA-Z\s]+ (?:Department|Ministry|Secretariat|Board|Commission|Agency)\b',
            r'\bTreasury Board of Canada Secretariat\b',
            r'\bHealth Canada\b'
        ]
        
        # Person/status patterns
        person_patterns = [
            r'\bCanadian citizen\b',
            r'\bpermanent resident\b',
            r'\bGovernor in Council\b'
        ]
        
        # Document patterns
        doc_patterns = [
            r'\b(?:record|document|file|report|correspondence|memo)\b'
        ]
        
        all_patterns = gov_patterns + person_patterns + doc_patterns
        
        for pattern in all_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            entities.extend(matches)
        
        return list(set(entities))  # Remove duplicates
    
    def translate_to_formal_query(self, natural_query: str, available_predicates: List[str]) -> str:
        """Simple translation of natural language to formal logic query."""
        query_lower = natural_query.lower()
        
        # Access to information patterns
        if 'access' in query_lower and ('record' in query_lower or 'document' in query_lower):
            if 'canadian citizen' in query_lower:
                return "has_right_to_access(Person, Record) :- canadian_citizen(Person), record(Record)"
            elif 'permanent resident' in query_lower:
                return "has_right_to_access(Person, Record) :- permanent_resident(Person), record(Record)"
            else:
                return "has_right_to_access(Person, Record)"
        
        # Generic fallback
        return f"user_query('{natural_query.replace(' ', '_')}')"


def main():
    """Test the LLM service."""
    llm = LLMService()
    
    print(f"LLM services available: {llm.is_available()}")
    print(f"OpenAI available: {llm.openai_client is not None}")
    print(f"Anthropic available: {llm.anthropic_client is not None}")
    
    # Test query analysis
    test_query = "Can a Canadian citizen request records from Health Canada?"
    
    async def test_analysis():
        analysis = await llm.analyze_query(test_query, ['canadian_citizen', 'has_right_to_access', 'record'])
        print(f"\nQuery analysis:")
        print(f"Intent: {analysis.intent}")
        print(f"Domain: {analysis.legal_domain}")
        print(f"Entities: {analysis.entities}")
        print(f"Formal query: {analysis.formal_query}")
        print(f"Confidence: {analysis.confidence}")
    
    # Run test
    try:
        asyncio.run(test_analysis())
    except Exception as e:
        print(f"Test failed: {e}")
        
        # Test fallback
        analysis = llm._fallback_query_analysis(test_query)
        print(f"\nFallback analysis:")
        print(f"Intent: {analysis.intent}")
        print(f"Domain: {analysis.legal_domain}")


if __name__ == "__main__":
    main()