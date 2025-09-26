import React from 'react';
import styled from 'styled-components';
import { useBotEditor } from '../components/BotEditor/useBotEditor';

const SidebarContainer = styled.div`
  width: 250px;
  background-color: #f8f9fa;
  border-right: 1px solid #dee2e6;
  padding: 20px;
  overflow-y: auto;
  height: 100%;
  box-sizing: border-box;
`;

const SectionTitle = styled.h3`
  margin-top: 0;
  margin-bottom: 15px;
  color: #495057;
  font-size: 18px;
`;

const BlockList = styled.ul`
  list-style: none;
  padding: 0;
  margin: 0;
`;

const BlockItem = styled.li`
  padding: 10px;
  margin-bottom: 10px;
  background-color: #fff;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  cursor: grab;
  transition: all 0.2s ease;
  
  &:hover {
    background-color: #e9ecef;
    transform: translateY(-2px);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }
  
  &:active {
    cursor: grabbing;
  }
`;

const BlockTitle = styled.div`
  font-weight: bold;
  color: #495057;
  margin-bottom: 5px;
`;

const BlockDescription = styled.div`
  font-size: 12px;
  color: #6c757d;
`;

const Sidebar = () => {
  const { addNode } = useBotEditor();

  const blocks = [
    {
      type: 'start',
      title: 'Start',
      description: 'Начальный узел бота'
    },
    {
      type: 'message',
      title: 'Message',
      description: 'Отправка текстового сообщения'
    },
    {
      type: 'image',
      title: 'Image',
      description: 'Отправка изображения'
    },
    {
      type: 'button',
      title: 'Button',
      description: 'Кнопки для взаимодействия'
    },
    {
      type: 'inline_button',
      title: 'Inline Button',
      description: 'Встроенные кнопки в сообщении'
    },
    {
      type: 'condition',
      title: 'Condition',
      description: 'Условный переход'
    },
    {
      type: 'menu',
      title: 'Menu',
      description: 'Пункт меню'
    },
    {
      type: 'file',
      title: 'File',
      description: 'Отправка файла'
    },
    {
      type: 'nlp_response',
      title: 'NLP Response',
      description: 'Обработка естественного языка'
    },
    {
      type: 'keyword_processor',
      title: 'Keyword Processor',
      description: 'Обработка по ключевым словам'
    },
    {
      type: 'product_card',
      title: 'Product Card',
      description: 'Карточка товара с фото и описанием'
    },
    {
      type: 'schedule',
      title: 'Schedule',
      description: 'Блок для записи пользователей на дату и время'
    },
    {
      type: 'end',
      title: 'End',
      description: 'Конец сценария'
    },
    {
      type: 'delay',
      title: 'Delay',
      description: 'Задержка отправки сообщения'
    }
  ];

  const handleDragStart = (event, blockType) => {
    event.dataTransfer.setData('application/reactflow', blockType);
    event.dataTransfer.effectAllowed = 'move';
  };

  // Добавляем отладочный вывод в консоль
  console.log('Available blocks:', blocks);

  return (
    <SidebarContainer>
      <SectionTitle>Блоки</SectionTitle>
      <BlockList>
        {blocks.map((block) => (
          <BlockItem
            key={block.type}
            draggable
            onDragStart={(event) => handleDragStart(event, block.type)}
          >
            <BlockTitle>{block.title}</BlockTitle>
            <BlockDescription>{block.description}</BlockDescription>
            {/* Отображаем тип блока для отладки */}
            <div style={{ fontSize: '10px', color: '#999', marginTop: '3px' }}>
              Тип: {block.type}
            </div>
          </BlockItem>
        ))}
      </BlockList>
    </SidebarContainer>
  );
};

export default Sidebar;