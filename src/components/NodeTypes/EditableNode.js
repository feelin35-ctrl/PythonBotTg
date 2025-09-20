import React, { useState, useEffect } from 'react';
import { Handle, Position } from 'reactflow';
import { colors, nodeLabels } from '../../styles';
import { ContextMenu } from './ContextMenu';
import TextareaWithEmoji from '../TextareaWithEmoji';
import InputWithEmoji from '../InputWithEmoji';
import styled from 'styled-components';

// Стили для адаптивного дизайна узлов
const NodeContainer = styled.div`
  background: ${props => props.color || '#ffffff'};
  border: 2px solid #2196f3;
  border-radius: 8px;
  padding: 10px;
  width: 240px; /* Увеличена ширина на 20% (с 200px до 240px) */
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  font-size: 14px;
  position: relative;
  
  &:hover {
    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
    transform: translateY(-2px);
  }
  
  @media (max-width: 768px) {
    width: 216px; /* 180px + 20% */
    padding: 8px;
    font-size: 12px;
  }
  
  @media (max-width: 480px) {
    width: 192px; /* 160px + 20% */
    padding: 6px;
    font-size: 11px;
  }
`;

const NodeHeader = styled.div`
  font-weight: bold;
  margin-bottom: 8px;
  color: #0d47a1;
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
  background: #2196f3;
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
      
      // Преобразуем поля задержки
      if (['hours', 'minutes', 'seconds'].includes(field)) {
        value = parseInt(value, 10);
        if (isNaN(value) || value < 0) value = 0;
        
        // Ограничиваем диапазон для минут и секунд
        if ((field === 'minutes' || field === 'seconds') && value > 59) value = 59;
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

    // Добавляем отладочный вывод
    console.log('Rendering node with blockType:', data.blockType);

    switch (data.blockType) {
      case "message":
      case "command":
      case "question":
        return (
          <>
            <NodeHeader>
              <span>{nodeLabels[data.blockType]?.toUpperCase() || data.blockType.toUpperCase()}</span>
              <NodeType>{data.blockType}</NodeType>
            </NodeHeader>
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
            <NodeHeader>
              <span>{nodeLabels.image.toUpperCase()}</span>
              <NodeType>image</NodeType>
            </NodeHeader>
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
            <NodeHeader>
              <span>{nodeLabels.gallery.toUpperCase()}</span>
              <NodeType>gallery</NodeType>
            </NodeHeader>
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
      case "inline_button":
        return (
          <>
            <NodeHeader>
              <span>{nodeLabels[data.blockType].toUpperCase()}</span>
              <NodeType>{data.blockType}</NodeType>
            </NodeHeader>
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
            {/* Контейнеры для кнопок с точками выхода */}
            <div style={{ position: "relative", width: "100%" }}>
              {(data.buttons || []).map((button, index) => (
                <div
                  key={index}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    marginBottom: 5,
                    position: 'relative',
                    width: "100%"
                  }}
                >
                  <InputWithEmoji
                    value={button.label || ""}
                    onChange={(e) => handleButtonChange(e, index)}
                    className="nodrag"
                    style={{
                      flexGrow: 1,
                      border: "1px solid #ccc",
                      padding: "5px",
                      boxSizing: "border-box",
                      fontSize: "12px",
                      minWidth: 0,
                      maxWidth: "calc(100% - 30px)"
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
                      fontSize: "16px",
                      flexShrink: 0
                    }}
                  >
                    &times;
                  </button>
                  {/* Точка выхода для каждой кнопки */}
                  <Handle
                    type="source"
                    position={Position.Right}
                    id={index.toString()}
                    style={{
                      top: "50%",
                      transform: "translateY(-50%)",
                      background: "#555",
                      width: '10px',
                      height: '10px',
                      right: '-5px'
                    }}
                  />
                </div>
              ))}
            </div>
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
      case "condition":
        return (
          <>
            <NodeHeader>
              <span>{nodeLabels.condition.toUpperCase()}</span>
              <NodeType>condition</NodeType>
            </NodeHeader>
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
            <NodeHeader>
              <span>{nodeLabels.abtest.toUpperCase()}</span>
              <NodeType>abtest</NodeType>
            </NodeHeader>
            <div style={{ fontSize: "0.7em", margin: "5px 0" }}>
              <p>Выходы: Вариант A / Вариант B</p>
            </div>
          </>
        );
      case "input":
        return (
          <>
            <NodeHeader>
              <span>{nodeLabels.input.toUpperCase()}</span>
              <NodeType>input</NodeType>
            </NodeHeader>
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
            <NodeHeader>
              <span>{nodeLabels.api.toUpperCase()}</span>
              <NodeType>api</NodeType>
            </NodeHeader>
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
            <NodeHeader>
              <span>{nodeLabels.random.toUpperCase()}</span>
              <NodeType>random</NodeType>
            </NodeHeader>
            <p style={{ fontSize: "0.7em", margin: "5px 0" }}>
              Выходы: Вариант A / Вариант B
            </p>
          </>
        );
      case "handoff":
        return (
          <>
            <NodeHeader>
              <span>{nodeLabels.handoff.toUpperCase()}</span>
              <NodeType>handoff</NodeType>
            </NodeHeader>
            <p style={{ fontSize: "0.7em", margin: "5px 0" }}>
              Перевод на оператора
            </p>
          </>
        );
      case "menu":
        return (
          <>
            <NodeHeader>
              <span>{nodeLabels.menu.toUpperCase()}</span>
              <NodeType>menu</NodeType>
            </NodeHeader>
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
            <NodeHeader>
              <span>{nodeLabels.file.toUpperCase()}</span>
              <NodeType>file</NodeType>
            </NodeHeader>
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
                      fontSize: "14px"
                    }}
                  >
                    &times;
                  </button>
                </div>
                <div style={{
                  display: "flex",
                  alignItems: "center"
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
                      marginLeft: 4
                    }}
                  />
                </div>
                <div style={{
                  display: "flex",
                  alignItems: "center",
                  marginTop: 4
                }}>
                  <span style={{
                    fontSize: "10px",
                    color: "#666",
                    minWidth: "60px",
                    textAlign: "left"
                  }}>
                    Файл:
                  </span>
                  <input
                    type="file"
                    onChange={(e) => handleFileSelect(e, index)}
                    className="nodrag"
                    style={{
                      flexGrow: 1,
                      fontSize: "11px",
                      marginLeft: 4
                    }}
                  />
                </div>
              </div>
            ))}
            <button
              onClick={handleAddFile}
              style={{
                width: "100%",
                cursor: "pointer",
                padding: 5,
                marginTop: 5,
                fontSize: "11px"
              }}
            >
              + Добавить файл
            </button>
          </>
        );
      case "nlp_response":
        return (
          <>
            <NodeHeader>
              <span>{nodeLabels.nlp_response.toUpperCase()}</span>
              <NodeType>nlp_response</NodeType>
            </NodeHeader>
            <TextareaWithEmoji
              value={data.prompt || ""}
              onChange={(e) => handleInputChange(e, "prompt")}
              className="nodrag"
              style={{
                width: "100%",
                minHeight: 60,
                resize: "vertical",
                border: "1px solid #ccc",
                padding: 5,
                boxSizing: "border-box",
                fontSize: "11px",
                marginBottom: 8
              }}
              placeholder="Введите подсказку для NLP-модели"
            />
            <div style={{
              fontSize: "10px",
              color: "#666",
              padding: 4,
              backgroundColor: "#f0f8ff",
              borderRadius: 3,
              border: "1px solid #cce7ff"
            }}>
              ℹ️ NLP-модель будет генерировать ответы на основе этой подсказки и контекста разговора
            </div>
          </>
        );
      case "delay":
        return (
          <>
            <NodeHeader>
              <span>{nodeLabels.delay.toUpperCase()}</span>
              <NodeType>delay</NodeType>
            </NodeHeader>
            <div style={{ 
              display: "grid", 
              gridTemplateColumns: "repeat(3, 1fr)", 
              gap: "5px",
              marginTop: "8px"
            }}>
              <div>
                <label style={{ 
                  display: "block", 
                  fontSize: "10px", 
                  marginBottom: "2px",
                  color: "#666"
                }}>
                  Часы:
                </label>
                <input
                  type="number"
                  min="0"
                  value={data.hours || 0}
                  onChange={(e) => handleInputChange(e, "hours")}
                  className="nodrag"
                  style={{
                    width: "100%",
                    border: "1px solid #ccc",
                    padding: "3px",
                    fontSize: "11px",
                    textAlign: "center"
                  }}
                />
              </div>
              <div>
                <label style={{ 
                  display: "block", 
                  fontSize: "10px", 
                  marginBottom: "2px",
                  color: "#666"
                }}>
                  Минуты:
                </label>
                <input
                  type="number"
                  min="0"
                  max="59"
                  value={data.minutes || 0}
                  onChange={(e) => handleInputChange(e, "minutes")}
                  className="nodrag"
                  style={{
                    width: "100%",
                    border: "1px solid #ccc",
                    padding: "3px",
                    fontSize: "11px",
                    textAlign: "center"
                  }}
                />
              </div>
              <div>
                <label style={{ 
                  display: "block", 
                  fontSize: "10px", 
                  marginBottom: "2px",
                  color: "#666"
                }}>
                  Секунды:
                </label>
                <input
                  type="number"
                  min="0"
                  max="59"
                  value={data.seconds || 0}
                  onChange={(e) => handleInputChange(e, "seconds")}
                  className="nodrag"
                  style={{
                    width: "100%",
                    border: "1px solid #ccc",
                    padding: "3px",
                    fontSize: "11px",
                    textAlign: "center"
                  }}
                />
              </div>
            </div>
            <div style={{
              fontSize: "10px",
              color: "#666",
              marginTop: "8px",
              textAlign: "center"
            }}>
              Общая задержка: {(data.hours || 0) * 3600 + (data.minutes || 0) * 60 + (data.seconds || 0)} сек
            </div>
          </>
        );
      case "start":
      case "end":
      default:
        return (
          <NodeHeader>
            <span>{nodeLabels[data.blockType] || "Неизвестный блок"}</span>
            <NodeType>{data.blockType}</NodeType>
          </NodeHeader>
        );
    }
  };

  const renderHandles = () => {
    switch (data.blockType) {
      case "condition":
        return (
          <>
            <Handle
              type="source"
              position={Position.Left}
              id="yes"
              style={{ top: "50%", background: "#555" }}
            />
            <Handle
              type="source"
              position={Position.Right}
              id="no"
              style={{ top: "50%", background: "#555" }}
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
              style={{ top: "50%", background: "#555" }}
            />
            <Handle
              type="source"
              position={Position.Right}
              id="b"
              style={{ top: "50%", background: "#555" }}
            />
          </>
        );
      case "button":
      case "inline_button":
        // Точки выхода для кнопок создаются в контейнерах кнопок
        return null;
      default:
        return null;
    }
  };

  // Добавляем основную точку выхода для всех узлов
  const renderMainHandle = () => {
    // Для узлов с кнопками также добавляем основную точку выхода 
    // для возможности подключения к следующему блоку
    if (data.blockType === "button" || data.blockType === "inline_button") {
      return (
        <Handle
          type="source"
          position={Position.Bottom}
          id="main"
          style={{ 
            background: "#555",
            width: '12px',
            height: '12px',
            right: '50%',
            transform: 'translateX(50%)'
          }}
        />
      );
    }
    
    return (
      <Handle
        type="source"
        position={Position.Bottom}
        id="main"
        style={{ 
          background: "#555",
          width: '12px',
          height: '12px',
          right: '50%',
          transform: 'translateX(50%)'
        }}
      />
    );
  };

  return (
    <>
      <NodeContainer 
        color={colors[data.blockType] || '#ffffff'}
        onContextMenu={handleContextMenu}
      >
        <Handle type="target" position={Position.Top} style={{ background: "#555" }} />
        {renderContent()}
        {renderHandles()}
        {renderMainHandle()}
      </NodeContainer>
      
      {contextMenu && (
        <ContextMenu
          position={contextMenu}
          onDelete={handleDelete}
          onClose={handleCloseMenu}
        />
      )}
    </>
  );
};