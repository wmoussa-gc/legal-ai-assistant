// Input Area Component for sending messages

import React, { useState, KeyboardEvent, useRef } from 'react';
import styled from 'styled-components';

const InputContainer = styled.div`
  padding: 1rem 2rem;
  border-top: 1px solid #e2e8f0;
  background: white;
  box-shadow: 0 -2px 8px rgba(0,0,0,0.1);
`;

const InputForm = styled.form`
  display: flex;
  align-items: flex-end;
  gap: 0.75rem;
  max-width: 100%;
`;

const TextAreaWrapper = styled.div`
  flex: 1;
  position: relative;
`;

const TextArea = styled.textarea`
  width: 100%;
  min-height: 44px;
  max-height: 120px;
  padding: 0.75rem 1rem;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  font-size: 1rem;
  font-family: inherit;
  resize: none;
  outline: none;
  transition: border-color 0.2s ease;

  &:focus {
    border-color: #667eea;
  }

  &:disabled {
    background-color: #f1f5f9;
    cursor: not-allowed;
  }

  &::placeholder {
    color: #94a3b8;
  }
`;

const ButtonContainer = styled.div`
  display: flex;
  gap: 0.5rem;
  align-items: flex-end;
`;

const SendButton = styled.button`
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
  min-height: 44px;

  &:hover:not(:disabled) {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
    box-shadow: none;
  }
`;

const ClearButton = styled.button`
  padding: 0.75rem 1rem;
  background: transparent;
  color: #64748b;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s ease;
  min-height: 44px;

  &:hover:not(:disabled) {
    border-color: #dc2626;
    color: #dc2626;
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const CharacterCount = styled.div`
  position: absolute;
  bottom: -20px;
  right: 0;
  font-size: 0.75rem;
  color: #94a3b8;
`;

const Suggestions = styled.div`
  display: flex;
  gap: 0.5rem;
  margin-top: 0.5rem;
  flex-wrap: wrap;
`;

const SuggestionChip = styled.button`
  padding: 0.25rem 0.75rem;
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  font-size: 0.8rem;
  color: #475569;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: #e2e8f0;
    border-color: #667eea;
  }
`;

interface InputAreaProps {
  onSendMessage: (message: string, context?: string) => void;
  isLoading: boolean;
  onClearChat: () => void;
  disabled?: boolean;
}

const InputArea: React.FC<InputAreaProps> = ({ 
  onSendMessage, 
  isLoading, 
  onClearChat, 
  disabled = false 
}) => {
  const [message, setMessage] = useState('');
  const [context, setContext] = useState('');
  const textAreaRef = useRef<HTMLTextAreaElement>(null);

  const maxLength = 2000;
  
  const followUpSuggestions = [
    "Can you explain that in simpler terms?",
    "What are the specific requirements?",
    "How long does this process take?",
    "What if I don't meet these criteria?",
    "Are there any exceptions?",
    "What documents do I need?"
  ];

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!message.trim() || isLoading || disabled) return;
    
    onSendMessage(message.trim(), context.trim() || undefined);
    setMessage('');
    setContext('');
    
    // Reset textarea height
    if (textAreaRef.current) {
      textAreaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleTextAreaChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const value = e.target.value;
    if (value.length <= maxLength) {
      setMessage(value);
      
      // Auto-resize textarea
      const textarea = e.target;
      textarea.style.height = 'auto';
      textarea.style.height = `${Math.min(textarea.scrollHeight, 120)}px`;
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    if (!isLoading && !disabled) {
      onSendMessage(suggestion);
    }
  };

  const remainingChars = maxLength - message.length;
  const isNearLimit = remainingChars < 100;

  return (
    <InputContainer>
      <InputForm onSubmit={handleSubmit}>
        <TextAreaWrapper>
          <TextArea
            ref={textAreaRef}
            value={message}
            onChange={handleTextAreaChange}
            onKeyDown={handleKeyDown}
            placeholder={
              disabled 
                ? "Connection error - please check your network"
                : "Ask a legal question... (Press Enter to send, Shift+Enter for new line)"
            }
            disabled={isLoading || disabled}
            rows={1}
          />
          {message.length > 0 && (
            <CharacterCount style={{ color: isNearLimit ? '#dc2626' : '#94a3b8' }}>
              {remainingChars} characters remaining
            </CharacterCount>
          )}
        </TextAreaWrapper>

        <ButtonContainer>
          <ClearButton
            type="button"
            onClick={onClearChat}
            disabled={isLoading || disabled}
            title="Clear chat history"
          >
            Clear
          </ClearButton>
          
          <SendButton
            type="submit"
            disabled={!message.trim() || isLoading || disabled}
          >
            {isLoading ? 'Sending...' : 'Send'}
          </SendButton>
        </ButtonContainer>
      </InputForm>

      {!isLoading && !disabled && message.length === 0 && (
        <Suggestions>
          {followUpSuggestions.map((suggestion, index) => (
            <SuggestionChip
              key={index}
              type="button"
              onClick={() => handleSuggestionClick(suggestion)}
            >
              {suggestion}
            </SuggestionChip>
          ))}
        </Suggestions>
      )}
    </InputContainer>
  );
};

export default InputArea;