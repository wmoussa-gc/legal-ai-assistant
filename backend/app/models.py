"""
Data models for the Legal AI Assistant API.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class QueryIntent(str, Enum):
    """Possible intents for legal queries."""
    ELIGIBILITY_CHECK = "eligibility_check"
    PROCESS_QUESTION = "process_question"
    DOCUMENT_REQUEST = "document_request"
    GENERAL_QUESTION = "general_question"
    LEGAL_ADVICE = "legal_advice"


class LegalDomain(str, Enum):
    """Legal domains supported by the system."""
    ACCESS_TO_INFORMATION = "access_to_information"
    PRIVACY = "privacy"
    EMPLOYMENT = "employment"
    IMMIGRATION = "immigration"
    GENERAL = "general"


class ConfidenceLevel(str, Enum):
    """Confidence levels for responses."""
    HIGH = "high"  # 0.8-1.0
    MEDIUM = "medium"  # 0.5-0.79
    LOW = "low"  # 0.0-0.49


# Request Models
class LegalQuery(BaseModel):
    """User's legal query request."""
    query: str = Field(..., description="The user's legal question", min_length=1)
    context: Optional[str] = Field(None, description="Additional context for the query")
    user_location: Optional[str] = Field(None, description="User's jurisdiction (e.g., 'Canada', 'Ontario')")
    
    class Config:
        schema_extra = {
            "example": {
                "query": "Can a Canadian citizen request records from Health Canada?",
                "context": "I am researching vaccine safety data",
                "user_location": "Canada"
            }
        }


class DocumentUpload(BaseModel):
    """Request to upload and parse a legal document."""
    filename: str = Field(..., description="Name of the document file")
    content_type: str = Field(..., description="MIME type of the document")
    
    class Config:
        schema_extra = {
            "example": {
                "filename": "privacy-act-section-3.blawx",
                "content_type": "application/octet-stream"
            }
        }


# Response Models
class LegalCitation(BaseModel):
    """A citation to a legal provision."""
    provision_id: str = Field(..., description="Unique identifier for the legal provision")
    title: str = Field(..., description="Title of the provision")
    text: str = Field(..., description="Text of the provision")
    source_document: str = Field(..., description="Source legal document")
    section: Optional[str] = Field(None, description="Section number")
    
    class Config:
        schema_extra = {
            "example": {
                "provision_id": "sec_4__subsec_1",
                "title": "Section 4(1) - Right of Access",
                "text": "Subject to this Part, but notwithstanding any other Act of Parliament, every person who is...",
                "source_document": "Access to Information Act",
                "section": "4(1)"
            }
        }


class ReasoningStep(BaseModel):
    """A step in the legal reasoning process."""
    step_number: int = Field(..., description="Order of this reasoning step")
    description: str = Field(..., description="Description of this reasoning step")
    rule_applied: Optional[str] = Field(None, description="Legal rule applied in this step")
    conclusion: str = Field(..., description="Conclusion reached in this step")
    
    class Config:
        schema_extra = {
            "example": {
                "step_number": 1,
                "description": "Determine if person is eligible",
                "rule_applied": "canadian_citizen(Person) :- ...",
                "conclusion": "Person qualifies as Canadian citizen"
            }
        }


class FormalVerification(BaseModel):
    """Results of formal logic verification."""
    query_executed: str = Field(..., description="The formal logic query that was executed")
    success: bool = Field(..., description="Whether the formal verification succeeded")
    solutions: List[Dict[str, str]] = Field(default_factory=list, description="Variable bindings for successful queries")
    execution_time: float = Field(..., description="Time taken for verification in seconds")
    error_message: Optional[str] = Field(None, description="Error message if verification failed")
    
    class Config:
        schema_extra = {
            "example": {
                "query_executed": "has_right_to_access(bob, record_X)",
                "success": True,
                "solutions": [{"Person": "bob", "Record": "record_X"}],
                "execution_time": 0.123,
                "error_message": None
            }
        }


class LegalResponse(BaseModel):
    """Complete response to a legal query."""
    query_id: str = Field(..., description="Unique identifier for this query")
    original_query: str = Field(..., description="The user's original query")
    answer: str = Field(..., description="The main answer to the query")
    confidence: float = Field(..., description="Confidence score (0.0-1.0)")
    confidence_level: ConfidenceLevel = Field(..., description="Human-readable confidence level")
    
    # Analysis
    intent: QueryIntent = Field(..., description="Detected intent of the query")
    legal_domain: LegalDomain = Field(..., description="Legal domain of the query")
    entities_found: List[str] = Field(default_factory=list, description="Legal entities extracted from query")
    
    # Reasoning
    reasoning_steps: List[ReasoningStep] = Field(default_factory=list, description="Steps in the legal reasoning")
    legal_citations: List[LegalCitation] = Field(default_factory=list, description="Relevant legal citations")
    formal_verification: Optional[FormalVerification] = Field(None, description="Formal logic verification results")
    
    # Metadata
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When this response was generated")
    model_used: str = Field(..., description="AI model used for generation")
    processing_time: float = Field(..., description="Total processing time in seconds")
    
    # Additional information
    limitations: List[str] = Field(default_factory=list, description="Limitations or caveats for this response")
    follow_up_questions: List[str] = Field(default_factory=list, description="Suggested follow-up questions")
    human_lawyer_recommended: bool = Field(default=False, description="Whether consultation with human lawyer is recommended")
    
    class Config:
        schema_extra = {
            "example": {
                "query_id": "query_123456",
                "original_query": "Can a Canadian citizen request records from Health Canada?",
                "answer": "Yes, under the Access to Information Act, Section 4(1)(a), Canadian citizens have the right to request access to records under the control of government institutions, including Health Canada.",
                "confidence": 0.92,
                "confidence_level": "high",
                "intent": "eligibility_check",
                "legal_domain": "access_to_information",
                "entities_found": ["Canadian citizen", "Health Canada", "records"],
                "reasoning_steps": [],
                "legal_citations": [],
                "formal_verification": None,
                "timestamp": "2024-01-15T10:30:00Z",
                "model_used": "gpt-4-turbo",
                "processing_time": 2.5,
                "limitations": ["This advice is based on federal law and may not account for all provincial variations"],
                "follow_up_questions": ["What specific types of records are you looking for?"],
                "human_lawyer_recommended": False
            }
        }


class SystemStatus(BaseModel):
    """System status information."""
    status: str = Field(..., description="Overall system status")
    services: Dict[str, bool] = Field(..., description="Status of individual services")
    loaded_documents: List[str] = Field(default_factory=list, description="Currently loaded legal documents")
    total_rules: int = Field(default=0, description="Total number of legal rules loaded")
    uptime: float = Field(..., description="System uptime in seconds")
    
    class Config:
        schema_extra = {
            "example": {
                "status": "healthy",
                "services": {
                    "scasp_engine": True,
                    "llm_service": True,
                    "blawx_parser": True
                },
                "loaded_documents": ["Access to Information Act s.4"],
                "total_rules": 25,
                "uptime": 3600.0
            }
        }


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When the error occurred")
    
    class Config:
        schema_extra = {
            "example": {
                "error": "QUERY_PROCESSING_ERROR",
                "message": "Unable to process the legal query",
                "details": {"reason": "No matching legal rules found"},
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }


class DocumentInfo(BaseModel):
    """Information about a loaded legal document."""
    name: str = Field(..., description="Document name")
    slug: str = Field(..., description="Document slug identifier")
    provisions_count: int = Field(..., description="Number of legal provisions")
    rules_count: int = Field(..., description="Number of formal logic rules")
    categories: List[str] = Field(default_factory=list, description="Legal categories defined")
    last_updated: datetime = Field(default_factory=datetime.utcnow, description="Last update time")
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Access to Information Act (s.4)",
                "slug": "access-to-information-act-s4",
                "provisions_count": 3,
                "rules_count": 15,
                "categories": ["person", "record", "government_institution"],
                "last_updated": "2024-01-15T10:30:00Z"
            }
        }


# Utility functions for confidence levels
def confidence_to_level(confidence: float) -> ConfidenceLevel:
    """Convert numeric confidence to confidence level enum."""
    if confidence >= 0.8:
        return ConfidenceLevel.HIGH
    elif confidence >= 0.5:
        return ConfidenceLevel.MEDIUM
    else:
        return ConfidenceLevel.LOW


def should_recommend_lawyer(confidence: float, query_intent: QueryIntent, has_verification: bool) -> bool:
    """Determine if human lawyer consultation should be recommended."""
    if confidence < 0.6:
        return True
    
    if query_intent == QueryIntent.LEGAL_ADVICE and not has_verification:
        return True
    
    return False