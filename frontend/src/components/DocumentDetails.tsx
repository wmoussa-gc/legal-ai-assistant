// Document Details Component

import React, { useState, useEffect, useCallback } from 'react';
import styled from 'styled-components';

const Modal = styled.div`
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
  padding: 2rem;
`;

const ModalContent = styled.div`
  background: white;
  border-radius: 12px;
  max-width: 1000px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15);
`;

const Header = styled.div`
  padding: 2rem;
  border-bottom: 1px solid #e2e8f0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 12px 12px 0 0;
`;

const Title = styled.h2`
  margin: 0 0 0.5rem 0;
  font-size: 1.5rem;
  font-weight: 600;
`;

const Subtitle = styled.p`
  margin: 0;
  opacity: 0.9;
  font-size: 0.9rem;
`;

const CloseButton = styled.button`
  position: absolute;
  top: 1rem;
  right: 1rem;
  background: none;
  border: none;
  color: white;
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  
  &:hover {
    background: rgba(255, 255, 255, 0.1);
  }
`;

const Content = styled.div`
  padding: 2rem;
`;

const Section = styled.div`
  margin-bottom: 2rem;
`;

const SectionTitle = styled.h3`
  color: #1a202c;
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0 0 1rem 0;
  border-bottom: 2px solid #3b82f6;
  padding-bottom: 0.5rem;
`;

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
`;

const StatCard = styled.div`
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 1rem;
  text-align: center;
`;

const StatValue = styled.div`
  font-size: 1.5rem;
  font-weight: 600;
  color: #059669;
  margin-bottom: 0.25rem;
`;

const StatLabel = styled.div`
  font-size: 0.875rem;
  color: #64748b;
`;

const TabContainer = styled.div`
  border-bottom: 1px solid #e2e8f0;
  margin-bottom: 1rem;
`;

const TabButton = styled.button<{ active: boolean }>`
  background: none;
  border: none;
  padding: 0.75rem 1rem;
  margin-right: 1rem;
  cursor: pointer;
  font-weight: 500;
  color: ${props => props.active ? '#3b82f6' : '#64748b'};
  border-bottom: 2px solid ${props => props.active ? '#3b82f6' : 'transparent'};
  transition: all 0.2s;

  &:hover {
    color: #3b82f6;
  }
`;

const ProvisionCard = styled.div`
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  margin-bottom: 1rem;
  overflow: hidden;
`;

const ProvisionHeader = styled.div`
  background: #f8fafc;
  padding: 1rem;
  border-bottom: 1px solid #e2e8f0;
`;

const ProvisionTitle = styled.h4`
  margin: 0;
  color: #1a202c;
  font-size: 1rem;
  font-weight: 600;
`;

const ProvisionMeta = styled.div`
  font-size: 0.875rem;
  color: #64748b;
  margin-top: 0.25rem;
`;

const ProvisionText = styled.div`
  padding: 1rem;
  line-height: 1.6;
  color: #374151;
`;

const RuleCard = styled.div`
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  margin-bottom: 0.5rem;
  padding: 1rem;
`;

const RuleText = styled.code`
  display: block;
  background: #1f2937;
  color: #f9fafb;
  padding: 0.75rem;
  border-radius: 4px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 0.875rem;
  margin-bottom: 0.5rem;
  overflow-x: auto;
`;

const RuleMeta = styled.div`
  font-size: 0.75rem;
  color: #64748b;
`;

const LoadingSpinner = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  color: #64748b;
`;

interface DocumentDetailsProps {
  documentSlug: string;
  onClose: () => void;
}

const DocumentDetails: React.FC<DocumentDetailsProps> = ({ documentSlug, onClose }) => {
  const [details, setDetails] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState('overview');

  const loadDocumentDetails = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/documents/${documentSlug}/details`);
      
      if (!response.ok) {
        throw new Error('Failed to load document details');
      }
      
      const data = await response.json();
      setDetails(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load document details');
    } finally {
      setLoading(false);
    }
  }, [documentSlug]);

  useEffect(() => {
    loadDocumentDetails();
  }, [loadDocumentDetails]);

  const handleBackdropClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  if (loading) {
    return (
      <Modal onClick={handleBackdropClick}>
        <ModalContent>
          <LoadingSpinner>🔍 Loading document details...</LoadingSpinner>
        </ModalContent>
      </Modal>
    );
  }

  if (error || !details) {
    return (
      <Modal onClick={handleBackdropClick}>
        <ModalContent>
          <Header>
            <Title>Error Loading Document</Title>
            <CloseButton onClick={onClose}>×</CloseButton>
          </Header>
          <Content>
            <p>❌ {error || 'Failed to load document details'}</p>
          </Content>
        </ModalContent>
      </Modal>
    );
  }

  return (
    <Modal onClick={handleBackdropClick}>
      <ModalContent>
        <Header>
          <Title>{details.name}</Title>
          <Subtitle>📋 {details.slug}</Subtitle>
          <CloseButton onClick={onClose}>×</CloseButton>
        </Header>

        <Content>
          <StatsGrid>
            <StatCard>
              <StatValue>{details.summary.total_provisions}</StatValue>
              <StatLabel>Legal Provisions</StatLabel>
            </StatCard>
            <StatCard>
              <StatValue>{details.summary.total_rules}</StatValue>
              <StatLabel>s(CASP) Rules</StatLabel>
            </StatCard>
            <StatCard>
              <StatValue>{details.summary.unique_predicates}</StatValue>
              <StatLabel>Unique Predicates</StatLabel>
            </StatCard>
            <StatCard>
              <StatValue>{details.summary.unique_variables}</StatValue>
              <StatLabel>Unique Variables</StatLabel>
            </StatCard>
          </StatsGrid>

          <TabContainer>
            <TabButton 
              active={activeTab === 'overview'} 
              onClick={() => setActiveTab('overview')}
            >
              📊 Overview
            </TabButton>
            <TabButton 
              active={activeTab === 'provisions'} 
              onClick={() => setActiveTab('provisions')}
            >
              📄 Provisions ({details.provisions.length})
            </TabButton>
            <TabButton 
              active={activeTab === 'rules'} 
              onClick={() => setActiveTab('rules')}
            >
              ⚖️ Rules Analysis
            </TabButton>
          </TabContainer>

          {activeTab === 'overview' && (
            <Section>
              <SectionTitle>📊 Rule Type Distribution</SectionTitle>
              {Object.entries(details.rules_analysis.type_counts).map(([type, count]: [string, any]) => (
                <div key={type} style={{ marginBottom: '0.5rem' }}>
                  <strong>{type.charAt(0).toUpperCase() + type.slice(1)}:</strong> {count} rules
                </div>
              ))}

              <SectionTitle style={{ marginTop: '2rem' }}>🔝 Top Predicates</SectionTitle>
              {details.rules_analysis.top_predicates.slice(0, 5).map(([predicate, count]: [string, number], index: number) => (
                <div key={predicate} style={{ marginBottom: '0.5rem' }}>
                  <strong>{index + 1}. {predicate}</strong> - used {count} times
                </div>
              ))}
            </Section>
          )}

          {activeTab === 'provisions' && (
            <Section>
              <SectionTitle>📄 Legal Provisions</SectionTitle>
              {details.provisions.map((provision: any, index: number) => (
                <ProvisionCard key={provision.id || index}>
                  <ProvisionHeader>
                    <ProvisionTitle>{provision.title || `Provision ${index + 1}`}</ProvisionTitle>
                    <ProvisionMeta>
                      {provision.section_number && `Section: ${provision.section_number}`}
                      {provision.subsection_number && ` • Subsection: ${provision.subsection_number}`}
                      • {provision.word_count} words
                    </ProvisionMeta>
                  </ProvisionHeader>
                  <ProvisionText>{provision.full_text}</ProvisionText>
                </ProvisionCard>
              ))}
            </Section>
          )}

          {activeTab === 'rules' && (
            <Section>
              <SectionTitle>⚖️ Sample s(CASP) Rules</SectionTitle>
              
              {/* Debug info - can remove later */}
              {process.env.NODE_ENV === 'development' && (
                <div style={{ background: '#f3f4f6', padding: '1rem', marginBottom: '1rem', borderRadius: '4px', fontSize: '0.875rem' }}>
                  <strong>Debug:</strong> Available rule types: {Object.keys(details.rules_analysis.sample_rules).join(', ')}
                </div>
              )}
              
              {Object.entries(details.rules_analysis.sample_rules).map(([type, rules]: [string, any]) => (
                rules && rules.length > 0 && (
                  <div key={type} style={{ marginBottom: '2rem' }}>
                    <h4 style={{ color: '#374151', marginBottom: '1rem' }}>
                      {type.charAt(0).toUpperCase() + type.slice(1)} Examples ({rules.length}):
                    </h4>
                    {rules.map((rule: any, index: number) => (
                      <RuleCard key={index}>
                        <RuleText>{rule.rule_text}</RuleText>
                        <RuleMeta>
                          Variables: {rule.variables?.join(', ') || 'None'} • 
                          Predicates: {rule.predicates?.join(', ') || 'None'}
                        </RuleMeta>
                      </RuleCard>
                    ))}
                  </div>
                )
              ))}
              
              {/* Show message if no sample rules */}
              {Object.values(details.rules_analysis.sample_rules).every((rules: any) => !rules || rules.length === 0) && (
                <div style={{ 
                  padding: '2rem', 
                  textAlign: 'center', 
                  color: '#64748b',
                  background: '#f8fafc',
                  borderRadius: '8px',
                  border: '2px dashed #e2e8f0'
                }}>
                  <p>📝 No sample rules available for display</p>
                  <p style={{ fontSize: '0.875rem', marginTop: '0.5rem' }}>
                    This document has {details.summary.total_rules} total rules, but no samples could be extracted for preview.
                  </p>
                </div>
              )}
            </Section>
          )}
        </Content>
      </ModalContent>
    </Modal>
  );
};

export default DocumentDetails;