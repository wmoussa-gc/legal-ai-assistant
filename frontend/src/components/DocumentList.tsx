// Document List Component

import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import ApiService from '../services/api';
import DocumentDetails from './DocumentDetails';
import { DocumentInfo } from '../types';

const DocumentContainer = styled.div`
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 1rem;
  margin: 1rem 0;
`;

const DocumentHeader = styled.div`
  display: flex;
  justify-content: between;
  align-items: center;
  margin-bottom: 0.5rem;
`;

const DocumentTitle = styled.h3`
  color: #1a202c;
  font-size: 1.1rem;
  font-weight: 600;
  margin: 0;
  flex-grow: 1;
`;

const DocumentStats = styled.div`
  display: flex;
  gap: 1rem;
  font-size: 0.875rem;
  color: #64748b;
`;

const StatItem = styled.div`
  display: flex;
  align-items: center;
  gap: 0.25rem;
`;

const StatLabel = styled.span`
  font-weight: 500;
`;

const StatValue = styled.span`
  color: #059669;
  font-weight: 600;
`;

const DocumentSlug = styled.div`
  font-size: 0.875rem;
  color: #64748b;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  background: #f1f5f9;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  margin-top: 0.5rem;
`;

const LoadingMessage = styled.div`
  color: #64748b;
  font-style: italic;
  padding: 1rem;
  text-align: center;
`;

const ErrorMessage = styled.div`
  color: #dc2626;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 4px;
  padding: 0.75rem;
  margin: 1rem 0;
`;

const NoDocuments = styled.div`
  color: #64748b;
  font-style: italic;
  padding: 2rem;
  text-align: center;
  border: 2px dashed #e2e8f0;
  border-radius: 8px;
  margin: 1rem 0;
`;

const RefreshButton = styled.button`
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  cursor: pointer;
  transition: background-color 0.2s;

  &:hover {
    background: #2563eb;
  }

  &:disabled {
    background: #9ca3af;
    cursor: not-allowed;
  }
`;

const ViewDetailsButton = styled.button`
  background: #059669;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  cursor: pointer;
  transition: background-color 0.2s;
  margin-top: 1rem;

  &:hover {
    background: #047857;
  }

  &:disabled {
    background: #9ca3af;
    cursor: not-allowed;
  }
`;

interface DocumentListProps {
  className?: string;
}

const DocumentList: React.FC<DocumentListProps> = ({ className }) => {
  const [documents, setDocuments] = useState<DocumentInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedDocument, setSelectedDocument] = useState<string | null>(null);

  const loadDocuments = async () => {
    try {
      setLoading(true);
      setError(null);
      const docs = await ApiService.getDocuments();
      setDocuments(docs);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load documents');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDocuments();
  }, []);

  if (loading) {
    return (
      <DocumentContainer className={className}>
        <LoadingMessage>📚 Loading legal documents...</LoadingMessage>
      </DocumentContainer>
    );
  }

  if (error) {
    return (
      <DocumentContainer className={className}>
        <ErrorMessage>
          ❌ Error loading documents: {error}
          <br />
          <RefreshButton onClick={loadDocuments} style={{ marginTop: '0.5rem' }}>
            Retry
          </RefreshButton>
        </ErrorMessage>
      </DocumentContainer>
    );
  }

  if (documents.length === 0) {
    return (
      <DocumentContainer className={className}>
        <NoDocuments>
          📄 No legal documents loaded
          <br />
          <small>Add .blawx files to the data directory to get started</small>
        </NoDocuments>
      </DocumentContainer>
    );
  }

  return (
    <DocumentContainer className={className}>
      <DocumentHeader>
        <DocumentTitle>📚 Loaded Legal Documents ({documents.length})</DocumentTitle>
        <RefreshButton onClick={loadDocuments}>Refresh</RefreshButton>
      </DocumentHeader>
      
      {documents.map((doc, index) => (
        <DocumentContainer key={index} style={{ margin: '0.5rem 0', background: 'white' }}>
          <DocumentHeader>
            <DocumentTitle>{doc.name}</DocumentTitle>
          </DocumentHeader>
          
          <DocumentStats>
            <StatItem>
              <StatLabel>Provisions:</StatLabel>
              <StatValue>{doc.provisions_count}</StatValue>
            </StatItem>
            <StatItem>
              <StatLabel>Rules:</StatLabel>
              <StatValue>{doc.rules_count}</StatValue>
            </StatItem>
            {doc.categories && doc.categories.length > 0 && (
              <StatItem>
                <StatLabel>Categories:</StatLabel>
                <StatValue>{doc.categories.join(', ')}</StatValue>
              </StatItem>
            )}
          </DocumentStats>
          
          {doc.slug && (
            <DocumentSlug>📋 {doc.slug}</DocumentSlug>
          )}
          
          {doc.slug && (
            <ViewDetailsButton onClick={() => setSelectedDocument(doc.slug)}>
              🔍 View Details & Analysis
            </ViewDetailsButton>
          )}
        </DocumentContainer>
      ))}
      
      {selectedDocument && (
        <DocumentDetails
          documentSlug={selectedDocument}
          onClose={() => setSelectedDocument(null)}
        />
      )}
    </DocumentContainer>
  );
};

export default DocumentList;