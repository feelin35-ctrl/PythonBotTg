import React from 'react';
import { Handle, Position } from 'reactflow';
import { colors, nodeLabels } from '../../styles';
import styled from 'styled-components';

// Стили для адаптивного дизайна узлов
const NodeContainer = styled.div`
  background: ${props => props.color || '#e8f5e9'};
  border: 2px solid ${props => props.selected ? '#ff9800' : '#4caf50'}; /* Оранжевая обводка для выбранного узла */
  border-radius: 8px;
  padding: 10px;
  width: 200px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  font-size: 14px;
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
    width: 180px;
    padding: 8px;
    font-size: 12px;
  }
  
  @media (max-width: 480px) {
    width: 160px;
    padding: 6px;
    font-size: 11px;
  }
`;

const NodeHeader = styled.div`
  font-weight: bold;
  margin-bottom: 8px;
  color: #1b5e20;
  display: flex;
  align-items: center;
  justify-content: space-between;
  
  @media (max-width: 768px) {
    margin-bottom: 6px;
  }
  
  @media (max-width: 480px) {
    margin-bottom: 4px;
  }
`;

const NodeType = styled.span`
  font-size: 0.8em;
  background: #4caf50;
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

export const ProductNode = ({ data, selected }) => {
  return (
    <NodeContainer color={colors.product_card || '#e8f5e9'} selected={selected}>
      <Handle type="target" position={Position.Top} style={{ background: "#555" }} />
      <NodeHeader>
        <span>Product Card</span>
        <NodeType>product_card</NodeType>
      </NodeHeader>
      <NodeBody>
        Карточка товара с фото и описанием
      </NodeBody>
      <Handle 
        type="source" 
        position={Position.Bottom} 
        style={{ 
          background: "#555",
          width: '12px',
          height: '12px',
          right: '50%',
          transform: 'translateX(50%)'
        }} 
        id="main"
      />
    </NodeContainer>
  );
};