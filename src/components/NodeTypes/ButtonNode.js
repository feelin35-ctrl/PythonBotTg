import React from 'react';
import { Handle, Position } from 'reactflow';
import styled from 'styled-components';

const NodeContainer = styled.div`
  background: #fff3e0;
  border: 2px solid ${props => props.selected ? '#ff9800' : '#ff9800'}; /* Оранжевая обводка для выбранного узла */
  border-radius: 8px;
  padding: 10px;
  width: 240px; /* Увеличена ширина на 20% (с 200px до 240px) */
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  position: relative;
  
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
  color: #e65100;
  display: flex;
  align-items: center;
  justify-content: space-between;
  
  @media (max-width: 768px) {
    margin-bottom: 6px;
  }
`;

const NodeType = styled.span`
  font-size: 0.8em;
  background: #ff9800;
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

const ButtonNode = ({ data, selected }) => {
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
    <NodeContainer selected={selected}>
      <Handle
        type="target"
        position={Position.Top}
        style={{ background: '#555' }}
      />
      <NodeHeader>
        <span>Button</span>
        <NodeType>button</NodeType>
      </NodeHeader>
      <NodeBody>
        Отправка кнопок для взаимодействия с пользователем
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

export default ButtonNode;