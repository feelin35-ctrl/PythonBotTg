import React from 'react';
import { Handle, Position } from 'reactflow';
import styled from 'styled-components';

const NodeContainer = styled.div`
  background: #e0f7fa;
  border: 2px solid #00bcd4;
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
  color: #006064;
  display: flex;
  align-items: center;
  justify-content: space-between;
`;

const NodeType = styled.span`
  font-size: 0.8em;
  background: #00bcd4;
  color: white;
  padding: 2px 6px;
  border-radius: 4px;
`;

const NodeBody = styled.div`
  font-size: 0.9em;
  color: #333;
`;

const MenuNode = ({ data }) => {
  return (
    <NodeContainer>
      <Handle
        type="target"
        position={Position.Top}
        style={{ background: '#555' }}
      />
      <NodeHeader>
        <span>Menu</span>
        <NodeType>menu</NodeType>
      </NodeHeader>
      <NodeBody>
        Пункт меню для навигации
      </NodeBody>
      <Handle
        type="source"
        position={Position.Bottom}
        style={{ background: '#555' }}
      />
    </NodeContainer>
  );
};

export default MenuNode;