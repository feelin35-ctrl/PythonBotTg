import React from 'react';
import { EditableNode } from './EditableNode';

// Иконка для блока обработки ключевых слов
const KeywordIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M19 3H5C3.9 3 3 3.9 3 5V19C3 20.1 3.9 21 5 21H19C20.1 21 21 20.1 21 19V5C21 3.9 20.1 3 19 3Z" stroke="#FF9800" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    <path d="M9 9H15" stroke="#FF9800" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    <path d="M9 13H15" stroke="#FF9800" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    <path d="M9 17H13" stroke="#FF9800" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
);

export const KeywordProcessorNode = ({ data, selected, ...props }) => {
  // Создаем объект данных для EditableNode, сохраняя пользовательские значения
  const nodeData = {
    ...data,
    icon: <KeywordIcon />,
    title: "Обработка по ключевым словам",
    color: "#FF9800",
    description: "Блок для обработки текстовых сообщений с использованием ключевых слов",
    // Используем значения из data или значения по умолчанию
    keywords: data.keywords || [],
    caseSensitive: data.caseSensitive !== undefined ? data.caseSensitive : false,
    matchMode: data.matchMode || "exact"
  };

  return (
    <EditableNode 
      data={nodeData} 
      selected={selected}
      {...props} 
    />
  );
};

export default KeywordProcessorNode;