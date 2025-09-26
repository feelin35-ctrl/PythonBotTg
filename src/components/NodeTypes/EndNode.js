import React from 'react';
import { Handle, Position } from 'reactflow';
import styled from 'styled-components';

const NodeContainer = styled.div`
  background: #ffebee;
  border: 2px solid ${props => props.selected ? '#ff9800' : '#f44336'}; /* Оранжевая обводка для выбранного узла */
  border-radius: 8px;
  padding: 10px;
  width: 200px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  
  /* Добавляем стиль для выбранного узла */
  ${props => props.selected && `
    box-shadow: 0 0 0 2px rgba(255, 152, 0, 0.5), 0 6px 12px rgba(0, 0, 0, 0.15);
    transform: translateY(-2px);
  `}
  
  &:hover {
    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
    transform: translateY(-2px);
    
    /* Увеличиваем тень при наведении на выбранный узел */
    ${props => props.selected && `
      box-shadow: 0 0 0 2px rgba(255, 152, 0, 0.7), 0 8px 16px rgba(0, 0, 0, 0.2);
    `}
  }
`;

const NodeHeader = styled.div`
  font-weight: bold;
  margin-bottom: 8px;
  color: #b71c1c;
  display: flex;
  align-items: center;
  justify-content: space-between;
`;

const NodeType = styled.span`
  font-size: 0.8em;
  background: #f44336;
  color: white;
  padding: 2px 6px;
  border-radius: 4px;
`;

const NodeBody = styled.div`
  font-size: 0.9em;
  color: #333;
`;

const EndNode = ({ data, selected }) => {
  return (
    <NodeContainer selected={selected}>
      <Handle
        type="target"
        position={Position.Top}
        style={{ background: '#555' }}
      />
      <NodeHeader>
        <span>End</span>
        <NodeType>end</NodeType>
      </NodeHeader>
      <NodeBody>
        Конец сценария бота
      </NodeBody>
    </NodeContainer>
  );
};

export default EndNode;