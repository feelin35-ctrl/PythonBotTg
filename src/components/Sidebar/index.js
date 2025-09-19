import React from 'react';
import { nodeLabels, colors } from '../../styles';

const SidebarComponent = () => {
  const onDragStart = (event, nodeType) => {
    event.dataTransfer.setData("application/reactflow", nodeType);
    event.dataTransfer.effectAllowed = "move";
    console.log('Drag started with type:', nodeType);
  };

  return (
    <aside style={{
      width: 250,
      borderRight: "1px solid #ccc",
      padding: 15,
      background: "#f0f0f0",
      display: "flex",
      flexDirection: "column",
    }}>
      <div style={{ marginBottom: 20 }}>
        <h4>Доступные блоки</h4>
        <p style={{ fontSize: '12px', color: '#666', margin: '5px 0' }}>
          Перетащите блок в рабочую область
        </p>
      </div>
      <div style={{ flexGrow: 1, overflowY: "auto" }}>
        {Object.entries(nodeLabels).map(([type, label]) => (
          <div
            key={type}
            onDragStart={(event) => onDragStart(event, type)}
            draggable
            style={{
              padding: 10,
              border: "1px solid #777",
              borderRadius: 5,
              marginBottom: 10,
              background: colors[type] || "#fff",
              cursor: "grab",
              textAlign: "center",
              userSelect: "none"
            }}
          >
            {label}
          </div>
        ))}
      </div>
    </aside>
  );
};

export default SidebarComponent;