// System Status Bar Component

import React from 'react';
import styled from 'styled-components';
import { SystemStatus } from '../types';
import ApiService from '../services/api';

const StatusBar = styled.div<{ $status: 'healthy' | 'warning' | 'error' }>`
  padding: 0.5rem 2rem;
  background-color: ${props => 
    props.$status === 'healthy' ? '#ecfdf5' :
    props.$status === 'warning' ? '#fffbeb' : '#fef2f2'
  };
  border-bottom: 1px solid ${props => 
    props.$status === 'healthy' ? '#d1fae5' :
    props.$status === 'warning' ? '#fed7aa' : '#fecaca'
  };
  color: ${props => 
    props.$status === 'healthy' ? '#065f46' :
    props.$status === 'warning' ? '#92400e' : '#991b1b'
  };
  font-size: 0.875rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
`;

const StatusContent = styled.div`
  display: flex;
  align-items: center;
  gap: 1rem;
`;

const StatusIndicator = styled.div<{ $status: 'healthy' | 'warning' | 'error' }>`
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: ${props => 
    props.$status === 'healthy' ? '#10b981' :
    props.$status === 'warning' ? '#f59e0b' : '#ef4444'
  };
  flex-shrink: 0;
`;

const ServicesList = styled.div`
  display: flex;
  gap: 1rem;
  align-items: center;
`;

const ServiceItem = styled.span<{ $available: boolean }>`
  display: flex;
  align-items: center;
  gap: 0.25rem;
  opacity: ${props => props.$available ? 1 : 0.6};
`;

const RefreshButton = styled.button`
  padding: 0.25rem 0.75rem;
  background: transparent;
  border: 1px solid currentColor;
  border-radius: 4px;
  color: inherit;
  font-size: 0.8rem;
  cursor: pointer;
  transition: opacity 0.2s ease;

  &:hover {
    opacity: 0.8;
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const HiddenBar = styled.div`
  height: 0;
  overflow: hidden;
  transition: height 0.3s ease;
`;

interface SystemStatusBarProps {
  status: SystemStatus | null;
  onRefresh: () => void;
  collapsed?: boolean;
}

const SystemStatusBar: React.FC<SystemStatusBarProps> = ({ 
  status, 
  onRefresh, 
  collapsed = false 
}) => {
  if (!status) {
    return (
      <StatusBar $status="error">
        <StatusContent>
          <StatusIndicator $status="error" />
          <span>Unable to connect to backend services</span>
        </StatusContent>
        <RefreshButton onClick={onRefresh}>
          Retry
        </RefreshButton>
      </StatusBar>
    );
  }

  const getOverallStatus = (): 'healthy' | 'warning' | 'error' => {
    if (status.status === 'healthy') {
      const criticalServices = ['scasp_engine', 'blawx_parser'];
      const criticalAvailable = criticalServices.every(service => 
        ApiService.isServiceAvailable(status.services, service)
      );
      
      if (criticalAvailable) {
        return 'healthy';
      } else {
        return 'warning';
      }
    }
    return 'error';
  };

  const overallStatus = getOverallStatus();
  const uptime = Math.floor(status.uptime / 3600);

  if (collapsed) {
    return <HiddenBar />;
  }

  return (
    <StatusBar $status={overallStatus}>
      <StatusContent>
        <StatusIndicator $status={overallStatus} />
        
        <span>
          System {overallStatus} • {status.loaded_documents.length} documents • 
          {status.total_rules} rules • {uptime}h uptime
        </span>

        <ServicesList>
          <ServiceItem $available={ApiService.isServiceAvailable(status.services, 'scasp_engine')}>
            {ApiService.getServiceStatusIcon(ApiService.isServiceAvailable(status.services, 'scasp_engine'))} Logic Engine
          </ServiceItem>
          
          <ServiceItem $available={ApiService.isServiceAvailable(status.services, 'llm_service')}>
            {ApiService.getServiceStatusIcon(ApiService.isServiceAvailable(status.services, 'llm_service'))} AI Model
          </ServiceItem>
          
          <ServiceItem $available={ApiService.isServiceAvailable(status.services, 'blawx_parser')}>
            {ApiService.getServiceStatusIcon(ApiService.isServiceAvailable(status.services, 'blawx_parser'))} Document Parser
          </ServiceItem>
        </ServicesList>
      </StatusContent>

      <RefreshButton onClick={onRefresh}>
        Refresh
      </RefreshButton>
    </StatusBar>
  );
};

export default SystemStatusBar;