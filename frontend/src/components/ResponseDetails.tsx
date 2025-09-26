// Response Details Modal Component

import React from 'react';
import styled from 'styled-components';
import { LegalResponse } from '../types';
import ApiService from '../services/api';

const ModalOverlay = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
`;

const ModalContent = styled.div`
  background: white;
  border-radius: 12px;
  width: 100%;
  max-width: 800px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
`;

const ModalHeader = styled.div`
  padding: 1.5rem 2rem 1rem;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
`;

const ModalTitle = styled.h2`
  margin: 0;
  font-size: 1.25rem;
  color: #1e293b;
`;

const CloseButton = styled.button`
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #64748b;
  padding: 0;
  margin-left: 1rem;

  &:hover {
    color: #1e293b;
  }
`;

const ModalBody = styled.div`
  padding: 1.5rem 2rem;
`;

const Section = styled.div`
  margin-bottom: 2rem;

  &:last-child {
    margin-bottom: 0;
  }
`;

const SectionTitle = styled.h3`
  margin: 0 0 1rem 0;
  font-size: 1rem;
  font-weight: 600;
  color: #374151;
  display: flex;
  align-items: center;
  gap: 0.5rem;
`;

const MetadataGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
`;

const MetadataItem = styled.div`
  padding: 1rem;
  background: #f8fafc;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
`;

const MetadataLabel = styled.div`
  font-size: 0.75rem;
  font-weight: 500;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 0.25rem;
`;

const MetadataValue = styled.div`
  font-size: 1rem;
  color: #1e293b;
  font-weight: 500;
`;

const ConfidenceMeter = styled.div`
  width: 100%;
  height: 8px;
  background: #e2e8f0;
  border-radius: 4px;
  overflow: hidden;
  margin-top: 0.5rem;
`;

const ConfidenceBar = styled.div<{ $width: number; $color: string }>`
  height: 100%;
  width: ${props => props.$width}%;
  background-color: ${props => props.$color};
  transition: width 0.3s ease;
`;

const ReasoningList = styled.ol`
  list-style: none;
  counter-reset: step-counter;
  padding: 0;
`;

const ReasoningItem = styled.li`
  counter-increment: step-counter;
  margin-bottom: 1rem;
  padding: 1rem;
  background: #f8fafc;
  border-radius: 8px;
  border-left: 4px solid #667eea;
  position: relative;

  &::before {
    content: counter(step-counter);
    position: absolute;
    left: -2px;
    top: -2px;
    background: #667eea;
    color: white;
    width: 24px;
    height: 24px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.75rem;
    font-weight: bold;
  }
`;

const CitationList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 1rem;
`;

const CitationItem = styled.div`
  padding: 1rem;
  background: #fefce8;
  border: 1px solid #fde047;
  border-radius: 8px;
`;

const CitationTitle = styled.div`
  font-weight: 600;
  color: #365314;
  margin-bottom: 0.5rem;
`;

const CitationText = styled.div`
  color: #4d7c0f;
  font-size: 0.9rem;
  line-height: 1.5;
`;

const Badge = styled.span<{ $variant: 'success' | 'warning' | 'error' | 'info' }>`
  display: inline-flex;
  align-items: center;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 500;
  
  ${props => {
    switch (props.$variant) {
      case 'success':
        return 'background: #dcfce7; color: #166534;';
      case 'warning':
        return 'background: #fef3c7; color: #92400e;';
      case 'error':
        return 'background: #fecaca; color: #991b1b;';
      case 'info':
      default:
        return 'background: #dbeafe; color: #1e40af;';
    }
  }}
`;

const CodeBlock = styled.pre`
  background: #1e293b;
  color: #e2e8f0;
  padding: 1rem;
  border-radius: 8px;
  overflow-x: auto;
  font-size: 0.875rem;
  margin: 0.5rem 0;
`;

const WarningBox = styled.div`
  background: #fef3c7;
  border: 1px solid #f59e0b;
  color: #92400e;
  padding: 1rem;
  border-radius: 8px;
  margin-top: 1rem;
`;

interface ResponseDetailsProps {
  response: LegalResponse;
  onClose: () => void;
}

const ResponseDetails: React.FC<ResponseDetailsProps> = ({ response, onClose }) => {
  const handleOverlayClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <ModalOverlay onClick={handleOverlayClick}>
      <ModalContent>
        <ModalHeader>
          <ModalTitle>Response Details</ModalTitle>
          <CloseButton onClick={onClose}>&times;</CloseButton>
        </ModalHeader>

        <ModalBody>
          {/* Metadata Section */}
          <Section>
            <SectionTitle>📊 Analysis Summary</SectionTitle>
            <MetadataGrid>
              <MetadataItem>
                <MetadataLabel>Confidence</MetadataLabel>
                <MetadataValue>{ApiService.formatConfidence(response.confidence)}</MetadataValue>
                <ConfidenceMeter>
                  <ConfidenceBar 
                    $width={response.confidence * 100} 
                    $color={ApiService.getConfidenceColor(response.confidence)}
                  />
                </ConfidenceMeter>
              </MetadataItem>

              <MetadataItem>
                <MetadataLabel>Intent</MetadataLabel>
                <MetadataValue>{ApiService.getIntentDisplayName(response.intent)}</MetadataValue>
              </MetadataItem>

              <MetadataItem>
                <MetadataLabel>Legal Domain</MetadataLabel>
                <MetadataValue>{ApiService.getDomainDisplayName(response.legal_domain)}</MetadataValue>
              </MetadataItem>

              <MetadataItem>
                <MetadataLabel>Processing Time</MetadataLabel>
                <MetadataValue>{ApiService.formatProcessingTime(response.processing_time)}</MetadataValue>
              </MetadataItem>

              <MetadataItem>
                <MetadataLabel>Model Used</MetadataLabel>
                <MetadataValue>{response.model_used}</MetadataValue>
              </MetadataItem>

              <MetadataItem>
                <MetadataLabel>Query ID</MetadataLabel>
                <MetadataValue style={{ fontFamily: 'monospace', fontSize: '0.8rem' }}>
                  {response.query_id}
                </MetadataValue>
              </MetadataItem>
            </MetadataGrid>
          </Section>

          {/* Entities Section */}
          {response.entities_found.length > 0 && (
            <Section>
              <SectionTitle>🔍 Extracted Entities</SectionTitle>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                {response.entities_found.map((entity, index) => (
                  <Badge key={index} $variant="info">{entity}</Badge>
                ))}
              </div>
            </Section>
          )}

          {/* Formal Verification Section */}
          {response.formal_verification && (
            <Section>
              <SectionTitle>
                ⚙️ Formal Verification
                <Badge $variant={response.formal_verification.success ? 'success' : 'error'}>
                  {response.formal_verification.success ? 'Passed' : 'Failed'}
                </Badge>
              </SectionTitle>
              
              <div>
                <strong>Query Executed:</strong>
                <CodeBlock>{response.formal_verification.query_executed}</CodeBlock>
              </div>

              {response.formal_verification.solutions.length > 0 && (
                <div>
                  <strong>Solutions:</strong>
                  {response.formal_verification.solutions.map((solution, index) => (
                    <CodeBlock key={index}>
                      {JSON.stringify(solution, null, 2)}
                    </CodeBlock>
                  ))}
                </div>
              )}

              <div>
                <strong>Execution Time:</strong> {ApiService.formatProcessingTime(response.formal_verification.execution_time)}
              </div>

              {response.formal_verification.error_message && (
                <div style={{ marginTop: '0.5rem' }}>
                  <strong>Error:</strong>
                  <div style={{ color: '#dc2626', marginTop: '0.25rem' }}>
                    {response.formal_verification.error_message}
                  </div>
                </div>
              )}
            </Section>
          )}

          {/* Reasoning Steps Section */}
          {response.reasoning_steps.length > 0 && (
            <Section>
              <SectionTitle>💭 Reasoning Steps</SectionTitle>
              <ReasoningList>
                {response.reasoning_steps.map((step, index) => (
                  <ReasoningItem key={index}>
                    <div style={{ marginLeft: '1rem' }}>
                      <div style={{ fontWeight: '500', marginBottom: '0.5rem' }}>
                        {step.description}
                      </div>
                      {step.rule_applied && (
                        <div style={{ fontSize: '0.8rem', color: '#64748b' }}>
                          Rule: <code>{step.rule_applied}</code>
                        </div>
                      )}
                      <div style={{ fontSize: '0.9rem', color: '#059669', marginTop: '0.25rem' }}>
                        → {step.conclusion}
                      </div>
                    </div>
                  </ReasoningItem>
                ))}
              </ReasoningList>
            </Section>
          )}

          {/* Legal Citations Section */}
          {response.legal_citations.length > 0 && (
            <Section>
              <SectionTitle>📚 Legal Citations</SectionTitle>
              <CitationList>
                {response.legal_citations.map((citation, index) => (
                  <CitationItem key={index}>
                    <CitationTitle>
                      {citation.title} 
                      {citation.section && ` (Section ${citation.section})`}
                    </CitationTitle>
                    <div style={{ fontSize: '0.8rem', color: '#4d7c0f', marginBottom: '0.5rem' }}>
                      {citation.source_document}
                    </div>
                    <CitationText>{citation.text}</CitationText>
                  </CitationItem>
                ))}
              </CitationList>
            </Section>
          )}

          {/* Limitations and Recommendations */}
          <Section>
            <SectionTitle>⚠️ Important Notes</SectionTitle>
            
            {response.limitations.length > 0 && (
              <div style={{ marginBottom: '1rem' }}>
                <strong>Limitations:</strong>
                <ul style={{ marginTop: '0.5rem', paddingLeft: '1.5rem' }}>
                  {response.limitations.map((limitation, index) => (
                    <li key={index} style={{ marginBottom: '0.25rem' }}>{limitation}</li>
                  ))}
                </ul>
              </div>
            )}

            {response.human_lawyer_recommended && (
              <WarningBox>
                <strong>⚠️ Legal Consultation Recommended</strong>
                <p style={{ margin: '0.5rem 0 0 0' }}>
                  This response has medium/low confidence or involves complex legal matters. 
                  Consider consulting with a qualified legal professional for authoritative advice.
                </p>
              </WarningBox>
            )}
          </Section>

          {/* Follow-up Questions */}
          {response.follow_up_questions.length > 0 && (
            <Section>
              <SectionTitle>💡 Suggested Follow-up Questions</SectionTitle>
              <ul style={{ paddingLeft: '1.5rem' }}>
                {response.follow_up_questions.map((question, index) => (
                  <li key={index} style={{ marginBottom: '0.5rem', color: '#4f46e5' }}>
                    {question}
                  </li>
                ))}
              </ul>
            </Section>
          )}
        </ModalBody>
      </ModalContent>
    </ModalOverlay>
  );
};

export default ResponseDetails;