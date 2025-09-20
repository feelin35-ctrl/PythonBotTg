import React from 'react';
import { Handle, Position } from 'reactflow';
import styled from 'styled-components';

const NodeContainer = styled.div`
  background: #e8f5e9;
  border: 2px solid #4caf50;
  border-radius: 8px;
  padding: 10px;
  width: 200px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  
  &:hover {
    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
    transform: translateY(-2px);
  }
`;

const NodeHeader = styled.div`
  font-weight: bold;
  margin-bottom: 8px;
  color: #2e7d32;
  display: flex;
  align-items: center;
  justify-content: space-between;
`;

const NodeType = styled.span`
  font-size: 0.8em;
  background: #4caf50;
  color: white;
  padding: 2px 6px;
  border-radius: 4px;
`;

const NodeBody = styled.div`
  font-size: 0.9em;
  color: #333;
`;

const StartNode = ({ data }) => {
  return (
    <NodeContainer>
      <Handle
        type="source"
        position={Position.Bottom}
        style={{ background: '#555' }}
      />
      <NodeHeader>
        <span>Start</span>
        <NodeType>start</NodeType>
      </NodeHeader>
      <NodeBody>
        Начальный узел сценария бота
      </NodeBody>
    </NodeContainer>
  );
};

export default StartNode;