import React, { useState, useEffect } from 'react';
import { Handle, Position } from 'reactflow';
import { colors, nodeLabels } from '../../styles';
import { ContextMenu } from './ContextMenu';

export const EditableNode = ({ id, data, selected, onDelete }) => {
  const [contextMenu, setContextMenu] = useState(null);
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    console.log(`Node ${id} rendered with data:`, data);
    setIsMounted(true);
  }, [id, data]);

  const handleContextMenu = (event) => {
    event.preventDefault();
    setContextMenu({ x: event.clientX, y: event.clientY });
  };

  const handleDelete = () => {
    onDelete?.(id);
    setContextMenu(null);
  };

  const handleCloseMenu = () => {
    setContextMenu(null);
  };

  const handleInputChange = (e, field) => {
    if (data.onChange) {
      data.onChange(id, { [field]: e.target.value });
    }
  };

  const handleButtonChange = (e, index) => {
    if (data.onChange) {
      const newButtons = [...(data.buttons || [])];
      newButtons[index].label = e.target.value;
      data.onChange(id, { buttons: newButtons });
    }
  };

  const handleButtonCallbackChange = (e, index) => {
    if (data.onChange) {
      const newButtons = [...(data.buttons || [])];
      newButtons[index].callbackData = e.target.value;
      data.onChange(id, { buttons: newButtons });
    }
  };

  const handleAddButton = () => {
    if (data.onChange) {
      data.onChange(id, {
        buttons: [...(data.buttons || []), { label: "Новая кнопка", callbackData: "" }],
      });
    }
  };

  const handleRemoveButton = (index) => {
    if (data.onChange) {
      const newButtons = (data.buttons || []).filter((_, i) => i !== index);
      data.onChange(id, { buttons: newButtons });
    }
  };

  const handleImageChange = (e, index) => {
    if (data.onChange) {
      const newImages = [...(data.images || [])];
      newImages[index] = e.target.value;
      data.onChange(id, { images: newImages });
    }
  };

  const handleAddImage = () => {
    if (data.onChange) {
      data.onChange(id, { images: [...(data.images || []), ""] });
    }
  };

  const handleRemoveImage = (index) => {
    if (data.onChange) {
      const newImages = (data.images || []).filter((_, i) => i !== index);
      data.onChange(id, { images: newImages });
    }
  };

  const renderContent = () => {
    if (!data.blockType) {
      return <div style={{ color: 'red' }}>Ошибка: нет типа блока</div>;
    }

    switch (data.blockType) {
      case "message":
      case "command":
      case "question":
        return (
          <>
            <div style={{ fontWeight: "bold", fontSize: "0.8em", marginBottom: 5 }}>
              {nodeLabels[data.blockType]?.toUpperCase() || data.blockType.toUpperCase()}
            </div>
            <textarea
              value={data.label || ""}
              onChange={(e) => handleInputChange(e, "label")}
              className="nodrag"
              style={{
                width: "100%",
                minHeight: 50,
                resize: "vertical",
                textAlign: "center",
                border: "none",
                outline: "none",
                background: "transparent",
                boxSizing: "border-box",
              }}
              placeholder={nodeLabels[data.blockType] ? `${nodeLabels[data.blockType]} текст` : "Текст"}
            />
          </>
        );
      case "image":
        return (
          <>
            <div style={{ fontWeight: "bold", fontSize: "0.8em", marginBottom: 5 }}>
              {nodeLabels.image.toUpperCase()}
            </div>
            <input
              type="text"
              placeholder="URL изображения"
              value={data.url || ""}
              onChange={(e) => handleInputChange(e, "url")}
              className="nodrag"
              style={{
                width: "100%",
                textAlign: "center",
                border: "none",
                outline: "none",
                background: "transparent",
                marginBottom: 5,
                boxSizing: "border-box",
              }}
            />
            {data.url && (
              <img
                src={data.url}
                alt="preview"
                style={{ maxWidth: "100%", height: "auto", maxHeight: "100px" }}
                onError={(e) => {
                  e.target.style.display = 'none';
                }}
              />
            )}
          </>
        );
      case "gallery":
        return (
          <>
            <div style={{ fontWeight: "bold", fontSize: "0.8em", marginBottom: 5 }}>
              {nodeLabels.gallery.toUpperCase()}
            </div>
            {(data.images || []).map((image, index) => (
              <div
                key={index}
                style={{
                  display: "flex",
                  alignItems: "center",
                  marginBottom: 5,
                }}
              >
                <input
                  type="text"
                  placeholder={`Изображение ${index + 1} URL`}
                  value={image || ""}
                  onChange={(e) => handleImageChange(e, index)}
                  className="nodrag"
                  style={{
                    flexGrow: 1,
                    border: "1px solid #ccc",
                    padding: 5,
                    boxSizing: "border-box",
                    fontSize: "12px"
                  }}
                />
                <button
                  onClick={() => handleRemoveImage(index)}
                  style={{
                    marginLeft: 5,
                    cursor: "pointer",
                    background: "none",
                    border: "none",
                    color: "red",
                    fontSize: "16px"
                  }}
                >
                  &times;
                </button>
              </div>
            ))}
            <button
              onClick={handleAddImage}
              style={{
                width: "100%",
                cursor: "pointer",
                padding: 5,
                marginTop: 5,
                fontSize: "12px"
              }}
            >
              + Добавить изображение
            </button>
          </>
        );
      case "button":
        return (
          <>
            <div style={{ fontWeight: "bold", fontSize: "0.8em", marginBottom: 5 }}>
              {nodeLabels.button.toUpperCase()}
            </div>
            <div style={{ fontSize: "0.7em", color: "#666", marginBottom: 8 }}>
              🔗 Подключите ответы к точкам снизу
            </div>
            {(data.buttons || []).map((button, index) => (
              <div
                key={index}
                style={{
                  display: "flex",
                  alignItems: "center",
                  marginBottom: 5,
                  position: 'relative'
                }}
              >
                <div style={{
                  width: '12px',
                  height: '12px',
                  borderRadius: '50%',
                  background: '#555',
                  marginRight: '8px',
                  flexShrink: 0
                }} />
                <input
                  type="text"
                  value={button.label || ""}
                  onChange={(e) => handleButtonChange(e, index)}
                  className="nodrag"
                  style={{
                    flexGrow: 1,
                    border: "1px solid #ccc",
                    padding: 5,
                    boxSizing: "border-box",
                    fontSize: "12px"
                  }}
                />
                <button
                  onClick={() => handleRemoveButton(index)}
                  style={{
                    marginLeft: 5,
                    cursor: "pointer",
                    background: "none",
                    border: "none",
                    color: "red",
                    fontSize: "16px"
                  }}
                >
                  &times;
                </button>
              </div>
            ))}
            <button
              onClick={handleAddButton}
              style={{
                width: "100%",
                cursor: "pointer",
                padding: 5,
                marginTop: 5,
                fontSize: "12px"
              }}
            >
              + Добавить кнопку
            </button>
          </>
        );
      case "inline_button":
        return (
          <>
            <div style={{ fontWeight: "bold", fontSize: "0.8em", marginBottom: 5 }}>
              {nodeLabels.inline_button.toUpperCase()}
            </div>
            <div style={{ fontSize: "0.7em", color: "#666", marginBottom: 8 }}>
              🔗 Подключите ответы к точкам снизу
            </div>
            <textarea
              value={data.label || "Выберите вариант:"}
              onChange={(e) => handleInputChange(e, "label")}
              className="nodrag"
              style={{
                width: "100%",
                minHeight: 40,
                resize: "vertical",
                textAlign: "center",
                border: "1px solid #ccc",
                outline: "none",
                background: "transparent",
                boxSizing: "border-box",
                marginBottom: 10,
                fontSize: "12px",
                padding: 5
              }}
              placeholder="Текст сообщения с кнопками"
            />
            {(data.buttons || []).map((button, index) => (
              <div
                key={index}
                style={{
                  display: "flex",
                  alignItems: "center",
                  marginBottom: 5,
                  position: 'relative'
                }}
              >
                <div style={{
                  width: '12px',
                  height: '12px',
                  borderRadius: '50%',
                  background: '#555',
                  marginRight: '8px',
                  flexShrink: 0
                }} />
                <input
                  type="text"
                  placeholder="Текст кнопки"
                  value={button.label || ""}
                  onChange={(e) => handleButtonChange(e, index)}
                  className="nodrag"
                  style={{
                    flexGrow: 1,
                    border: "1px solid #ccc",
                    padding: 5,
                    boxSizing: "border-box",
                    fontSize: "12px",
                    marginRight: 5
                  }}
                />
                <input
                  type="text"
                  placeholder="callback_data"
                  value={button.callbackData || ""}
                  onChange={(e) => handleButtonCallbackChange(e, index)}
                  className="nodrag"
                  style={{
                    width: "80px",
                    border: "1px solid #ccc",
                    padding: 5,
                    boxSizing: "border-box",
                    fontSize: "10px"
                  }}
                />
                <button
                  onClick={() => handleRemoveButton(index)}
                  style={{
                    marginLeft: 5,
                    cursor: "pointer",
                    background: "none",
                    border: "none",
                    color: "red",
                    fontSize: "16px"
                  }}
                >
                  &times;
                </button>
              </div>
            ))}
            <button
              onClick={handleAddButton}
              style={{
                width: "100%",
                cursor: "pointer",
                padding: 5,
                marginTop: 5,
                fontSize: "12px"
              }}
            >
              + Добавить inline-кнопку
            </button>
          </>
        );
      case "condition":
        return (
          <>
            <div style={{ fontWeight: "bold", fontSize: "0.8em", marginBottom: 5 }}>
              {nodeLabels.condition.toUpperCase()}
            </div>
            <input
              type="text"
              placeholder="условие (e.g., score > 10)"
              value={data.condition || ""}
              onChange={(e) => handleInputChange(e, "condition")}
              className="nodrag"
              style={{
                width: "100%",
                textAlign: "center",
                border: "1px solid #ccc",
                padding: 5,
                boxSizing: "border-box",
                fontSize: "12px"
              }}
            />
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                marginTop: 10,
              }}
            >
              <span style={{ fontSize: "0.8em", color: "#555" }}>Да</span>
              <span style={{ fontSize: "0.8em", color: "#555" }}>Нет</span>
            </div>
          </>
        );
      case "abtest":
        return (
          <>
            <div style={{ fontWeight: "bold", fontSize: "0.8em", marginBottom: 5 }}>
              {nodeLabels.abtest.toUpperCase()}
            </div>
            <div style={{ fontSize: "0.7em", margin: "5px 0" }}>
              <p>Выходы: Вариант A / Вариант B</p>
            </div>
          </>
        );
      case "input":
        return (
          <>
            <div style={{ fontWeight: "bold", fontSize: "0.8em", marginBottom: 5 }}>
              {nodeLabels.input.toUpperCase()}
            </div>
            <input
              type="text"
              placeholder="имя переменной"
              value={data.variableName || ""}
              onChange={(e) => handleInputChange(e, "variableName")}
              className="nodrag"
              style={{
                width: "100%",
                textAlign: "center",
                border: "1px solid #ccc",
                padding: 5,
                boxSizing: "border-box",
                fontSize: "12px"
              }}
            />
          </>
        );
      case "api":
        return (
          <>
            <div style={{ fontWeight: "bold", fontSize: "0.8em", marginBottom: 5 }}>
              {nodeLabels.api.toUpperCase()}
            </div>
            <input
              type="text"
              placeholder="URL"
              value={data.url || ""}
              onChange={(e) => handleInputChange(e, "url")}
              className="nodrag"
              style={{
                width: "100%",
                textAlign: "center",
                border: "1px solid #ccc",
                padding: 5,
                marginBottom: 5,
                boxSizing: "border-box",
                fontSize: "12px"
              }}
            />
            <input
              type="text"
              placeholder="метод (GET, POST)"
              value={data.method || ""}
              onChange={(e) => handleInputChange(e, "method")}
              className="nodrag"
              style={{
                width: "100%",
                textAlign: "center",
                border: "1px solid #ccc",
                padding: 5,
                boxSizing: "border-box",
                fontSize: "12px"
              }}
            />
          </>
        );
      case "random":
        return (
          <>
            <div style={{ fontWeight: "bold", fontSize: "0.8em", marginBottom: 5 }}>
              {nodeLabels.random.toUpperCase()}
            </div>
            <p style={{ fontSize: "0.7em", margin: "5px 0" }}>
              Выходы: Вариант A / Вариант B
            </p>
          </>
        );
      case "handoff":
        return (
          <>
            <div style={{ fontWeight: "bold", fontSize: "0.8em", marginBottom: 5 }}>
              {nodeLabels.handoff.toUpperCase()}
            </div>
            <p style={{ fontSize: "0.7em", margin: "5px 0" }}>
              Перевод на оператора
            </p>
          </>
        );
      case "start":
        return (
          <div style={{ fontWeight: "bold", textAlign: "center", padding: "10px" }}>
            {nodeLabels.start}
          </div>
        );
      case "end":
        return (
          <div style={{ fontWeight: "bold", textAlign: "center", padding: "10px" }}>
            {nodeLabels.end}
          </div>
        );
      default:
        return (
          <div style={{ fontWeight: "bold", color: "red", textAlign: "center", padding: "10px" }}>
            {data.blockType ? `Неизвестный блок: ${data.blockType}` : "Без типа"}
          </div>
        );
    }
  };

  const renderHandles = () => {
    if (!data.blockType) return null;

    switch (data.blockType) {
      case "condition":
        return (
          <>
            <Handle
              type="source"
              position={Position.Left}
              id="yes"
              style={{ top: "30%", background: "#555" }}
            />
            <Handle
              type="source"
              position={Position.Right}
              id="no"
              style={{ top: "70%", background: "#555" }}
            />
          </>
        );
      case "abtest":
      case "random":
        return (
          <>
            <Handle
              type="source"
              position={Position.Left}
              id="a"
              style={{ top: "30%", background: "#555" }}
            />
            <Handle
              type="source"
              position={Position.Right}
              id="b"
              style={{ top: "70%", background: "#555" }}
            />
          </>
        );
      case "button":
        return (data.buttons || []).map((button, index) => (
          <Handle
            key={index}
            type="source"
            position={Position.Bottom}
            id={index.toString()}
            style={{
              left: `${((index + 1) * 100) / ((data.buttons?.length || 0) + 1)}%`,
              transform: 'translateX(-50%)',
              background: "#555",
              bottom: "-6px"
            }}
          />
        ));
      case "inline_button":
        return (data.buttons || []).map((button, index) => (
          <Handle
            key={index}
            type="source"
            position={Position.Bottom}
            id={index.toString()}
            style={{
              left: `${((index + 1) * 100) / ((data.buttons?.length || 0) + 1)}%`,
              transform: 'translateX(-50%)',
              background: "#555",
              bottom: "-6px"
            }}
          />
        ));
      default:
        return (
          <Handle
            type="source"
            position={Position.Bottom}
            id="default"
            style={{ background: "#555", bottom: "-6px" }}
          />
        );
    }
  };

  if (!isMounted) {
    return (
      <div style={{
        padding: 10,
        border: "1px solid #bbb",
        borderRadius: 8,
        background: "#fff",
        minWidth: 150,
        minHeight: 50,
        textAlign: "center",
      }}>
        Загрузка...
      </div>
    );
  }

  return (
    <div
      style={{
        padding: 10,
        border: selected ? "2px solid #0071ff" : "1px solid #bbb",
        borderRadius: 8,
        background: colors[data.blockType] || "#fff",
        minWidth: 150,
        minHeight: 50,
        boxShadow: "0 2px 5px rgba(0,0,0,0.15)",
        textAlign: "center",
        cursor: "grab",
        fontSize: "14px",
        position: "relative",
      }}
      onContextMenu={handleContextMenu}
    >
      <Handle type="target" position={Position.Top} style={{ background: "#555" }} />
      {renderContent()}
      {renderHandles()}

      <ContextMenu
        position={contextMenu}
        onDelete={handleDelete}
        onClose={handleCloseMenu}
      />
    </div>
  );
};