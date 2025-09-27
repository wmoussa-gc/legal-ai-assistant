// Message Bubble Component for displaying chat messages

import React from 'react';
import styled from 'styled-components';
import { ChatMessage } from '../types';
import ApiService from '../services/api';
import { parseResponseContent } from '../utils/responseParser';
import LegalResponseDisplay from './LegalResponseDisplay';

const BubbleContainer = styled.div<{ $isUser: boolean }>`
  display: flex;
  justify-content: ${props => props.$isUser ? 'flex-end' : 'flex-start'};
  margin: 0.5rem 0;
`;

const Bubble = styled.div<{ $isUser: boolean; $isSystem?: boolean }>`
  max-width: 70%;
  padding: 1rem;
  border-radius: 18px;
  position: relative;
  word-wrap: break-word;
  
  ${props => props.$isUser ? `
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border-bottom-right-radius: 4px;
  ` : props.$isSystem ? `
    background: #f1f5f9;
    color: #475569;
    border: 1px solid #e2e8f0;
    font-style: italic;
  ` : `
    background: white;
    color: #1e293b;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    border-bottom-left-radius: 4px;
    border: 1px solid #e2e8f0;
  `}
`;

const MessageContent = styled.div`
  line-height: 1.5;
  white-space: pre-wrap;
`;

const MessageMeta = styled.div<{ $isUser: boolean }>`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.5rem;
  font-size: 0.75rem;
  opacity: 0.7;
  ${props => props.$isUser ? 'justify-content: flex-end;' : ''}
`;

const LoadingDots = styled.div`
  display: inline-flex;
  align-items: center;
  gap: 2px;
  
  &::after {
    content: '';
    display: inline-block;
    width: 4px;
    height: 4px;
    border-radius: 50%;
    background-color: currentColor;
    animation: loading 1.4s infinite both;
  }
  
  &::before {
    content: '';
    display: inline-block;
    width: 4px;
    height: 4px;
    border-radius: 50%;
    background-color: currentColor;
    animation: loading 1.4s infinite both;
    animation-delay: 0.2s;
    margin-right: 2px;
  }
  
  @keyframes loading {
    0%, 80%, 100% {
      opacity: 0;
      transform: scale(0.8);
    }
    40% {
      opacity: 1;
      transform: scale(1);
    }
  }
`;

const ConfidenceBadge = styled.span<{ $confidence: number }>`
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  color: white;
  background-color: ${props => ApiService.getConfidenceColor(props.$confidence)};
`;

const ResponseActions = styled.div`
  display: flex;
  gap: 0.5rem;
  margin-top: 0.75rem;
`;

const ActionButton = styled.button`
  padding: 0.5rem 1rem;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  background: white;
  color: #475569;
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    border-color: #667eea;
    background-color: #f8fafc;
  }
`;

const VerificationStatus = styled.div<{ $success: boolean }>`
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.75rem;
  color: ${props => props.$success ? '#059669' : '#dc2626'};
  margin-top: 0.5rem;
`;

interface MessageBubbleProps {
  message: ChatMessage;
  onShowDetails?: () => void;
}

const MessageBubble: React.FC<MessageBubbleProps> = ({ message, onShowDetails }) => {
  const isUser = message.type === 'user';
  const isSystem = message.type === 'system';
  const response = message.response;

  const formatTime = (timestamp: Date) => {
    return timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  // Parse the message content to handle JSON responses
  const parsedContent = !isUser && !isSystem ? parseResponseContent(message.content) : null;
  const displayContent = parsedContent ? parsedContent.answer : message.content;

  return (
    <BubbleContainer $isUser={isUser}>
      <Bubble $isUser={isUser} $isSystem={isSystem}>
        <MessageContent>
          {message.isLoading ? (
            <div>
              {displayContent}
              <LoadingDots />
            </div>
          ) : (
            displayContent
          )}
        </MessageContent>

        {/* Show enhanced response details if we have parsed JSON data */}
        {parsedContent && !message.isLoading && (
          <LegalResponseDisplay parsedResponse={parsedContent} />
        )}

        {response && !message.isLoading && (
          <>
            <MessageMeta $isUser={isUser}>
              <ConfidenceBadge $confidence={response.confidence}>
                {ApiService.formatConfidence(response.confidence)} confidence
              </ConfidenceBadge>
              
              <span>{ApiService.getIntentDisplayName(response.intent)}</span>
              <span>•</span>
              <span>{ApiService.formatProcessingTime(response.processing_time)}</span>
            </MessageMeta>

            {response.formal_verification && (
              <VerificationStatus $success={response.formal_verification.success}>
                {response.formal_verification.success ? '✓' : '⚠'} 
                Formal verification {response.formal_verification.success ? 'passed' : 'failed'}
              </VerificationStatus>
            )}

            <ResponseActions>
              {onShowDetails && (
                <ActionButton onClick={onShowDetails}>
                  View Details
                </ActionButton>
              )}
              
              {response.legal_citations.length > 0 && (
                <ActionButton>
                  {response.legal_citations.length} Citation{response.legal_citations.length !== 1 ? 's' : ''}
                </ActionButton>
              )}

              {response.human_lawyer_recommended && (
                <ActionButton style={{ borderColor: '#f59e0b', color: '#f59e0b' }}>
                  ⚠ Lawyer Recommended
                </ActionButton>
              )}
            </ResponseActions>
          </>
        )}

        <MessageMeta $isUser={isUser}>
          <span>{formatTime(message.timestamp)}</span>
          {response && response.model_used && (
            <>
              <span>•</span>
              <span>{response.model_used}</span>
            </>
          )}
        </MessageMeta>
      </Bubble>
    </BubbleContainer>
  );
};

export default MessageBubble;