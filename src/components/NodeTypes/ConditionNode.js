import React from 'react';
import { Handle, Position } from 'reactflow';
import styled from 'styled-components';

const NodeContainer = styled.div`
  background: #fff8e1;
  border: 2px solid #ffc107;
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
  color: #ff6f00;
  display: flex;
  align-items: center;
  justify-content: space-between;
`;

const NodeType = styled.span`
  font-size: 0.8em;
  background: #ffc107;
  color: black;
  padding: 2px 6px;
  border-radius: 4px;
`;

const NodeBody = styled.div`
  font-size: 0.9em;
  color: #333;
`;

const ConditionNode = ({ data }) => {
  return (
    <NodeContainer>
      <Handle
        type="target"
        position={Position.Top}
        style={{ background: '#555' }}
      />
      <NodeHeader>
        <span>Condition</span>
        <NodeType>condition</NodeType>
      </NodeHeader>
      <NodeBody>
        Условный переход на основе переменных
      </NodeBody>
      <Handle
        type="source"
        position={Position.Bottom}
        style={{ background: '#555' }}
      />
    </NodeContainer>
  );
};

export default ConditionNode;