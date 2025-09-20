import React from 'react';
import { Handle, Position } from 'reactflow';
import styled from 'styled-components';

const NodeContainer = styled.div`
  background: #f3e5f5;
  border: 2px solid #9c27b0;
  border-radius: 8px;
  padding: 10px;
  width: 240px; /* Увеличена ширина на 20% (с 200px до 240px) */
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  position: relative;
  
  &:hover {
    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
    transform: translateY(-2px);
  }
  
  @media (max-width: 768px) {
    width: 216px; /* 180px + 20% */
    padding: 8px;
  }
  
  @media (max-width: 480px) {
    width: 192px; /* 160px + 20% */
    padding: 6px;
  }
`;

const NodeHeader = styled.div`
  font-weight: bold;
  margin-bottom: 8px;
  color: #4a148c;
  display: flex;
  align-items: center;
  justify-content: space-between;
  
  @media (max-width: 768px) {
    margin-bottom: 6px;
  }
`;

const NodeType = styled.span`
  font-size: 0.8em;
  background: #9c27b0;
  color: white;
  padding: 2px 6px;
  border-radius: 4px;
  
  @media (max-width: 768px) {
    padding: 1px 4px;
  }
`;

const NodeBody = styled.div`
  font-size: 0.9em;
  color: #333;
  
  @media (max-width: 480px) {
    font-size: 0.85em;
  }
`;

// Стили для контейнера кнопки с точкой выхода
const ButtonContainer = styled.div`
  position: relative;
  width: 100%;
  margin-bottom: 5px;
  
  &:last-child {
    margin-bottom: 0;
  }
`;

const ButtonInput = styled.input`
  width: 100%;
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 14px;
  
  @media (max-width: 768px) {
    padding: 6px;
    font-size: 12px;
  }
  
  @media (max-width: 480px) {
    padding: 5px;
    font-size: 11px;
  }
`;

const InlineButtonNode = ({ data }) => {
  // Создаем точки выхода для каждой кнопки пользователя
  const renderButtons = () => {
    const buttons = data.buttons || [];
    
    return buttons.map((button, index) => (
      <ButtonContainer key={index}>
        <ButtonInput 
          type="text" 
          value={button.label || ''} 
          placeholder="Текст кнопки"
          readOnly
        />
        <Handle
          type="source"
          position={Position.Right}
          id={`button-${index}`}
          style={{
            top: "50%",
            transform: "translateY(-50%)",
            background: '#555',
            width: '10px',
            height: '10px',
            right: '-5px'
          }}
        />
      </ButtonContainer>
    ));
  };

  return (
    <NodeContainer>
      <Handle
        type="target"
        position={Position.Top}
        style={{ background: '#555' }}
      />
      <NodeHeader>
        <span>Inline Button</span>
        <NodeType>inline_button</NodeType>
      </NodeHeader>
      <NodeBody>
        Отправка встроенных кнопок в сообщении
      </NodeBody>
      {renderButtons()}
      {/* Основная точка выхода для возможности подключения к следующему блоку */}
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

export default InlineButtonNode;