import React from 'react';

const BlockTest = () => {
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
      type: 'end',
      title: 'End',
      description: 'Конец сценария'
    }
  ];

  return (
    <div style={{ padding: '20px' }}>
      <h2>Тест отображения блоков</h2>
      <p>Проверка, что все блоки корректно отображаются:</p>
      <ul>
        {blocks.map((block, index) => (
          <li key={index} style={{ marginBottom: '10px', padding: '10px', border: '1px solid #ccc' }}>
            <strong>{block.title}</strong> ({block.type})
            <br />
            <small>{block.description}</small>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default BlockTest;