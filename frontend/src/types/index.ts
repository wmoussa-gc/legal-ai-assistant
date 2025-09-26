// TypeScript interfaces matching the backend models

export interface LegalQuery {
  query: string;
  context?: string;
  user_location?: string;
}

export interface LegalCitation {
  provision_id: string;
  title: string;
  text: string;
  source_document: string;
  section?: string;
}

export interface ReasoningStep {
  step_number: number;
  description: string;
  rule_applied?: string;
  conclusion: string;
}

export interface FormalVerification {
  query_executed: string;
  success: boolean;
  solutions: Record<string, string>[];
  execution_time: number;
  error_message?: string;
}

export type QueryIntent = 'eligibility_check' | 'process_question' | 'document_request' | 'general_question' | 'legal_advice';
export type LegalDomain = 'access_to_information' | 'privacy' | 'employment' | 'immigration' | 'general';
export type ConfidenceLevel = 'high' | 'medium' | 'low';

export interface LegalResponse {
  query_id: string;
  original_query: string;
  answer: string;
  confidence: number;
  confidence_level: ConfidenceLevel;
  intent: QueryIntent;
  legal_domain: LegalDomain;
  entities_found: string[];
  reasoning_steps: ReasoningStep[];
  legal_citations: LegalCitation[];
  formal_verification?: FormalVerification;
  timestamp: string;
  model_used: string;
  processing_time: number;
  limitations: string[];
  follow_up_questions: string[];
  human_lawyer_recommended: boolean;
}

export interface SystemStatus {
  status: string;
  services: Record<string, boolean>;
  loaded_documents: string[];
  total_rules: number;
  uptime: number;
}

export interface DocumentInfo {
  name: string;
  slug: string;
  provisions_count: number;
  rules_count: number;
  categories: string[];
  last_updated: string;
}

export interface ChatMessage {
  id: string;
  type: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  response?: LegalResponse;
  isLoading?: boolean;
}

// UI State interfaces
export interface ChatState {
  messages: ChatMessage[];
  isLoading: boolean;
  systemStatus: SystemStatus | null;
  availableDocuments: DocumentInfo[];
}

export interface VisualizationNode {
  id: string;
  label: string;
  type: 'fact' | 'rule' | 'query' | 'conclusion';
  x?: number;
  y?: number;
  children?: string[];
}

export interface VisualizationLink {
  source: string;
  target: string;
  type: 'derives' | 'uses' | 'proves';
}