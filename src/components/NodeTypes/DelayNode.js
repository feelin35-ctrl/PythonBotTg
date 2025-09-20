import React from 'react';
import { Handle, Position } from 'reactflow';
import styled from 'styled-components';

const NodeContainer = styled.div`
  background: #ffe4b5;
  border: 2px solid #ffa500;
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
  color: #8b4513;
  display: flex;
  align-items: center;
  justify-content: space-between;
`;

const NodeType = styled.span`
  font-size: 0.8em;
  background: #ffa500;
  color: white;
  padding: 2px 6px;
  border-radius: 4px;
`;

const NodeBody = styled.div`
  font-size: 0.9em;
  color: #333;
`;

const DelayNode = ({ data }) => {
  return (
    <NodeContainer>
      <Handle
        type="target"
        position={Position.Top}
        style={{ background: '#555' }}
      />
      <NodeHeader>
        <span>Задержка отправки</span>
        <NodeType>delay</NodeType>
      </NodeHeader>
      <NodeBody>
        {data.hours || data.minutes || data.seconds ? (
          <>
            Задержка: {data.hours || 0} ч {data.minutes || 0} мин {data.seconds || 0} сек
          </>
        ) : (
          "Настройте задержку"
        )}
      </NodeBody>
      <Handle
        type="source"
        position={Position.Bottom}
        style={{ background: '#555' }}
      />
    </NodeContainer>
  );
};

export default DelayNode;