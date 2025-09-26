export const colors = {
  start: "#a0e6a0",
  message: "#a0c4ff",
  question: "#ffd580",
  end: "#ff9999",
  command: "#c4a0ff",
  image: "#ffebcd",
  gallery: "#c2d4fe",
  button: "#ffcc99",
  inline_button: "#e83e8c",
  condition: "#b3e0ff",
  abtest: "#99ffb3",
  input: "#ffb3d1",
  api: "#ff99cc",
  random: "#d1b3ff",
  handoff: "#ccffcc",
  menu: "#ffb347",
  file: "#d4d4aa",
  nlp_response: "#f0f8ff",
  delay: "#ffe4b5",
  keyword_processor: "#FF9800",
  product_card: "#e8f5e9", // Новый цвет
  schedule: "#ce93d8", // Фиолетовый цвет для блока расписания
};

export const nodeLabels = {
  start: "Старт",
  message: "Сообщение",
  question: "Вопрос",
  end: "Конец",
  command: "Команда",
  image: "Изображение",
  gallery: "Галерея",
  button: "Кнопки",
  inline_button: "Inline-кнопки",
  condition: "Условие",
  abtest: "A/B Тест",
  input: "Ввод данных",
  api: "API Запрос",
  random: "Случайный выбор",
  handoff: "На оператора",
  menu: "Меню",
  file: "Файлы",
  nlp_response: "NLP Ответ",
  delay: "Задержка",
  keyword_processor: "Обработка по ключевым словам",
  product_card: "Карточка товара", // Новая метка
  schedule: "Расписание", // Новая метка для блока расписания
};

export const nodeTypes = Object.keys(nodeLabels);

// Адаптивные стили для узлов
export const nodeStyles = {
  mobile: {
    width: 160,
    padding: '6px',
    fontSize: '11px'
  },
  tablet: {
    width: 180,
    padding: '8px',
    fontSize: '12px'
  },
  desktop: {
    width: 200,
    padding: '10px',
    fontSize: '14px'
  }
};

// Адаптивные стили для панели управления
export const controlPanelStyles = {
  mobile: {
    padding: '8px 10px',
    fontSize: '12px',
    button: {
      padding: '4px 8px',
      fontSize: '10px',
      minWidth: '30px'
    }
  },
  tablet: {
    padding: '10px 15px',
    fontSize: '14px',
    button: {
      padding: '6px 10px',
      fontSize: '12px',
      minWidth: '40px'
    }
  },
  desktop: {
    padding: '10px 15px',
    fontSize: '14px',
    button: {
      padding: '6px 10px',
      fontSize: '12px',
      minWidth: '40px'
    }
  }
};

// Адаптивные стили для боковой панели
export const sidebarStyles = {
  mobile: {
    width: '100%',
    maxHeight: '200px',
    padding: '10px'
  },
  tablet: {
    width: '250px',
    padding: '15px'
  },
  desktop: {
    width: '250px',
    padding: '15px'
  }
};

// Адаптивные стили для списка ботов
export const botListStyles = {
  mobile: {
    gridColumns: '1fr',
    gap: '10px'
  },
  tablet: {
    gridColumns: 'repeat(auto-fill, minmax(250px, 1fr))',
    gap: '15px'
  },
  desktop: {
    gridColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
    gap: '20px'
  }
};