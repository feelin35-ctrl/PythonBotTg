import React, { useState } from 'react';
import { Handle, Position } from 'reactflow';
import styled from 'styled-components';

const NodeContainer = styled.div`
  background: #f3e5f5;
  border: 2px solid ${props => props.selected ? '#9c27b0' : '#9c27b0'};
  border-radius: 8px;
  padding: 10px;
  width: 240px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  position: relative;
  
  ${props => props.selected && `
    box-shadow: 0 0 0 2px rgba(156, 39, 176, 0.5), 0 6px 12px rgba(0, 0, 0, 0.15);
    transform: translateY(-2px);
  `}
  
  &:hover {
    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
    transform: translateY(-2px);
    
    ${props => props.selected && `
      box-shadow: 0 0 0 2px rgba(156, 39, 176, 0.7), 0 8px 16px rgba(0, 0, 0, 0.2);
    `}
  }
`;

const NodeHeader = styled.div`
  font-weight: bold;
  margin-bottom: 8px;
  color: #4a148c;
  display: flex;
  align-items: center;
  justify-content: space-between;
`;

const NodeType = styled.span`
  font-size: 0.8em;
  background: #9c27b0;
  color: white;
  padding: 2px 6px;
  border-radius: 4px;
`;

const NodeBody = styled.div`
  font-size: 0.9em;
  color: #333;
  margin-bottom: 10px;
`;

const ConfigSection = styled.div`
  margin: 10px 0;
  padding: 8px;
  background: rgba(156, 39, 176, 0.1);
  border-radius: 4px;
`;

const ConfigLabel = styled.div`
  font-weight: bold;
  font-size: 0.8em;
  color: #4a148c;
  margin-bottom: 4px;
`;

const ConfigValue = styled.div`
  font-size: 0.8em;
  color: #333;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
`;

const ScheduleNode = ({ data, selected }) => {
  const [showConfig, setShowConfig] = useState(false);
  
  // Configuration values with defaults
  const dateQuestion = data.dateQuestion || 'На какую дату вы хотите записаться?';
  const timeQuestion = data.timeQuestion || 'На какое время вы хотите записаться?';
  const minDate = data.minDate || 'today';
  const maxDate = data.maxDate || 'today + 30 дней';
  const timeInterval = data.timeInterval || 30;
  const workStartTime = data.workStartTime || '09:00';
  const workEndTime = data.workEndTime || '18:00';
  const crmIntegration = data.crmIntegration || false;
  const crmEndpoint = data.crmEndpoint || '';
  const unavailableMessage = data.unavailableMessage || 'Извините, это время уже занято. Пожалуйста, выберите другое.';

  return (
    <NodeContainer selected={selected} onClick={() => setShowConfig(!showConfig)}>
      <Handle
        type="target"
        position={Position.Top}
        style={{ background: '#555' }}
      />
      <NodeHeader>
        <span>Schedule</span>
        <NodeType>schedule</NodeType>
      </NodeHeader>
      <NodeBody>
        Блок для записи пользователей на дату и время
      </NodeBody>
      
      {showConfig && (
        <>
          <ConfigSection>
            <ConfigLabel>Вопрос о дате:</ConfigLabel>
            <ConfigValue>{dateQuestion}</ConfigValue>
          </ConfigSection>
          
          <ConfigSection>
            <ConfigLabel>Вопрос о времени:</ConfigLabel>
            <ConfigValue>{timeQuestion}</ConfigValue>
          </ConfigSection>
          
          <ConfigSection>
            <ConfigLabel>Диапазон дат:</ConfigLabel>
            <ConfigValue>{minDate} - {maxDate}</ConfigValue>
          </ConfigSection>
          
          <ConfigSection>
            <ConfigLabel>Рабочие часы:</ConfigLabel>
            <ConfigValue>{workStartTime} - {workEndTime} ({timeInterval} мин)</ConfigValue>
          </ConfigSection>
          
          {crmIntegration && (
            <ConfigSection>
              <ConfigLabel>CRM интеграция:</ConfigLabel>
              <ConfigValue>{crmEndpoint || 'Не указан'}</ConfigValue>
            </ConfigSection>
          )}
        </>
      )}
      
      <Handle
        type="source"
        position={Position.Bottom}
        id="main"
        style={{ 
          background: '#555',
          width: '12px',
          height: '12px',
          right: '50%',
          transform: 'translateX(50%)'
        }}
      />
    </NodeContainer>
  );
};

export default ScheduleNode;