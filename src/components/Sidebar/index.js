import React from 'react';
import { nodeLabels, colors } from '../../styles';
import styled from 'styled-components';

const SidebarContainer = styled.aside`
  width: 250px;
  border-right: 1px solid #ccc;
  padding: 15px;
  background: #f0f0f0;
  display: flex;
  flex-direction: column;
  
  @media (max-width: 768px) {
    width: 100%;
    border-right: none;
    border-bottom: 1px solid #ccc;
    height: auto;
    max-height: 200px;
  }
`;

const BlockList = styled.div`
  flex-grow: 1;
  overflow-y: auto;
  
  @media (max-width: 768px) {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    max-height: 150px;
  }
`;

const BlockItem = styled.div`
  padding: 10px;
  border: 1px solid #777;
  border-radius: 5px;
  margin-bottom: 10px;
  background: ${props => props.color || "#fff"};
  cursor: grab;
  text-align: center;
  user-select: none;
  
  @media (max-width: 768px) {
    flex: 1 1 calc(50% - 5px);
    margin-bottom: 0;
    min-width: 120px;
    font-size: 14px;
  }
  
  @media (max-width: 480px) {
    flex: 1 1 calc(100% - 10px);
    font-size: 12px;
  }
`;

const SidebarComponent = () => {
  const onDragStart = (event, nodeType) => {
    event.dataTransfer.setData("application/reactflow", nodeType);
    event.dataTransfer.effectAllowed = "move";
    console.log('Drag started with type:', nodeType);
  };

  // Добавляем отладочный вывод
  console.log('Available node labels:', nodeLabels);
  console.log('Available node types:', Object.keys(nodeLabels));

  return (
    <SidebarContainer>
      <div style={{ marginBottom: 20 }}>
        <h4>Доступные блоки</h4>
        <p style={{ fontSize: '12px', color: '#666', margin: '5px 0' }}>
          Перетащите блок в рабочую область
        </p>
        {/* Отладочная информация */}
        <div style={{ fontSize: '10px', color: '#999', marginTop: '5px' }}>
          Всего блоков: {Object.keys(nodeLabels).length}
        </div>
      </div>
      <BlockList>
        {Object.entries(nodeLabels).map(([type, label]) => (
          <BlockItem
            key={type}
            color={colors[type] || "#fff"}
            onDragStart={(event) => onDragStart(event, type)}
            draggable
          >
            {label}
            {/* Отображаем тип блока для отладки */}
            <div style={{ fontSize: '10px', color: '#666', marginTop: '3px' }}>
              ({type})
            </div>
          </BlockItem>
        ))}
      </BlockList>
    </SidebarContainer>
  );
};

export default SidebarComponent;