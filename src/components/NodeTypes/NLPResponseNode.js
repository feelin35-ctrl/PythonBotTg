import React from 'react';
import { Handle, Position } from 'reactflow';
import styled from 'styled-components';

const NodeContainer = styled.div`
  background: #f0f8ff;
  border: 2px solid #4682b4;
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
  color: #4682b4;
  display: flex;
  align-items: center;
  justify-content: space-between;
`;

const NodeType = styled.span`
  font-size: 0.8em;
  background: #4682b4;
  color: white;
  padding: 2px 6px;
  border-radius: 4px;
`;

const NodeBody = styled.div`
  font-size: 0.9em;
  color: #333;
`;

const NLPResponseNode = ({ data }) => {
  // Добавляем отладочный вывод
  console.log('Rendering NLPResponseNode with data:', data);
  
  return (
    <NodeContainer>
      <Handle
        type="target"
        position={Position.Top}
        style={{ background: '#555' }}
      />
      <NodeHeader>
        <span>NLP Response</span>
        <NodeType>nlp_response</NodeType>
      </NodeHeader>
      <NodeBody>
        Обрабатывает естественный язык и формирует ответы на основе контекста сообщений пользователей
      </NodeBody>
      <div style={{ 
        fontSize: '0.7em', 
        color: '#666', 
        marginTop: '8px',
        fontStyle: 'italic',
        textAlign: 'center'
      }}>
        Перетащите этот блок в редактор
      </div>
      {/* Добавляем отладочную информацию */}
      <div style={{ 
        fontSize: '0.6em', 
        color: '#999', 
        marginTop: '5px',
        textAlign: 'center'
      }}>
        Тип: nlp_response
      </div>
      <Handle
        type="source"
        position={Position.Bottom}
        style={{ background: '#555' }}
      />
    </NodeContainer>
  );
};

export default NLPResponseNode;