// Enhanced Response Display Component for Legal AI responses

import React, { useState } from 'react';
import styled from 'styled-components';
import { ParsedResponse } from '../utils/responseParser';

const ResponseContainer = styled.div`
  margin-top: 0.75rem;
  padding: 0.75rem;
  background-color: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
`;

const SectionHeader = styled.h4`
  margin: 0 0 0.5rem 0;
  font-size: 0.85rem;
  font-weight: 600;
  color: #475569;
  display: flex;
  align-items: center;
  gap: 0.25rem;
`;

const SectionContent = styled.div`
  font-size: 0.8rem;
  line-height: 1.4;
  color: #64748b;
  margin-bottom: 0.75rem;
  
  &:last-child {
    margin-bottom: 0;
  }
`;

const ReasoningStep = styled.div`
  padding: 0.25rem 0;
  border-left: 2px solid #e2e8f0;
  padding-left: 0.5rem;
  margin: 0.25rem 0;
`;

const Citation = styled.div`
  padding: 0.25rem 0;
  font-style: italic;
`;

const ToggleButton = styled.button`
  background: none;
  border: none;
  color: #667eea;
  font-size: 0.75rem;
  cursor: pointer;
  text-decoration: underline;
  padding: 0;
  margin-top: 0.5rem;
  
  &:hover {
    color: #5a67d8;
  }
`;

const CollapsibleSection = styled.div<{ $isExpanded: boolean }>`
  max-height: ${props => props.$isExpanded ? 'none' : '0'};
  overflow: hidden;
  transition: max-height 0.2s ease;
`;

const WarningBadge = styled.span`
  background-color: #fef3c7;
  color: #d97706;
  padding: 0.125rem 0.375rem;
  border-radius: 4px;
  font-size: 0.7rem;
  font-weight: 500;
`;

const InfoBadge = styled.span`
  background-color: #dbeafe;
  color: #2563eb;
  padding: 0.125rem 0.375rem;
  border-radius: 4px;
  font-size: 0.7rem;
  font-weight: 500;
`;

interface LegalResponseDisplayProps {
  parsedResponse: ParsedResponse;
}

const LegalResponseDisplay: React.FC<LegalResponseDisplayProps> = ({ parsedResponse }) => {
  const [showReasoningSteps, setShowReasoningSteps] = useState(false);
  const [showCitations, setShowCitations] = useState(false);
  const [showLimitations, setShowLimitations] = useState(false);
  
  const hasReasoningSteps = parsedResponse.reasoning_steps && parsedResponse.reasoning_steps.length > 0;
  const hasCitations = parsedResponse.legal_citations && parsedResponse.legal_citations.length > 0;
  const hasLimitations = parsedResponse.limitations && parsedResponse.limitations.length > 0;
  const hasAdditionalInfo = parsedResponse.additional_info_needed && parsedResponse.additional_info_needed.length > 0;
  
  // Don't render if there's no additional information
  if (!hasReasoningSteps && !hasCitations && !hasLimitations && !hasAdditionalInfo) {
    return null;
  }

  return (
    <ResponseContainer>
      {hasReasoningSteps && (
        <>
          <SectionHeader>
            🧠 Legal Reasoning
            <ToggleButton onClick={() => setShowReasoningSteps(!showReasoningSteps)}>
              {showReasoningSteps ? 'Hide' : 'Show'} ({parsedResponse.reasoning_steps!.length} steps)
            </ToggleButton>
          </SectionHeader>
          <CollapsibleSection $isExpanded={showReasoningSteps}>
            <SectionContent>
              {parsedResponse.reasoning_steps!.map((step, index) => (
                <ReasoningStep key={index}>
                  <strong>{index + 1}.</strong> {step}
                </ReasoningStep>
              ))}
            </SectionContent>
          </CollapsibleSection>
        </>
      )}

      {hasCitations && (
        <>
          <SectionHeader>
            📚 Legal Citations
            <ToggleButton onClick={() => setShowCitations(!showCitations)}>
              {showCitations ? 'Hide' : 'Show'} ({parsedResponse.legal_citations!.length} sources)
            </ToggleButton>
          </SectionHeader>
          <CollapsibleSection $isExpanded={showCitations}>
            <SectionContent>
              {parsedResponse.legal_citations!.map((citation, index) => (
                <Citation key={index}>• {citation}</Citation>
              ))}
            </SectionContent>
          </CollapsibleSection>
        </>
      )}

      {hasLimitations && (
        <>
          <SectionHeader>
            ⚠️ Important Limitations <WarningBadge>Review Required</WarningBadge>
            <ToggleButton onClick={() => setShowLimitations(!showLimitations)}>
              {showLimitations ? 'Hide' : 'Show'} limitations
            </ToggleButton>
          </SectionHeader>
          <CollapsibleSection $isExpanded={showLimitations}>
            <SectionContent>
              {parsedResponse.limitations!.map((limitation, index) => (
                <div key={index} style={{ marginBottom: '0.5rem' }}>
                  • {limitation}
                </div>
              ))}
            </SectionContent>
          </CollapsibleSection>
        </>
      )}

      {hasAdditionalInfo && (
        <>
          <SectionHeader>
            📝 Additional Information Needed <InfoBadge>For Better Analysis</InfoBadge>
          </SectionHeader>
          <SectionContent>
            {parsedResponse.additional_info_needed!.map((info, index) => (
              <div key={index} style={{ marginBottom: '0.25rem' }}>
                • {info}
              </div>
            ))}
          </SectionContent>
        </>
      )}
    </ResponseContainer>
  );
};

export default LegalResponseDisplay;