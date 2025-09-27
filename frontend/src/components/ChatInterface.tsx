// Main Chat Interface Component

import React, { useState, useEffect, useRef } from 'react';
import styled from 'styled-components';
import { ChatMessage, LegalResponse, SystemStatus, DocumentInfo } from '../types';
import ApiService from '../services/api';
import MessageBubble from './MessageBubble';
import InputArea from './InputArea';
import SystemStatusBar from './SystemStatusBar';
import ResponseDetails from './ResponseDetails';
import DocumentList from './DocumentList';

const ChatContainer = styled.div`
  display: flex;
  flex-direction: column;
  height: 100vh;
  max-width: 1200px;
  margin: 0 auto;
  background-color: #f8fafc;
`;

const Header = styled.header`
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 1rem 2rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
`;

const Title = styled.h1`
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
`;

const Subtitle = styled.p`
  margin: 0.25rem 0 0 0;
  opacity: 0.9;
  font-size: 0.9rem;
`;

const MessagesContainer = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
`;

const EmptyState = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  text-align: center;
  color: #64748b;
`;

const SampleQueriesContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-top: 2rem;
`;

const SampleQuery = styled.button`
  padding: 0.75rem 1rem;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  cursor: pointer;
  text-align: left;
  color: #475569;
  transition: all 0.2s ease;

  &:hover {
    border-color: #667eea;
    background-color: #f8fafc;
  }
`;

const ErrorMessage = styled.div`
  background-color: #fef2f2;
  border: 1px solid #fecaca;
  color: #dc2626;
  padding: 1rem;
  border-radius: 8px;
  margin: 1rem;
`;

const LoadingIndicator = styled.div`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #64748b;
  margin: 1rem;
  padding: 1rem;
  background: linear-gradient(90deg, #f1f5f9, #e2e8f0, #f1f5f9);
  background-size: 200% 100%;
  animation: shimmer 2s infinite;
  border-radius: 8px;
  
  @keyframes shimmer {
    0% { background-position: -200% 0; }
    100% { background-position: 200% 0; }
  }
`;

const ProcessingSteps = styled.div`
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  font-size: 0.85rem;
`;

const ProcessingStep = styled.div<{ $completed: boolean }>`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: ${props => props.$completed ? '#059669' : '#64748b'};
  
  &::before {
    content: '${props => props.$completed ? '✓' : '⏳'}';
    font-size: 0.8rem;
  }
`;

interface ChatInterfaceProps {
  className?: string;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({ className }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);
  const [documents, setDocuments] = useState<DocumentInfo[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [selectedResponse, setSelectedResponse] = useState<LegalResponse | null>(null);
  const [processingSteps, setProcessingSteps] = useState<{ step: string; completed: boolean }[]>([]);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Scroll to bottom when new messages are added
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Load initial data
  useEffect(() => {
    loadSystemStatus();
    loadDocuments();
  }, []);

  const loadSystemStatus = async () => {
    try {
      const status = await ApiService.getHealth();
      setSystemStatus(status);
    } catch (err) {
      console.error('Failed to load system status:', err);
      setError('Failed to connect to the backend service');
    }
  };

  const loadDocuments = async () => {
    try {
      const docs = await ApiService.getDocuments();
      setDocuments(docs);
    } catch (err) {
      console.error('Failed to load documents:', err);
    }
  };

  const handleSendMessage = async (queryText: string, context?: string) => {
    if (!queryText.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      type: 'user',
      content: queryText,
      timestamp: new Date(),
    };

    const loadingMessage: ChatMessage = {
      id: `loading-${Date.now()}`,
      type: 'assistant',
      content: 'Processing your query...',
      timestamp: new Date(),
      isLoading: true,
    };

    setMessages(prev => [...prev, userMessage, loadingMessage]);
    setIsLoading(true);
    setError(null);

    // Initialize processing steps
    const steps = [
      { step: 'Analyzing your question...', completed: false },
      { step: 'Searching legal documents...', completed: false },
      { step: 'Applying formal reasoning...', completed: false },
      { step: 'Generating response...', completed: false }
    ];
    setProcessingSteps(steps);

    try {
      let stepIndex = 0;
      
      await ApiService.submitQueryStream(
        { query: queryText, context },
        (chunk) => {
          // Simulate processing step progression
          if (stepIndex < steps.length - 1) {
            setProcessingSteps(prev => prev.map((step, index) => 
              index <= stepIndex ? { ...step, completed: true } : step
            ));
            stepIndex++;
          }

          // Update the loading message with partial response
          setMessages(prev => prev.map(msg => 
            msg.id === loadingMessage.id 
              ? { ...msg, content: chunk, isLoading: true }
              : msg
          ));
        },
        (response) => {
          // Complete all processing steps
          setProcessingSteps(prev => prev.map(step => ({ ...step, completed: true })));

          // Final response received
          const assistantMessage: ChatMessage = {
            id: `assistant-${Date.now()}`,
            type: 'assistant',
            content: response.answer,
            timestamp: new Date(),
            response: response,
            isLoading: false,
          };

          setMessages(prev => prev.map(msg => 
            msg.id === loadingMessage.id ? assistantMessage : msg
          ));

          setIsLoading(false);
          setProcessingSteps([]);
        },
        (error) => {
          console.error('Query failed:', error);
          setError(error.message);
          setProcessingSteps([]);
          
          const errorMessage: ChatMessage = {
            id: `error-${Date.now()}`,
            type: 'system',
            content: `Error: ${error.message}`,
            timestamp: new Date(),
          };

          setMessages(prev => prev.map(msg => 
            msg.id === loadingMessage.id ? errorMessage : msg
          ));

          setIsLoading(false);
        }
      );

    } catch (err: any) {
      console.error('Query failed:', err);
      setError(err.message);
      
      const errorMessage: ChatMessage = {
        id: `error-${Date.now()}`,
        type: 'system',
        content: `Error: ${err.message}`,
        timestamp: new Date(),
      };

      setMessages(prev => prev.map(msg => 
        msg.id === loadingMessage.id ? errorMessage : msg
      ));

      setIsLoading(false);
    }
  };

  const handleSampleQuery = (query: string) => {
    handleSendMessage(query);
  };

  const handleClearChat = () => {
    setMessages([]);
    setError(null);
    setSelectedResponse(null);
  };

  const showResponseDetails = (response: LegalResponse) => {
    setSelectedResponse(response);
  };

  return (
    <ChatContainer className={className}>
      <Header>
        <Title>Legal AI Assistant</Title>
        <Subtitle>
          Ask questions about legal matters with formal verification • 
          {documents.length} legal documents loaded
        </Subtitle>
      </Header>

      <SystemStatusBar 
        status={systemStatus} 
        onRefresh={loadSystemStatus}
      />

      {error && (
        <ErrorMessage>
          <strong>Connection Error:</strong> {error}
          <button 
            onClick={() => setError(null)}
            style={{ float: 'right', background: 'none', border: 'none', cursor: 'pointer' }}
          >
            ×
          </button>
        </ErrorMessage>
      )}

      <MessagesContainer>
        {messages.length === 0 ? (
          <EmptyState>
            <h2>Welcome to Legal AI Assistant</h2>
            <p>
              Ask questions about legal matters and get answers backed by formal logic verification.
              <br />
              Try one of these sample queries to get started:
            </p>
            
            <SampleQueriesContainer>
              {ApiService.getSampleQueries().map((query, index) => (
                <SampleQuery 
                  key={index}
                  onClick={() => handleSampleQuery(query)}
                  disabled={isLoading}
                >
                  {query}
                </SampleQuery>
              ))}
            </SampleQueriesContainer>

            <DocumentList />
          </EmptyState>
        ) : (
          <>
            {messages.map((message) => (
              <MessageBubble
                key={message.id}
                message={message}
                onShowDetails={message.response ? () => showResponseDetails(message.response!) : undefined}
              />
            ))}
            <div ref={messagesEndRef} />
          </>
        )}
      </MessagesContainer>

      {/* Show processing steps when actively processing */}
      {isLoading && processingSteps.length > 0 && (
        <LoadingIndicator>
          <div style={{ fontWeight: 500 }}>Processing your legal query...</div>
          <ProcessingSteps>
            {processingSteps.map((step, index) => (
              <ProcessingStep key={index} $completed={step.completed}>
                {step.step}
              </ProcessingStep>
            ))}
          </ProcessingSteps>
        </LoadingIndicator>
      )}

      <InputArea
        onSendMessage={handleSendMessage}
        isLoading={isLoading}
        onClearChat={handleClearChat}
        disabled={!!error}
      />

      {selectedResponse && (
        <ResponseDetails
          response={selectedResponse}
          onClose={() => setSelectedResponse(null)}
        />
      )}
    </ChatContainer>
  );
};

export default ChatInterface;