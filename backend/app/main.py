"""
Main FastAPI application for Legal AI Assistant.
"""

import os
import uuid
import time
import asyncio
from typing import List, Optional
from datetime import datetime
from pathlib import Path

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# FastAPI imports (will be gracefully handled if not available)
try:
    from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import StreamingResponse
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    # Create mock classes for when FastAPI is not available
    class MockFile:
        def __call__(self, *args, **kwargs):
            return None
    File = MockFile()

# Import our services and models
from .services.blawx_parser import BlawxParser, LegalRuleDoc
from .services.scasp_engine import ScaspEngine, MockScaspEngine
from .services.llm_service import LLMService

# Import models (will create mock versions if pydantic not available)
try:
    from .models import (
        LegalQuery, LegalResponse, SystemStatus, ErrorResponse, DocumentInfo,
        QueryIntent, LegalDomain, ConfidenceLevel, LegalCitation, ReasoningStep,
        FormalVerification, confidence_to_level, should_recommend_lawyer
    )
    MODELS_AVAILABLE = True
except ImportError:
    MODELS_AVAILABLE = False
    # Create basic mock classes
    class LegalQuery:
        def __init__(self, query: str, context: str = None, user_location: str = None):
            self.query = query
            self.context = context
            self.user_location = user_location


# Application state
class AppState:
    """Application state management."""
    def __init__(self):
        self.start_time = time.time()
        self.loaded_documents: List[LegalRuleDoc] = []
        self.blawx_parser = BlawxParser()
        
        # Initialize s(CASP) engine
        try:
            self.scasp_engine = ScaspEngine()
            if not self.scasp_engine.is_available():
                print("Warning: s(CASP) not available, using mock engine")
                self.scasp_engine = MockScaspEngine()
        except Exception as e:
            print(f"Warning: Could not initialize s(CASP) engine: {e}")
            self.scasp_engine = MockScaspEngine()
        
        # Initialize LLM service
        try:
            self.llm_service = LLMService()
        except Exception as e:
            print(f"Warning: Could not initialize LLM service: {e}")
            self.llm_service = None
        
        # Load initial documents
        self._load_initial_documents()
    
    def _load_initial_documents(self):
        """Load initial legal documents from data directory."""
        data_dir = Path(__file__).parent.parent.parent / "data"
        
        if not data_dir.exists():
            print("Warning: Data directory not found")
            return
        
        for blawx_file in data_dir.glob("*.blawx"):
            try:
                doc = self.blawx_parser.parse_file(str(blawx_file))
                self.loaded_documents.append(doc)
                print(f"Loaded legal document: {doc.name}")
            except Exception as e:
                print(f"Warning: Could not load {blawx_file}: {e}")
    
    def get_all_predicates(self) -> List[str]:
        """Get all available predicates from loaded documents."""
        predicates = set()
        for doc in self.loaded_documents:
            for rule in doc.scasp_rules:
                predicates.update(rule.predicates)
        return sorted(list(predicates))
    
    def find_relevant_rules(self, query_terms: List[str]) -> str:
        """Find rules relevant to query terms."""
        all_rules = []
        for doc in self.loaded_documents:
            relevant_rules = self.blawx_parser.extract_facts_for_query(doc, query_terms)
            all_rules.extend(relevant_rules)
        
        if all_rules:
            return self.blawx_parser.format_scasp_program(all_rules)
        return ""


# Initialize application state
app_state = AppState()

# Create FastAPI app if available
if FASTAPI_AVAILABLE:
    app = FastAPI(
        title="Legal AI Assistant",
        description="A ChatGPT-like interface for legal queries with formal verification using s(CASP)",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000", 
            "http://127.0.0.1:3000",
            "http://localhost:3001",
            "http://127.0.0.1:3001"
        ],  # React dev server
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    # Mock app for development without FastAPI
    class MockApp:
        def get(self, path): return lambda f: f
        def post(self, path): return lambda f: f
        def put(self, path): return lambda f: f
        def delete(self, path): return lambda f: f
    
    app = MockApp()


@app.get("/")
async def root():
    """Root endpoint with basic information."""
    return {
        "message": "Legal AI Assistant API",
        "version": "1.0.0",
        "status": "running",
        "documentation": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    if MODELS_AVAILABLE:
        return SystemStatus(
            status="healthy",
            services={
                "scasp_engine": app_state.scasp_engine.is_available(),
                "llm_service": app_state.llm_service.is_available() if app_state.llm_service else False,
                "blawx_parser": True
            },
            loaded_documents=[doc.name for doc in app_state.loaded_documents],
            total_rules=sum(len(doc.scasp_rules) for doc in app_state.loaded_documents),
            uptime=time.time() - app_state.start_time
        )
    else:
        return {
            "status": "healthy",
            "services": {
                "scasp_engine": app_state.scasp_engine.is_available(),
                "llm_service": app_state.llm_service.is_available() if app_state.llm_service else False,
                "blawx_parser": True
            },
            "loaded_documents": [doc.name for doc in app_state.loaded_documents],
            "total_rules": sum(len(doc.scasp_rules) for doc in app_state.loaded_documents),
            "uptime": time.time() - app_state.start_time
        }


@app.get("/documents")
async def list_documents():
    """List all loaded legal documents."""
    if MODELS_AVAILABLE:
        return [
            DocumentInfo(
                name=doc.name,
                slug=doc.slug,
                provisions_count=len(doc.provisions),
                rules_count=len(doc.scasp_rules),
                categories=doc.categories,
                last_updated=datetime.utcnow()
            )
            for doc in app_state.loaded_documents
        ]
    else:
        return [
            {
                "name": doc.name,
                "slug": doc.slug,
                "provisions_count": len(doc.provisions),
                "rules_count": len(doc.scasp_rules),
                "categories": doc.categories
            }
            for doc in app_state.loaded_documents
        ]


@app.get("/documents/{slug}/details")
async def get_document_details(slug: str):
    """Get detailed analysis of a specific legal document."""
    # Find document by slug
    document = None
    for doc in app_state.loaded_documents:
        if doc.slug == slug:
            document = doc
            break
    
    if not document:
        if FASTAPI_AVAILABLE:
            raise HTTPException(status_code=404, detail=f"Document with slug '{slug}' not found")
        else:
            return {"error": f"Document with slug '{slug}' not found"}
    
    # Analyze provisions
    provisions_analysis = []
    for i, provision in enumerate(document.provisions):
        provisions_analysis.append({
            "id": provision.id,
            "title": provision.title,
            "text": provision.text[:200] + "..." if len(provision.text) > 200 else provision.text,
            "full_text": provision.text,
            "section_number": provision.section_number,
            "subsection_number": provision.subsection_number,
            "parent_id": provision.parent_id,
            "word_count": len(provision.text.split()),
            "index": i
        })
    
    # Analyze s(CASP) rules
    rule_type_counts = {}
    predicate_counts = {}
    variable_counts = {}
    sample_rules = {"fact": [], "rule": [], "query": [], "abducible": [], "other": []}
    
    for rule in document.scasp_rules:
        # Count rule types
        rule_type_counts[rule.rule_type] = rule_type_counts.get(rule.rule_type, 0) + 1
        
        # Count predicates
        for pred in rule.predicates:
            predicate_counts[pred] = predicate_counts.get(pred, 0) + 1
        
        # Count variables  
        for var in rule.variables:
            variable_counts[var] = variable_counts.get(var, 0) + 1
        
        # Collect sample rules (first 3 of each type)
        rule_type_key = rule.rule_type if rule.rule_type in sample_rules else "other"
        if len(sample_rules[rule_type_key]) < 3:
            sample_rules[rule_type_key].append({
                "rule_text": rule.rule_text,
                "variables": rule.variables,
                "predicates": rule.predicates
            })
    
    # Get top predicates and variables
    top_predicates = sorted(predicate_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    top_variables = sorted(variable_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    
    return {
        "name": document.name,
        "slug": document.slug,
        "categories": document.categories,
        "summary": {
            "total_provisions": len(document.provisions),
            "total_rules": len(document.scasp_rules),
            "rule_type_distribution": rule_type_counts,
            "unique_predicates": len(predicate_counts),
            "unique_variables": len(variable_counts)
        },
        "provisions": provisions_analysis,
        "rules_analysis": {
            "type_counts": rule_type_counts,
            "top_predicates": top_predicates,
            "top_variables": top_variables,
            "sample_rules": sample_rules
        }
    }


@app.post("/query")
async def process_legal_query(query: LegalQuery if MODELS_AVAILABLE else dict):
    """Process a legal query and return a comprehensive response."""
    start_time = time.time()
    query_id = str(uuid.uuid4())
    
    try:
        # Extract query text
        if MODELS_AVAILABLE:
            query_text = query.query
            context = query.context
        else:
            query_text = query.get("query", "")
            context = query.get("context")
        
        if not query_text:
            if FASTAPI_AVAILABLE:
                raise HTTPException(status_code=400, detail="Query text is required")
            else:
                return {"error": "Query text is required"}
        
        # Step 1: Analyze the query
        if app_state.llm_service and app_state.llm_service.is_available():
            analysis = await app_state.llm_service.analyze_query(
                query_text, 
                app_state.get_all_predicates()
            )
            intent = analysis.intent
            domain = analysis.legal_domain
            entities = analysis.entities
            formal_query = analysis.formal_query
        else:
            # Fallback analysis
            intent = "general_question"
            domain = "access_to_information"
            entities = app_state.llm_service.extract_legal_entities(query_text) if app_state.llm_service else []
            formal_query = f"user_query('{query_text.replace(' ', '_')}')"
        
        # Step 2: Find relevant rules
        relevant_program = app_state.find_relevant_rules(entities + [query_text])
        
        # Step 3: Execute formal verification
        verification_result = None
        if relevant_program and formal_query:
            scasp_result = app_state.scasp_engine.query(relevant_program, formal_query.split(":-")[0])
            
            if MODELS_AVAILABLE:
                verification_result = FormalVerification(
                    query_executed=formal_query,
                    success=scasp_result.success,
                    solutions=[answer.solution for answer in scasp_result.answers],
                    execution_time=scasp_result.execution_time,
                    error_message=scasp_result.error_message
                )
        
        # Step 4: Generate natural language response
        if app_state.llm_service and app_state.llm_service.is_available():
            llm_response = await app_state.llm_service.generate_legal_response(
                query_text,
                f"Legal documents: {', '.join(doc.name for doc in app_state.loaded_documents)}",
                relevant_program,
                str(verification_result) if verification_result else "No formal verification available"
            )
            answer = llm_response.content
            confidence = llm_response.confidence
            reasoning_steps = [
                {"step_number": i+1, "description": step, "conclusion": step}
                for i, step in enumerate(llm_response.reasoning_steps)
            ] if MODELS_AVAILABLE else llm_response.reasoning_steps
        else:
            # Fallback response
            if verification_result and verification_result.success:
                answer = f"Based on the available legal rules, the answer to your query appears to be affirmative. The formal logic verification succeeded with solutions: {verification_result.solutions}"
                confidence = 0.7
            else:
                answer = f"I cannot provide a definitive answer to your query based on the available legal rules. This may require consultation with a legal professional."
                confidence = 0.4
            reasoning_steps = []
        
        # Step 5: Extract citations
        legal_citations = []
        for doc in app_state.loaded_documents:
            for provision in doc.provisions:
                if any(entity.lower() in provision.text.lower() for entity in entities):
                    if MODELS_AVAILABLE:
                        citation = LegalCitation(
                            provision_id=provision.id,
                            title=provision.title,
                            text=provision.text[:200] + "..." if len(provision.text) > 200 else provision.text,
                            source_document=doc.name,
                            section=provision.section_number
                        )
                        legal_citations.append(citation)
                    else:
                        legal_citations.append({
                            "provision_id": provision.id,
                            "title": provision.title,
                            "text": provision.text[:200] + "..." if len(provision.text) > 200 else provision.text,
                            "source_document": doc.name,
                            "section": provision.section_number
                        })
        
        processing_time = time.time() - start_time
        
        # Build response
        if MODELS_AVAILABLE:
            confidence_level = confidence_to_level(confidence)
            recommend_lawyer = should_recommend_lawyer(
                confidence, 
                QueryIntent(intent) if intent in [e.value for e in QueryIntent] else QueryIntent.GENERAL_QUESTION,
                verification_result is not None and verification_result.success
            )
            
            return LegalResponse(
                query_id=query_id,
                original_query=query_text,
                answer=answer,
                confidence=confidence,
                confidence_level=confidence_level,
                intent=QueryIntent(intent) if intent in [e.value for e in QueryIntent] else QueryIntent.GENERAL_QUESTION,
                legal_domain=LegalDomain(domain) if domain in [e.value for e in LegalDomain] else LegalDomain.GENERAL,
                entities_found=entities,
                reasoning_steps=reasoning_steps,
                legal_citations=legal_citations,
                formal_verification=verification_result,
                model_used=llm_response.model_used if 'llm_response' in locals() else "fallback",
                processing_time=processing_time,
                limitations=["This is AI-generated legal information and should not replace professional legal advice"],
                follow_up_questions=["Would you like more specific information about any particular aspect?"],
                human_lawyer_recommended=recommend_lawyer
            )
        else:
            return {
                "query_id": query_id,
                "original_query": query_text,
                "answer": answer,
                "confidence": confidence,
                "confidence_level": "high" if confidence >= 0.8 else "medium" if confidence >= 0.5 else "low",
                "intent": intent,
                "legal_domain": domain,
                "entities_found": entities,
                "reasoning_steps": reasoning_steps,
                "legal_citations": legal_citations,
                "formal_verification": verification_result.__dict__ if verification_result else None,
                "processing_time": processing_time,
                "limitations": ["This is AI-generated legal information and should not replace professional legal advice"],
                "human_lawyer_recommended": confidence < 0.6
            }
    
    except Exception as e:
        if FASTAPI_AVAILABLE:
            raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
        else:
            return {"error": f"Internal server error: {str(e)}"}


@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload and parse a new legal document."""
    if not file.filename.endswith('.blawx'):
        if FASTAPI_AVAILABLE:
            raise HTTPException(status_code=400, detail="Only .blawx files are supported")
        else:
            return {"error": "Only .blawx files are supported"}
    
    try:
        # Save uploaded file temporarily
        temp_path = Path(f"/tmp/{file.filename}")
        content = await file.read()
        
        with open(temp_path, 'wb') as f:
            f.write(content)
        
        # Parse the document
        doc = app_state.blawx_parser.parse_file(str(temp_path))
        app_state.loaded_documents.append(doc)
        
        # Clean up
        temp_path.unlink()
        
        return {
            "message": f"Successfully uploaded and parsed {file.filename}",
            "document_name": doc.name,
            "provisions_count": len(doc.provisions),
            "rules_count": len(doc.scasp_rules)
        }
    
    except Exception as e:
        if FASTAPI_AVAILABLE:
            raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")
        else:
            return {"error": f"Failed to process document: {str(e)}"}


# Development server
if __name__ == "__main__":
    if FASTAPI_AVAILABLE:
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8000)
    else:
        print("FastAPI not available. Install with: pip install fastapi uvicorn")
        print("Running in mock mode for development...")
        
        # Simple test of core functionality
        async def test_query():
            query = {"query": "Can a Canadian citizen request records from Health Canada?"}
            result = await process_legal_query(query)
            print("Test query result:")
            print(f"Answer: {result.get('answer', 'No answer')}")
            print(f"Confidence: {result.get('confidence', 0)}")
        
        # Run test
        import asyncio
        asyncio.run(test_query())