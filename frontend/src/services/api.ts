// API service for communicating with the backend

import axios, { AxiosResponse } from 'axios';
import { LegalQuery, LegalResponse, SystemStatus, DocumentInfo } from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API Response Error:', error.response?.data || error.message);
    
    // Handle common error cases
    if (error.response?.status === 500) {
      throw new Error('Server error. Please try again later.');
    } else if (error.response?.status === 400) {
      throw new Error(error.response.data?.detail || 'Invalid request');
    } else if (!error.response) {
      throw new Error('Network error. Please check your connection.');
    }
    
    throw error;
  }
);

export class ApiService {
  
  // Health and status endpoints
  static async getHealth(): Promise<SystemStatus> {
    const response: AxiosResponse<SystemStatus> = await api.get('/health');
    return response.data;
  }

  static async getDocuments(): Promise<DocumentInfo[]> {
    const response: AxiosResponse<DocumentInfo[]> = await api.get('/documents');
    return response.data;
  }

  // Main query endpoint
  static async submitQuery(query: LegalQuery): Promise<LegalResponse> {
    const response: AxiosResponse<LegalResponse> = await api.post('/query', query);
    return response.data;
  }

  // Streaming query (for real-time responses)
  static async submitQueryStream(
    query: LegalQuery, 
    onChunk: (chunk: string) => void,
    onComplete: (response: LegalResponse) => void,
    onError: (error: Error) => void
  ): Promise<void> {
    try {
      // For now, simulate streaming by breaking up the regular response
      const response = await this.submitQuery(query);
      
      // Simulate streaming the response
      const chunks = this.chunkResponse(response.answer);
      let currentChunk = '';
      
      for (const chunk of chunks) {
        currentChunk += chunk;
        onChunk(currentChunk);
        await this.delay(50); // Small delay to simulate streaming
      }
      
      onComplete(response);
    } catch (error) {
      onError(error as Error);
    }
  }

  // Upload document endpoint
  static async uploadDocument(file: File): Promise<{ message: string; document_name: string }> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  }

  // Utility methods
  private static chunkResponse(text: string): string[] {
    // Split response into chunks for streaming effect
    const words = text.split(' ');
    const chunks: string[] = [];
    const wordsPerChunk = 3;
    
    for (let i = 0; i < words.length; i += wordsPerChunk) {
      chunks.push(words.slice(i, i + wordsPerChunk).join(' ') + ' ');
    }
    
    return chunks;
  }

  private static delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  // Test connection
  static async testConnection(): Promise<boolean> {
    try {
      await api.get('/');
      return true;
    } catch {
      return false;
    }
  }

  // Get confidence level color
  static getConfidenceColor(confidence: number): string {
    if (confidence >= 0.8) return '#22c55e'; // Green
    if (confidence >= 0.5) return '#f59e0b'; // Orange
    return '#ef4444'; // Red
  }

  // Format confidence as percentage
  static formatConfidence(confidence: number): string {
    return `${Math.round(confidence * 100)}%`;
  }

  // Get intent display name
  static getIntentDisplayName(intent: string): string {
    const intentMap: Record<string, string> = {
      'eligibility_check': 'Eligibility Check',
      'process_question': 'Process Question',
      'document_request': 'Document Request',
      'general_question': 'General Question',
      'legal_advice': 'Legal Advice'
    };
    
    return intentMap[intent] || intent;
  }

  // Get domain display name
  static getDomainDisplayName(domain: string): string {
    const domainMap: Record<string, string> = {
      'access_to_information': 'Access to Information',
      'privacy': 'Privacy Law',
      'employment': 'Employment Law',
      'immigration': 'Immigration Law',
      'general': 'General Law'
    };
    
    return domainMap[domain] || domain;
  }

  // Format processing time
  static formatProcessingTime(time: number): string {
    if (time < 1) {
      return `${Math.round(time * 1000)}ms`;
    } else {
      return `${time.toFixed(1)}s`;
    }
  }

  // Check if service is available
  static isServiceAvailable(services: Record<string, boolean>, service: string): boolean {
    return services[service] === true;
  }

  // Get service status icon
  static getServiceStatusIcon(isAvailable: boolean): string {
    return isAvailable ? '✅' : '❌';
  }

  // Generate sample queries
  static getSampleQueries(): string[] {
    return [
      "Can a Canadian citizen request records from Health Canada?",
      "What is the process for submitting an Access to Information request?",
      "Am I eligible to access government documents as a permanent resident?",
      "How long does the government have to respond to my request?",
      "Can I appeal if my request is denied?",
      "What types of records are available under the Access to Information Act?",
    ];
  }
}

export default ApiService;