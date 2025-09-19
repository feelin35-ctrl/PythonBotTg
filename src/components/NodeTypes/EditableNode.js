import React, { useState, useEffect } from 'react';
import { Handle, Position } from 'reactflow';
import { colors, nodeLabels } from '../../styles';
import { ContextMenu } from './ContextMenu';
import TextareaWithEmoji from '../TextareaWithEmoji';
import InputWithEmoji from '../InputWithEmoji';

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
      let value = e.target.value;
      
      // Преобразуем числовые поля
      if (field === 'buttonsPerRow') {
        value = parseInt(value, 10);
        // Ограничиваем диапазон 1-8
        if (isNaN(value) || value < 1) value = 1;
        if (value > 8) value = 8;
      }
      
      console.log(`🔧 Изменение ${field}:`, value, 'для узла:', id);
      data.onChange(id, { [field]: value });
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

  const handleMenuItemChange = (e, index, field) => {
    if (data.onChange) {
      const newMenuItems = [...(data.menuItems || [])];
      newMenuItems[index][field] = e.target.value;
      data.onChange(id, { menuItems: newMenuItems });
    }
  };

  const handleAddMenuItem = () => {
    if (data.onChange) {
      data.onChange(id, {
        menuItems: [...(data.menuItems || []), { command: "", description: "" }],
      });
    }
  };

  const handleRemoveMenuItem = (index) => {
    if (data.onChange) {
      const newMenuItems = (data.menuItems || []).filter((_, i) => i !== index);
      data.onChange(id, { menuItems: newMenuItems });
    }
  };

  const handleKeyboardToggle = () => {
    if (data.onChange) {
      data.onChange(id, { hideKeyboard: !data.hideKeyboard });
    }
  };

  const handleFileChange = (e, index, field) => {
    if (data.onChange) {
      const newFiles = [...(data.files || [])];
      newFiles[index][field] = e.target.value;
      data.onChange(id, { files: newFiles });
    }
  };

  const handleFileSelect = (e, index) => {
    const file = e.target.files[0];
    if (file && data.onChange) {
      const newFiles = [...(data.files || [])];
      newFiles[index] = {
        name: file.name,
        path: file.path || file.webkitRelativePath || `Выбран: ${file.name}`
      };
      data.onChange(id, { files: newFiles });
    }
  };

  const handleAddFile = () => {
    if (data.onChange) {
      data.onChange(id, {
        files: [...(data.files || []), { name: "", path: "" }],
      });
    }
  };

  const handleRemoveFile = (index) => {
    if (data.onChange) {
      const newFiles = (data.files || []).filter((_, i) => i !== index);
      data.onChange(id, { files: newFiles });
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
            <TextareaWithEmoji
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
              🔗 Подключите ответы к точкам справа
            </div>
            <TextareaWithEmoji
              value={data.label || ""}
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
              placeholder="Текст сообщения с кнопками (необязательно)"
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
                <InputWithEmoji
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
                  placeholder="Текст кнопки"
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
            
            {/* Настройка расположения кнопок */}
            <div style={{
              marginTop: 10,
              marginBottom: 8,
              fontSize: "11px",
              color: "#666"
            }}>
              <div style={{ marginBottom: 4, fontWeight: "bold" }}>Расположение:</div>
              <div style={{ display: "flex", gap: 10 }}>
                <label style={{ display: "flex", alignItems: "center", cursor: "pointer" }}>
                  <input
                    type="radio"
                    name={`buttonLayout-${id}`}
                    value="column"
                    checked={(data.buttonLayout || 'column') === 'column'}
                    onChange={(e) => handleInputChange(e, 'buttonLayout')}
                    className="nodrag"
                    style={{ marginRight: 4 }}
                  />
                  📋 В столбик
                </label>
                <label style={{ display: "flex", alignItems: "center", cursor: "pointer" }}>
                  <input
                    type="radio"
                    name={`buttonLayout-${id}`}
                    value="row"
                    checked={data.buttonLayout === 'row'}
                    onChange={(e) => handleInputChange(e, 'buttonLayout')}
                    className="nodrag"
                    style={{ marginRight: 4 }}
                  />
                  ↔️ В ряд
                </label>
              </div>
              {data.buttonLayout === 'row' && (
                <>
                  <div style={{
                    fontSize: "10px",
                    color: "#888",
                    marginTop: 4,
                    fontStyle: "italic"
                  }}>
                    ℹ️ Максимум 8 кнопок в ряду, всего 100 кнопок
                  </div>
                  <div style={{
                    marginTop: 6,
                    display: "flex",
                    alignItems: "center",
                    gap: 8
                  }}>
                    <label style={{
                      fontSize: "10px",
                      color: "#666",
                      fontWeight: "bold"
                    }}>
                      Кнопок в ряду:
                    </label>
                    <input
                      type="number"
                      min="1"
                      max="8"
                      value={data.buttonsPerRow || 8}
                      onChange={(e) => handleInputChange(e, 'buttonsPerRow')}
                      className="nodrag"
                      style={{
                        width: "40px",
                        border: "1px solid #ccc",
                        padding: "2px 4px",
                        fontSize: "10px",
                        textAlign: "center"
                      }}
                    />
                  </div>
                </>
              )}
            </div>
            
            {/* Переключатель скрытия клавиатуры */}
            <div style={{
              display: "flex",
              alignItems: "center",
              marginTop: 8,
              fontSize: "11px",
              color: "#666"
            }}>
              <input
                type="checkbox"
                id={`hideKeyboard-${id}`}
                checked={data.hideKeyboard || false}
                onChange={handleKeyboardToggle}
                className="nodrag"
                style={{
                  marginRight: 5,
                  cursor: "pointer"
                }}
              />
              <label
                htmlFor={`hideKeyboard-${id}`}
                className="nodrag"
                style={{
                  cursor: "pointer",
                  userSelect: "none"
                }}
              >
                🙈 Скрыть клавиатуру
              </label>
            </div>
          </>
        );
      case "inline_button":
        return (
          <>
            <div style={{ fontWeight: "bold", fontSize: "0.8em", marginBottom: 5 }}>
              {nodeLabels.inline_button.toUpperCase()}
            </div>
            <div style={{ fontSize: "0.7em", color: "#666", marginBottom: 8 }}>
              🔗 Подключите ответы к точкам справа
            </div>
            <TextareaWithEmoji
              value={data.label || ""}
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
                <InputWithEmoji
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
            
            {/* Настройка расположения кнопок */}
            <div style={{
              marginTop: 10,
              marginBottom: 8,
              fontSize: "11px",
              color: "#666"
            }}>
              <div style={{ marginBottom: 4, fontWeight: "bold" }}>Расположение:</div>
              <div style={{ display: "flex", gap: 10 }}>
                <label style={{ display: "flex", alignItems: "center", cursor: "pointer" }}>
                  <input
                    type="radio"
                    name={`inlineButtonLayout-${id}`}
                    value="column"
                    checked={(data.buttonLayout || 'column') === 'column'}
                    onChange={(e) => handleInputChange(e, 'buttonLayout')}
                    className="nodrag"
                    style={{ marginRight: 4 }}
                  />
                  📋 В столбик
                </label>
                <label style={{ display: "flex", alignItems: "center", cursor: "pointer" }}>
                  <input
                    type="radio"
                    name={`inlineButtonLayout-${id}`}
                    value="row"
                    checked={data.buttonLayout === 'row'}
                    onChange={(e) => handleInputChange(e, 'buttonLayout')}
                    className="nodrag"
                    style={{ marginRight: 4 }}
                  />
                  ↔️ В ряд
                </label>
              </div>
              {data.buttonLayout === 'row' && (
                <>
                  <div style={{
                    fontSize: "10px",
                    color: "#888",
                    marginTop: 4,
                    fontStyle: "italic"
                  }}>
                    ℹ️ Максимум 8 кнопок в ряду, всего 100 кнопок
                  </div>
                  <div style={{
                    marginTop: 6,
                    display: "flex",
                    alignItems: "center",
                    gap: 8
                  }}>
                    <label style={{
                      fontSize: "10px",
                      color: "#666",
                      fontWeight: "bold"
                    }}>
                      Кнопок в ряду:
                    </label>
                    <input
                      type="number"
                      min="1"
                      max="8"
                      value={data.buttonsPerRow || 8}
                      onChange={(e) => handleInputChange(e, 'buttonsPerRow')}
                      className="nodrag"
                      style={{
                        width: "40px",
                        border: "1px solid #ccc",
                        padding: "2px 4px",
                        fontSize: "10px",
                        textAlign: "center"
                      }}
                    />
                  </div>
                </>
              )}
            </div>
            
            {/* Переключатель скрытия клавиатуры */}
            <div style={{
              display: "flex",
              alignItems: "center",
              marginTop: 8,
              fontSize: "11px",
              color: "#666"
            }}>
              <input
                type="checkbox"
                id={`hideKeyboard-${id}`}
                checked={data.hideKeyboard || false}
                onChange={handleKeyboardToggle}
                className="nodrag"
                style={{
                  marginRight: 5,
                  cursor: "pointer"
                }}
              />
              <label
                htmlFor={`hideKeyboard-${id}`}
                className="nodrag"
                style={{
                  cursor: "pointer",
                  userSelect: "none"
                }}
              >
                🙈 Скрыть клавиатуру
              </label>
            </div>
          </>
        );
      case "condition":
        return (
          <>
            <div style={{ fontWeight: "bold", fontSize: "0.8em", marginBottom: 5 }}>
              {nodeLabels.condition.toUpperCase()}
            </div>
            <InputWithEmoji
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
      case "menu":
        return (
          <>
            <div style={{ fontWeight: "bold", fontSize: "0.8em", marginBottom: 5 }}>
              {nodeLabels.menu.toUpperCase()}
            </div>
            <TextareaWithEmoji
              value={data.label || "Главное меню"}
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
              placeholder="Заголовок меню"
            />
            <div style={{
              fontSize: "10px",
              color: "#666",
              marginBottom: 8,
              padding: 4,
              backgroundColor: "#f0f8ff",
              borderRadius: 3,
              border: "1px solid #cce7ff"
            }}>
              🔙 Команда "/назад" добавляется автоматически
            </div>
            {(data.menuItems || []).map((item, index) => (
              <div
                key={index}
                style={{
                  display: "flex",
                  alignItems: "center",
                  marginBottom: 5,
                  gap: 5
                }}
              >
                <input
                  type="text"
                  placeholder="/команда"
                  value={item.command || ""}
                  onChange={(e) => handleMenuItemChange(e, index, "command")}
                  className="nodrag"
                  style={{
                    width: "40%",
                    border: "1px solid #ccc",
                    padding: 4,
                    boxSizing: "border-box",
                    fontSize: "11px"
                  }}
                />
                <InputWithEmoji
                  placeholder="Описание"
                  value={item.description || ""}
                  onChange={(e) => handleMenuItemChange(e, index, "description")}
                  className="nodrag"
                  style={{
                    flex: 1,
                    border: "1px solid #ccc",
                    padding: 4,
                    boxSizing: "border-box",
                    fontSize: "11px"
                  }}
                />
                <button
                  onClick={() => handleRemoveMenuItem(index)}
                  style={{
                    cursor: "pointer",
                    background: "none",
                    border: "none",
                    color: "red",
                    fontSize: "14px"
                  }}
                >
                  &times;
                </button>
              </div>
            ))}
            <button
              onClick={handleAddMenuItem}
              style={{
                width: "100%",
                cursor: "pointer",
                padding: 5,
                marginTop: 5,
                fontSize: "11px"
              }}
            >
              + Добавить команду
            </button>
          </>
        );
      case "file":
        return (
          <>
            <div style={{ fontWeight: "bold", fontSize: "0.8em", marginBottom: 5 }}>
              {nodeLabels.file.toUpperCase()}
            </div>
            <TextareaWithEmoji
              value={data.caption || ""}
              onChange={(e) => handleInputChange(e, "caption")}
              className="nodrag"
              style={{
                width: "100%",
                minHeight: 30,
                resize: "vertical",
                border: "1px solid #ccc",
                padding: 5,
                boxSizing: "border-box",
                fontSize: "11px",
                marginBottom: 8
              }}
              placeholder="Подпись к файлам (необязательно)"
            />
            {(data.files || []).map((file, index) => (
              <div
                key={index}
                style={{
                  marginBottom: 8,
                  border: "1px solid #ddd",
                  borderRadius: 4,
                  padding: 6,
                  backgroundColor: "#f9f9f9"
                }}
              >
                <div style={{
                  display: "flex",
                  alignItems: "center",
                  marginBottom: 4
                }}>
                  <span style={{
                    fontSize: "10px",
                    color: "#666",
                    minWidth: "60px",
                    textAlign: "left"
                  }}>
                    Название:
                  </span>
                  <InputWithEmoji
                    placeholder="Название файла"
                    value={file.name || ""}
                    onChange={(e) => handleFileChange(e, index, "name")}
                    className="nodrag"
                    style={{
                      flexGrow: 1,
                      border: "1px solid #ccc",
                      padding: 3,
                      fontSize: "11px",
                      marginLeft: 4
                    }}
                  />
                  <button
                    onClick={() => handleRemoveFile(index)}
                    style={{
                      marginLeft: 4,
                      cursor: "pointer",
                      background: "none",
                      border: "none",
                      color: "red",
                      fontSize: "14px",
                      padding: 0,
                      width: "16px",
                      height: "16px"
                    }}
                  >
                    ×
                  </button>
                </div>
                <div style={{
                  display: "flex",
                  alignItems: "center",
                  marginBottom: 4
                }}>
                  <span style={{
                    fontSize: "10px",
                    color: "#666",
                    minWidth: "60px",
                    textAlign: "left"
                  }}>
                    Путь:
                  </span>
                  <input
                    type="text"
                    placeholder="Путь к файлу"
                    value={file.path || ""}
                    onChange={(e) => handleFileChange(e, index, "path")}
                    className="nodrag"
                    style={{
                      flexGrow: 1,
                      border: "1px solid #ccc",
                      padding: 3,
                      fontSize: "11px",
                      marginLeft: 4,
                      marginRight: 4
                    }}
                  />
                  <input
                    type="file"
                    id={`file-input-${id}-${index}`}
                    style={{ display: "none" }}
                    onChange={(e) => handleFileSelect(e, index)}
                    className="nodrag"
                  />
                  <button
                    onClick={() => document.getElementById(`file-input-${id}-${index}`).click()}
                    style={{
                      cursor: "pointer",
                      border: "1px solid #ccc",
                      borderRadius: 3,
                      backgroundColor: "#f8f8f8",
                      fontSize: "9px",
                      padding: "2px 6px",
                      minWidth: "50px"
                    }}
                    className="nodrag"
                  >
                    📁 Обзор
                  </button>
                </div>
              </div>
            ))}
            <button
              onClick={handleAddFile}
              style={{
                width: "100%",
                cursor: "pointer",
                padding: 6,
                marginTop: 5,
                fontSize: "11px",
                border: "1px solid #ccc",
                borderRadius: 3,
                backgroundColor: "#f0f0f0"
              }}
            >
              📎 Добавить файл
            </button>
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
        return (data.buttons || []).map((button, index) => {
          // Вычисляем позицию каждой кнопки (заголовок + подсказка + textarea + сама кнопка)
          const buttonHeight = 29; // Высота одной кнопки (5px margin + 19px высота input + 5px padding)
          const headerHeight = 45; // Высота заголовка и подсказки
          const textareaHeight = 55; // textarea с маржином
          const topPosition = headerHeight + textareaHeight + (index * buttonHeight) + (buttonHeight / 2);
          
          return (
            <Handle
              key={index}
              type="source"
              position={Position.Right}
              id={index.toString()}
              style={{
                top: `${topPosition}px`,
                background: "#555",
                right: "-6px"
              }}
            />
          );
        });
      case "inline_button":
        return (data.buttons || []).map((button, index) => {
          // Для inline_button учитываем textarea и кнопки
          const buttonHeight = 29; // Высота одной кнопки
          const headerHeight = 45; // Заголовок и подсказка
          const textareaHeight = 55; // textarea с маржином
          const topPosition = headerHeight + textareaHeight + (index * buttonHeight) + (buttonHeight / 2);
          
          return (
            <Handle
              key={index}
              type="source"
              position={Position.Right}
              id={index.toString()}
              style={{
                top: `${topPosition}px`,
                background: "#555",
                right: "-6px"
              }}
            />
          );
        });
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