import React, { useState, useEffect, useCallback, useMemo } from "react";
import { useParams, useNavigate } from "react-router-dom";
import ReactFlow, {
  addEdge,
  Background,
  Controls,
  applyNodeChanges,
  applyEdgeChanges,
  Handle,
  Position,
  useReactFlow,
} from "reactflow";
import "reactflow/dist/style.css";
import axios from "axios";
import { v4 as uuidv4 } from "uuid";

// Node Types
const EditableNode = ({ id, data, selected, onDelete }) => {
  const [showContextMenu, setShowContextMenu] = useState(false);
  const [menuPosition, setMenuPosition] = useState({ x: 0, y: 0 });

  const colors = {
    start: "#a0e6a0",
    message: "#a0c4ff",
    question: "#ffd580",
    end: "#ff9999",
    command: "#c4a0ff",
    image: "#ffebcd",
    gallery: "#c2d4fe",
    button: "#ffcc99",
    condition: "#b3e0ff",
    abtest: "#99ffb3",
    input: "#ffb3d1",
    api: "#ff99cc",
    random: "#d1b3ff",
    handoff: "#ccffcc",
  };

  const nodeLabels = {
    start: "Старт",
    message: "Сообщение",
    question: "Вопрос",
    end: "Конец",
    command: "Команда",
    image: "Изображение",
    gallery: "Галерея",
    button: "Кнопки",
    condition: "Условие",
    abtest: "A/B Тест",
    input: "Ввод данных",
    api: "API Запрос",
    random: "Случайный выбор",
    handoff: "На оператора",
  };

  const handleInputChange = (e, field) => {
    data.onChange(id, { [field]: e.target.value });
  };

  const handleButtonChange = (e, index) => {
    const newButtons = [...(data.buttons || [])];
    newButtons[index].label = e.target.value;
    data.onChange(id, { buttons: newButtons });
  };

  const handleAddButton = () => {
    data.onChange(id, {
      buttons: [...(data.buttons || []), { label: "Новая кнопка" }],
    });
  };

  const handleRemoveButton = (index) => {
    const newButtons = (data.buttons || []).filter((_, i) => i !== index);
    data.onChange(id, { buttons: newButtons });
  };

  const handleImageChange = (e, index) => {
    const newImages = [...(data.images || [])];
    newImages[index] = e.target.value;
    data.onChange(id, { images: newImages });
  };

  const handleAddImage = () => {
    data.onChange(id, { images: [...(data.images || []), ""] });
  };

  const handleRemoveImage = (index) => {
    const newImages = (data.images || []).filter((_, i) => i !== index);
    data.onChange(id, { images: newImages });
  };

  const handleContextMenu = (event) => {
    event.preventDefault();
    setMenuPosition({ x: event.clientX, y: event.clientY });
    setShowContextMenu(true);
  };

  const handleDelete = () => {
    onDelete?.(id);
    setShowContextMenu(false);
  };

  const handleCloseMenu = () => {
    setShowContextMenu(false);
  };

  const renderContent = () => {
    switch (data.blockType) {
      case "message":
      case "command":
      case "question":
        return (
          <>
            <div
              style={{
                fontWeight: "bold",
                fontSize: "0.8em",
                marginBottom: 5,
              }}
            >
              {nodeLabels[data.blockType].toUpperCase()}
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
              placeholder={`${nodeLabels[data.blockType]} текст`}
            />
          </>
        );
      case "image":
        return (
          <>
            <div
              style={{
                fontWeight: "bold",
                fontSize: "0.8em",
                marginBottom: 5,
              }}
            >
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
                style={{ maxWidth: "100%", height: "auto" }}
              />
            )}
          </>
        );
      case "gallery":
        return (
          <>
            <div
              style={{
                fontWeight: "bold",
                fontSize: "0.8em",
                marginBottom: 5,
              }}
            >
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
              }}
            >
              + Добавить изображение
            </button>
          </>
        );
      case "button":
        return (
          <>
            <div
              style={{
                fontWeight: "bold",
                fontSize: "0.8em",
                marginBottom: 5,
              }}
            >
              {nodeLabels.button.toUpperCase()}
            </div>
            {(data.buttons || []).map((button, index) => (
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
                  value={button.label || ""}
                  onChange={(e) => handleButtonChange(e, index)}
                  className="nodrag"
                  style={{
                    flexGrow: 1,
                    border: "1px solid #ccc",
                    padding: 5,
                    boxSizing: "border-box",
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
              }}
            >
              + Добавить кнопку
            </button>
          </>
        );
      case "condition":
        return (
          <>
            <div
              style={{
                fontWeight: "bold",
                fontSize: "0.8em",
                marginBottom: 5,
              }}
            >
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
            <div
              style={{
                fontWeight: "bold",
                fontSize: "0.8em",
                marginBottom: 5,
              }}
            >
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
            <div
              style={{
                fontWeight: "bold",
                fontSize: "0.8em",
                marginBottom: 5,
              }}
            >
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
              }}
            />
          </>
        );
      case "api":
        return (
          <>
            <div
              style={{
                fontWeight: "bold",
                fontSize: "0.8em",
                marginBottom: 5,
              }}
            >
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
              }}
            />
          </>
        );
      case "random":
        return (
          <>
            <div
              style={{
                fontWeight: "bold",
                fontSize: "0.8em",
                marginBottom: 5,
              }}
            >
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
            <div
              style={{
                fontWeight: "bold",
                fontSize: "0.8em",
                marginBottom: 5,
              }}
            >
              {nodeLabels.handoff.toUpperCase()}
            </div>
            <p style={{ fontSize: "0.7em", margin: "5px 0" }}>
              Перевод на оператора
            </p>
          </>
        );
      case "start":
      case "end":
      default:
        return (
          <div style={{ fontWeight: "bold" }}>
            {nodeLabels[data.blockType] || "Неизвестный блок"}
          </div>
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
        return (data.buttons || []).map((button, index) => (
          <Handle
            key={index}
            type="source"
            position={Position.Bottom}
            id={`button-handle-${index}`}
            style={{
              top: `${50 + index * 25}px`,
              background: "#555",
              left: "50%",
            }}
          />
        ));
      default:
        return (
          <Handle type="source" position={Position.Bottom} style={{ background: "#555" }} />
        );
    }
  };

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
      }}
      onContextMenu={handleContextMenu}
    >
      <Handle type="target" position={Position.Top} style={{ background: "#555" }} />
      {renderContent()}
      {renderHandles()}

      {showContextMenu && (
        <>
          <div
            style={{
              position: 'fixed',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              zIndex: 999,
            }}
            onClick={handleCloseMenu}
          />
          <div
            style={{
              position: 'fixed',
              left: menuPosition.x,
              top: menuPosition.y,
              background: 'white',
              border: '1px solid #ccc',
              borderRadius: '4px',
              boxShadow: '0 2px 10px rgba(0,0,0,0.2)',
              zIndex: 1000,
              minWidth: '120px',
            }}
          >
            <div
              style={{
                padding: '10px',
                cursor: 'pointer',
                color: '#dc3545',
                borderBottom: '1px solid #eee',
              }}
              onClick={handleDelete}
            >
              🗑️ Удалить блок
            </div>
            <div
              style={{
                padding: '10px',
                cursor: 'pointer',
                color: '#6c757d',
              }}
              onClick={handleCloseMenu}
            >
              ✕ Отмена
            </div>
          </div>
        </>
      )}
    </div>
  );
};

// Sidebar Component
const Sidebar = () => {
  const onDragStart = (event, nodeType) => {
    event.dataTransfer.setData("application/reactflow", nodeType);
    event.dataTransfer.effectAllowed = "move";
  };

  const nodeLabels = {
    start: "Старт",
    message: "Сообщение",
    question: "Вопрос",
    command: "Команда",
    image: "Изображение",
    gallery: "Галерея",
    button: "Кнопки",
    condition: "Условие",
    abtest: "A/B Тест",
    input: "Ввод данных",
    api: "API Запрос",
    random: "Случайный выбор",
    handoff: "На оператора",
    end: "Конец",
  };

  const nodeColors = {
    start: "#a0e6a0",
    message: "#a0c4ff",
    question: "#ffd580",
    end: "#ff9999",
    command: "#c4a0ff",
    image: "#ffebcd",
    gallery: "#c2d4fe",
    button: "#ffcc99",
    condition: "#b3e0ff",
    abtest: "#99ffb3",
    input: "#ffb3d1",
    api: "#ff99cc",
    random: "#d1b3ff",
    handoff: "#ccffcc",
  };

  return (
    <aside
      style={{
        width: 250,
        borderRight: "1px solid #ccc",
        padding: 15,
        background: "#f0f0f0",
        display: "flex",
        flexDirection: "column",
      }}
    >
      <div style={{ marginBottom: 20 }}>
        <h4>Доступные блоки</h4>
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
              background: nodeColors[type] || "#fff",
              cursor: "grab",
              textAlign: "center",
            }}
          >
            {label}
          </div>
        ))}
      </div>
    </aside>
  );
};

function BotEditor() {
  const { botId } = useParams();
  const navigate = useNavigate();
  const { screenToFlowPosition, getNodes, getEdges } = useReactFlow();
  const [initialNodes, setInitialNodes] = useState([]);
  const [edges, setEdges] = useState([]);
  const [botToken, setBotToken] = useState("");
  const [history, setHistory] = useState([]);
  const [historyIndex, setHistoryIndex] = useState(-1);

  const nodeTypes = useMemo(() => ({
    editable: (props) => <EditableNode {...props} onDelete={deleteNodeById} />
  }), []);

  const onDataChange = useCallback(
    (id, newData) => {
      setInitialNodes((nds) =>
        nds.map((node) =>
          node.id === id ? { ...node, data: { ...node.data, ...newData } } : node
        )
      );
    },
    [setInitialNodes]
  );

  // Функции для удаления блоков
  const deleteSelectedNodes = useCallback(() => {
    const selectedNodes = getNodes().filter(node => node.selected);

    if (selectedNodes.length === 0) {
      alert("Выберите блок(и) для удаления");
      return;
    }

    if (!window.confirm(`Удалить ${selectedNodes.length} блок(ов)?`)) {
      return;
    }

    const selectedNodeIds = selectedNodes.map(node => node.id);

    // Удаляем узлы
    const newNodes = getNodes().filter(node => !selectedNodeIds.includes(node.id));

    // Удаляем связанные edges
    const newEdges = getEdges().filter(edge =>
      !selectedNodeIds.includes(edge.source) && !selectedNodeIds.includes(edge.target)
    );

    setInitialNodes(newNodes);
    setEdges(newEdges);

    console.log(`Удалено блоков: ${selectedNodes.length}`);
  }, [getNodes, getEdges]);

  const deleteAllNodes = useCallback(() => {
    if (getNodes().length === 0) {
      alert("Нет блоков для удаления");
      return;
    }

    if (!window.confirm("Удалить ВСЕ блоки? Это действие нельзя отменить.")) {
      return;
    }

    setInitialNodes([]);
    setEdges([]);
    console.log("Все блоки удалены");
  }, [getNodes]);

  const deleteNodeById = useCallback((nodeId) => {
    const newNodes = getNodes().filter(node => node.id !== nodeId);
    const newEdges = getEdges().filter(edge =>
      edge.source !== nodeId && edge.target !== nodeId
    );

    setInitialNodes(newNodes);
    setEdges(newEdges);
    console.log(`Удален блок: ${nodeId}`);
  }, [getNodes, getEdges]);

  // Функции для истории изменений
  const saveToHistory = useCallback(() => {
    const currentState = {
      nodes: getNodes(),
      edges: getEdges()
    };

    setHistory(prev => [...prev.slice(0, historyIndex + 1), currentState]);
    setHistoryIndex(prev => prev + 1);
  }, [getNodes, getEdges, historyIndex]);

  const undo = useCallback(() => {
    if (historyIndex > 0) {
      const previousState = history[historyIndex - 1];
      setInitialNodes(previousState.nodes);
      setEdges(previousState.edges);
      setHistoryIndex(prev => prev - 1);
    }
  }, [history, historyIndex]);

  const redo = useCallback(() => {
    if (historyIndex < history.length - 1) {
      const nextState = history[historyIndex + 1];
      setInitialNodes(nextState.nodes);
      setEdges(nextState.edges);
      setHistoryIndex(prev => prev + 1);
    }
  }, [history, historyIndex]);

  // Обработчики горячих клавиш
  useEffect(() => {
    const handleKeyPress = (event) => {
      // Delete - удалить выбранные блоки
      if (event.key === 'Delete') {
        event.preventDefault();
        deleteSelectedNodes();
      }

      // Ctrl+D - удалить выбранные блоки
      if (event.ctrlKey && event.key === 'd') {
        event.preventDefault();
        deleteSelectedNodes();
      }

      // Ctrl+Shift+D - удалить все блоки
      if (event.ctrlKey && event.shiftKey && event.key === 'D') {
        event.preventDefault();
        deleteAllNodes();
      }

      // Ctrl+Z - отмена
      if (event.ctrlKey && event.key === 'z') {
        event.preventDefault();
        undo();
      }

      // Ctrl+Y - повтор
      if (event.ctrlKey && event.key === 'y') {
        event.preventDefault();
        redo();
      }
    };

    window.addEventListener('keydown', handleKeyPress);

    return () => {
      window.removeEventListener('keydown', handleKeyPress);
    };
  }, [deleteSelectedNodes, deleteAllNodes, undo, redo]);

  // загрузка сценария и токена
  useEffect(() => {
    // Загрузка сценария
    axios
      .get(`http://127.0.0.1:8001/get_scenario/${botId}/`)
      .then((res) => {
        const loadedNodes = (res.data.nodes || []).map((n) => {
          const blockType = n.data?.blockType || n.type;
          return {
            ...n,
            type: "editable",
            data: {
              ...n.data,
              blockType: blockType,
              onChange: onDataChange,
            },
          };
        });

        const loadedEdges = (res.data.edges || []).map((e) => ({
          ...e,
          animated: true,
          style: { strokeWidth: 2, stroke: "black" },
          markerEnd: { type: "arrowclosed", color: "black" },
        }));

        setInitialNodes(loadedNodes);
        setEdges(loadedEdges);

        // Сохраняем начальное состояние в историю
        setHistory([{ nodes: loadedNodes, edges: loadedEdges }]);
        setHistoryIndex(0);
      })
      .catch((err) => console.error("Ошибка загрузки сценария:", err));

    // Загрузка токена
    axios.get(`http://127.0.0.1:8001/get_token/${botId}/`)
      .then(res => setBotToken(res.data.token || ""))
      .catch(err => console.error("Ошибка загрузки токена:", err));
  }, [botId, onDataChange]);

  // Автоматически сохраняем в историю при изменениях
  useEffect(() => {
    if (initialNodes.length > 0 || edges.length > 0) {
      saveToHistory();
    }
  }, [initialNodes, edges]);

  // сохранение сценария
  const saveScenario = useCallback(() => {
    const cleanNodes = getNodes().map(({ data, ...rest }) => {
      const { onChange, blockType, ...cleanData } = data;
      return {
        ...rest,
        type: blockType,
        data: cleanData,
      };
    });

    const cleanEdges = getEdges().map(({ animated, style, markerEnd, ...rest }) => rest);

    axios
      .post(`http://127.0.0.1:8001/save_scenario/${botId}/`, {
        nodes: cleanNodes,
        edges: cleanEdges,
      })
      .then(() => {
        console.log("Сценарий сохранен");
        alert("Сценарий успешно сохранен!");
      })
      .catch((err) => {
        console.error("Ошибка сохранения:", err);
        alert("Ошибка при сохранении сценария!");
      });
  }, [botId, getNodes, getEdges]);

  const saveToken = useCallback(() => {
    axios
      .post(`http://127.0.0.1:8001/save_token/${botId}/`, { token: botToken })
      .then(() => {
        console.log("Токен сохранен");
        alert("Токен успешно сохранен!");
      })
      .catch((err) => {
        console.error("Ошибка сохранения токена:", err);
        alert("Ошибка при сохранении токена!");
      });
  }, [botId, botToken]);

  const runBot = useCallback(() => {
    if (!botToken) {
      alert("Сначала сохраните токен бота");
      return;
    }
    axios
      .post(`http://127.0.0.1:8001/run_bot/${botId}/`, { token: botToken })
      .then((res) => alert(res.data.message))
      .catch((err) => alert("Ошибка запуска: " + (err.response?.data?.message || err.message)));
  }, [botId, botToken]);

  const onNodesChange = useCallback(
    (changes) => setInitialNodes((nds) => applyNodeChanges(changes, nds)),
    []
  );

  const onEdgesChange = useCallback(
    (changes) => setEdges((eds) => applyEdgeChanges(changes, eds)),
    []
  );

  const onConnect = useCallback(
    (connection) =>
      setEdges((eds) =>
        addEdge(
          {
            ...connection,
            animated: true,
            style: { strokeWidth: 2, stroke: "black" },
            markerEnd: { type: "arrowclosed", color: "black" },
          },
          eds
        )
      ),
    []
  );

  const onDrop = useCallback(
    (event) => {
      event.preventDefault();

      const type = event.dataTransfer.getData("application/reactflow");
      if (!type) return;

      const position = screenToFlowPosition({
        x: event.clientX,
        y: event.clientY,
      });

      const newNode = {
        id: uuidv4(),
        type: "editable",
        position,
        data: {
          label: `${type} блок`,
          blockType: type,
          onChange: onDataChange
        },
      };

      setInitialNodes((nds) => nds.concat(newNode));
    },
    [screenToFlowPosition, onDataChange]
  );

  const onDragOver = useCallback((event) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = "move";
  }, []);

  return (
    <div style={{ display: "flex", height: "100vh" }}>
      <Sidebar />
      <div style={{ flexGrow: 1, position: "relative" }}>
        <ReactFlow
          nodes={initialNodes}
          edges={edges}
          nodeTypes={nodeTypes}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onDrop={onDrop}
          onDragOver={onDragOver}
          fitView
          deleteKeyCode={null} // Отключаем стандартное удаление ReactFlow
        >
          <Background />
          <Controls />
        </ReactFlow>

        {/* Панель управления */}
        <div style={{
          position: "absolute",
          left: 20,
          top: 20,
          display: "flex",
          flexDirection: "column",
          gap: 10,
          background: "white",
          padding: 15,
          borderRadius: 8,
          boxShadow: "0 2px 10px rgba(0,0,0,0.1)",
          minWidth: 250,
          zIndex: 1000
        }}>
          <h4 style={{ margin: "0 0 10px 0", fontSize: "16px" }}>Управление ботом</h4>

          {/* Управление токеном */}
          <div style={{ marginBottom: "10px", paddingBottom: "10px", borderBottom: "1px solid #eee" }}>
            <input
              type="password"
              value={botToken}
              onChange={(e) => setBotToken(e.target.value)}
              placeholder="Токен бота"
              style={{
                width: "100%",
                padding: "8px",
                border: "1px solid #ccc",
                borderRadius: "4px",
                marginBottom: "5px"
              }}
            />
            <button onClick={saveToken} style={{
              width: "100%",
              padding: "8px",
              background: "#28a745",
              color: "white",
              border: "none",
              borderRadius: "4px",
              cursor: "pointer",
              marginBottom: "5px"
            }}>
              💾 Сохранить токен
            </button>
          </div>

          {/* Управление сценарием */}
          <div style={{ marginBottom: "10px", paddingBottom: "10px", borderBottom: "1px solid #eee" }}>
            <button onClick={saveScenario} style={{
              width: "100%",
              padding: "8px",
              background: "#007bff",
              color: "white",
              border: "none",
              borderRadius: "4px",
              cursor: "pointer",
              marginBottom: "5px"
            }}>
              💾 Сохранить сценарий
            </button>

            <button onClick={deleteSelectedNodes} style={{
              width: "100%",
              padding: "8px",
              background: "#dc3545",
              color: "white",
              border: "none",
              borderRadius: "4px",
              cursor: "pointer",
              marginBottom: "5px"
            }}>
              🗑️ Удалить выбранные (Del)
            </button>

            <button onClick={deleteAllNodes} style={{
              width: "100%",
              padding: "8px",
              background: "#ff6b6b",
              color: "white",
              border: "none",
              borderRadius: "4px",
              cursor: "pointer",
              marginBottom: "5px"
            }}>
              🗑️ Удалить ВСЕ (Ctrl+Shift+D)
            </button>
          </div>

          {/* Управление историей */}
          <div style={{
            marginBottom: "10px",
            paddingBottom: "10px",
            borderBottom: "1px solid #eee",
            display: "flex",
            gap: "5px"
          }}>
            <button onClick={undo} disabled={historyIndex <= 0} style={{
              flex: 1,
              padding: "8px",
              background: "#6c757d",
              color: "white",
              border: "none",
              borderRadius: "4px",
              cursor: "pointer",
              opacity: historyIndex <= 0 ? 0.5 : 1
            }}>
              ↩️ Отмена (Ctrl+Z)
            </button>

            <button onClick={redo} disabled={historyIndex >= history.length - 1} style={{
              flex: 1,
              padding: "8px",
              background: "#6c757d",
              color: "white",
              border: "none",
              borderRadius: "4px",
              cursor: "pointer",
              opacity: historyIndex >= history.length - 1 ? 0.5 : 1
            }}>
              ↪️ Повтор (Ctrl+Y)
            </button>
          </div>

          {/* Запуск бота */}
          <div>
            <button onClick={runBot} style={{
              width: "100%",
              padding: "8px",
              background: "#17a2b8",
              color: "white",
              border: "none",
              borderRadius: "4px",
              cursor: "pointer",
              marginBottom: "5px"
            }}>
              ▶️ Запустить бота
            </button>

            <button onClick={() => navigate("/")} style={{
              width: "100%",
              padding: "8px",
              background: "#6c757d",
              color: "white",
              border: "none",
              borderRadius: "4px",
              cursor: "pointer"
            }}>
              ⬅ Назад к списку
            </button>
          </div>

          {/* Статистика */}
          <div style={{
            marginTop: "10px",
            padding: "10px",
            background: "#f8f9fa",
            borderRadius: "4px",
            fontSize: "12px"
          }}>
            <div>Блоков: {getNodes().length}</div>
            <div>Связей: {getEdges().length}</div>
            <div>Выбрано: {getNodes().filter(n => n.selected).length}</div>
            <div>История: {historyIndex + 1}/{history.length}</div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default BotEditor;