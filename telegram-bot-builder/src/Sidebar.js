// Sidebar.js
import React from "react";

const blockTypes = [
  { type: "start", label: "Старт" },
  { type: "end", label: "Конец" },
  { type: "message", label: "Сообщение" },
  { type: "question", label: "Вопрос" },
  { type: "command", label: "Команда" },
  { type: "image", label: "Изображение" },
  { type: "gallery", label: "Галерея" },
  { type: "button", label: "Кнопки" },
  { type: "condition", label: "Условие" },
  { type: "input", label: "Ввод" },
  { type: "api", label: "API" }
];

function Sidebar() {
  const onDragStart = (event, nodeType) => {
    event.dataTransfer.setData("application/reactflow", nodeType);
    event.dataTransfer.effectAllowed = "move";
  };

  return (
    <aside style={{ width: 200, borderRight: "1px solid #ccc", padding: 10, background: "#fafafa" }}>
      <h4>Блоки</h4>
      {blockTypes.map((b) => (
        <div
          key={b.type}
          onDragStart={(e) => onDragStart(e, b.type)}
          draggable
          style={{
            padding: "8px",
            marginBottom: "6px",
            background: "#fff",
            border: "1px solid #ccc",
            borderRadius: "4px",
            cursor: "grab"
          }}
        >
          {b.label}
        </div>
      ))}
    </aside>
  );
}

export default Sidebar;
