import { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { applyNodeChanges, applyEdgeChanges, addEdge } from 'reactflow';
import axios from 'axios';
import { useUndoRedo } from '../../hooks/useUndoRedo';
import { useKeyboardShortcuts } from '../../hooks/useKeyboardShortcuts';
import { v4 as uuidv4 } from 'uuid';

export const useBotEditor = () => {
  const { botId } = useParams();
  const navigate = useNavigate();
  const [reactFlowInstance, setReactFlowInstance] = useState(null);
  const [initialNodes, setInitialNodes] = useState([]);
  const [edges, setEdges] = useState([]);
  const [botToken, setBotToken] = useState('');
  const [botName, setBotName] = useState(''); // Добавляем состояние для имени бота
  const [isBotRunning, setIsBotRunning] = useState(false);
  const [loadingStatus, setLoadingStatus] = useState(false);

  const { saveToHistory, undo, redo } = useUndoRedo({
    nodes: initialNodes,
    edges: edges
  });

  // Функция для проверки статуса бота
  const checkBotStatus = useCallback(async () => {
    try {
      const response = await axios.get(`http://127.0.0.1:8001/bot_running_status/${botId}/`);
      setIsBotRunning(response.data.is_running);
    } catch (error) {
      console.error('Ошибка проверки статуса бота:', error);
      setIsBotRunning(false);
    }
  }, [botId]);

  // Проверяем статус бота при загрузке и периодически
  useEffect(() => {
    checkBotStatus();

    // Периодическая проверка статуса каждые 5 секунд
    const interval = setInterval(checkBotStatus, 5000);

    return () => clearInterval(interval);
  }, [checkBotStatus]);

  // Добавим отладочный эффект
  useEffect(() => {
    console.log('Nodes updated:', initialNodes);
    console.log('Edges updated:', edges);
  }, [initialNodes, edges]);

  const onInit = useCallback((instance) => {
    console.log('ReactFlow instance initialized');
    setReactFlowInstance(instance);
  }, []);

  const onDataChange = useCallback((id, newData) => {
    setInitialNodes(nds => nds.map(node =>
      node.id === id ? { ...node, data: { ...node.data, ...newData } } : node
    ));
  }, []);

  const onDrop = useCallback((event) => {
    event.preventDefault();

    const type = event.dataTransfer.getData('application/reactflow');
    if (!type || !reactFlowInstance) {
      console.log('Cannot drop: no type or reactFlowInstance');
      return;
    }

    const position = reactFlowInstance.screenToFlowPosition({
      x: event.clientX,
      y: event.clientY,
    });

    console.log('Dropping node at position:', position, 'type:', type);

    const newNode = {
      id: uuidv4(),
      type: 'editable',
      position,
      data: {
        label: type === 'message' ? 'Новое сообщение' : '',
        blockType: type,
        onChange: onDataChange
      }
    };

    setInitialNodes(nds => [...nds, newNode]);

    // Автоматически подстраиваем вид после добавления узла
    setTimeout(() => {
      if (reactFlowInstance) {
        reactFlowInstance.fitView();
      }
    }, 100);
  }, [reactFlowInstance, onDataChange]);

  const onDragOver = useCallback((event) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  }, []);

  const deleteSelectedNodes = useCallback(() => {
    const selectedNodes = initialNodes.filter(node => node.selected);
    const selectedEdges = edges.filter(edge => edge.selected);
    
    if (selectedNodes.length === 0 && selectedEdges.length === 0) {
      // На мобильных устройствах показываем уведомление через alert
      if (window.innerWidth <= 768) {
        alert("Выберите элемент(ы) для удаления");
      }
      return;
    }

    let confirmMessage = "";
    if (selectedNodes.length > 0 && selectedEdges.length > 0) {
      confirmMessage = `Удалить ${selectedNodes.length} блок(ов) и ${selectedEdges.length} связей?`;
    } else if (selectedNodes.length > 0) {
      confirmMessage = `Удалить ${selectedNodes.length} блок(ов)?`;
    } else {
      confirmMessage = `Удалить ${selectedEdges.length} связей?`;
    }

    if (!window.confirm(confirmMessage)) {
      return;
    }

    const selectedNodeIds = selectedNodes.map(node => node.id);
    const selectedEdgeIds = selectedEdges.map(edge => edge.id);
    
    // Удаляем узлы
    const newNodes = initialNodes.filter(node => !selectedNodeIds.includes(node.id));
    
    // Удаляем связи (выбранные + связанные с удаленными узлами)
    const newEdges = edges.filter(edge => 
      !selectedEdgeIds.includes(edge.id) && 
      !selectedNodeIds.includes(edge.source) && 
      !selectedNodeIds.includes(edge.target)
    );

    setInitialNodes(newNodes);
    setEdges(newEdges);
    
    console.log(`Удалено: ${selectedNodes.length} блоков, ${selectedEdges.length} связей`);
  }, [initialNodes, edges]);

  const deleteAllNodes = useCallback(() => {
    if (initialNodes.length === 0) return;
    if (!window.confirm("Удалить ВСЕ блоки?")) return;

    setInitialNodes([]);
    setEdges([]);
  }, [initialNodes.length]);

  const deleteNodeById = useCallback((nodeId) => {
    setInitialNodes(nodes => nodes.filter(node => node.id !== nodeId));
    setEdges(edges => edges.filter(edge =>
      edge.source !== nodeId && edge.target !== nodeId
    ));
  }, []);

  useKeyboardShortcuts({
    onDeleteSelected: deleteSelectedNodes,
    onDeleteAll: deleteAllNodes
  });

  useEffect(() => {
    axios.get(`http://127.0.0.1:8001/get_scenario/${botId}/`)
      .then((res) => {
        console.log('Loaded scenario data:', res.data);
        const loadedNodes = (res.data.nodes || []).map(n => ({
          ...n,
          type: "editable",
          data: {
            ...n.data,
            blockType: n.data?.blockType || n.type,
            onChange: onDataChange
          },
        }));

        const loadedEdges = (res.data.edges || []).map(e => ({
          ...e,
          animated: true,
          style: { 
            strokeWidth: e.selected ? 3 : 2, 
            stroke: e.selected ? "#1976d2" : "black" 
          },
          markerEnd: { 
            type: "arrowclosed", 
            color: e.selected ? "#1976d2" : "black" 
          },
        }));

        console.log('Processed nodes:', loadedNodes);
        console.log('Processed edges:', loadedEdges);

        setInitialNodes(loadedNodes);
        setEdges(loadedEdges);
      })
      .catch(error => {
        console.error('Error loading scenario:', error);
      });

    axios.get(`http://127.0.0.1:8001/get_token/${botId}/`)
      .then(res => {
        console.log('Loaded bot token:', res.data.token);
        setBotToken(res.data.token || '');
      })
      .catch(console.error);
      
    // Загружаем имя бота
    axios.get(`http://127.0.0.1:8001/get_bot_name/${botId}/`)
      .then(res => {
        if (res.data.status === 'success') {
          console.log('Loaded bot name:', res.data.name);
          setBotName(res.data.name || '');
        }
      })
      .catch(error => {
        console.error('Error loading bot name:', error);
        // Если не удалось получить имя, оставляем пустым
        setBotName('');
      });
  }, [botId, onDataChange]);

  const saveScenario = useCallback(() => {
    const cleanNodes = initialNodes.map(({ data, ...rest }) => {
      const { onChange, ...cleanData } = data;
      return { ...rest, type: data.blockType, data: cleanData };
    });

    const cleanEdges = edges.map(({ animated, style, markerEnd, ...rest }) => rest);

    axios.post(`http://127.0.0.1:8001/save_scenario/${botId}/`, {
      nodes: cleanNodes,
      edges: cleanEdges,
    })
    .then(() => {
      // На мобильных устройствах показываем уведомление через alert
      if (window.innerWidth <= 768) {
        alert("Сценарий сохранен!");
      } else {
        console.log("Сценарий сохранен");
      }
    })
    .catch(err => {
      // На мобильных устройствах показываем уведомление через alert
      if (window.innerWidth <= 768) {
        alert("Ошибка сохранения: " + err.message);
      } else {
        console.error("Ошибка сохранения:", err);
      }
    });
  }, [botId, initialNodes, edges]);

  const saveToken = useCallback(() => {
    axios.post(`http://127.0.0.1:8001/save_token/${botId}/`, { token: botToken })
      .then(() => {
        // На мобильных устройствах показываем уведомление через alert
        if (window.innerWidth <= 768) {
          alert("Токен сохранен!");
        } else {
          console.log("Токен сохранен");
        }
      })
      .catch(err => {
        // На мобильных устройствах показываем уведомление через alert
        if (window.innerWidth <= 768) {
          alert("Ошибка сохранения токена: " + err.message);
        } else {
          console.error("Ошибка сохранения токена:", err);
        }
      });
  }, [botId, botToken]);

  // Функция для сохранения имени бота
  const saveBotName = useCallback(async () => {
    if (!botName.trim()) {
      // На мобильных устройствах показываем уведомление через alert
      if (window.innerWidth <= 768) {
        alert("Имя бота не может быть пустым");
      } else {
        console.log("Имя бота не может быть пустым");
      }
      return;
    }

    try {
      const response = await axios.post(`http://127.0.0.1:8001/set_bot_name/${botId}/`, { name: botName });
      // На мобильных устройствах показываем уведомление через alert
      if (window.innerWidth <= 768) {
        alert(response.data.message);
      } else {
        console.log(response.data.message);
      }
    } catch (err) {
      const errorMessage = err.response?.data?.message || err.message;
      // На мобильных устройствах показываем уведомление через alert
      if (window.innerWidth <= 768) {
        alert("Ошибка сохранения имени бота: " + errorMessage);
      } else {
        console.error("Ошибка сохранения имени бота:", errorMessage);
      }
    }
  }, [botId, botName]);

  const runBot = useCallback(async () => {
    if (!botToken) {
      // На мобильных устройствах показываем уведомление через alert
      if (window.innerWidth <= 768) {
        alert("Сначала сохраните токен");
      } else {
        console.log("Сначала сохраните токен");
      }
      return;
    }

    setLoadingStatus(true);
    try {
      const response = await axios.post(`http://127.0.0.1:8001/run_bot/${botId}/`, { token: botToken });
      // На мобильных устройствах показываем уведомление через alert
      if (window.innerWidth <= 768) {
        alert(response.data.message);
      } else {
        console.log(response.data.message);
      }
      // После запуска проверяем статус
      setTimeout(checkBotStatus, 1000);
    } catch (err) {
      // На мобильных устройствах показываем уведомление через alert
      if (window.innerWidth <= 768) {
        alert("Ошибка запуска: " + (err.response?.data?.message || err.message));
      } else {
        console.error("Ошибка запуска:", err.response?.data?.message || err.message);
      }
    } finally {
      setLoadingStatus(false);
    }
  }, [botId, botToken, checkBotStatus]);

  // Функция перезапуска бота
  const restartBot = useCallback(async () => {
    if (!botToken) {
      // На мобильных устройствах показываем уведомление через alert
      if (window.innerWidth <= 768) {
        alert("Сначала сохраните токен");
      } else {
        console.log("Сначала сохраните токен");
      }
      return;
    }

    setLoadingStatus(true);
    try {
      const response = await axios.post(`http://127.0.0.1:8001/restart_bot/${botId}/`);
      // На мобильных устройствах показываем уведомление через alert
      if (window.innerWidth <= 768) {
        alert(response.data.message);
      } else {
        console.log(response.data.message);
      }
      // После перезапуска проверяем статус
      setTimeout(checkBotStatus, 1000);
    } catch (err) {
      // На мобильных устройствах показываем уведомление через alert
      if (window.innerWidth <= 768) {
        alert("Ошибка перезапуска: " + (err.response?.data?.message || err.message));
      } else {
        console.error("Ошибка перезапуска:", err.response?.data?.message || err.message);
      }
    } finally {
      setLoadingStatus(false);
    }
  }, [botId, botToken, checkBotStatus]);

  // Функция остановки бота
  const stopBot = useCallback(async () => {
    setLoadingStatus(true);
    try {
      const response = await axios.get(`http://127.0.0.1:8001/stop_bot/${botId}/`);
      // На мобильных устройствах показываем уведомление через alert
      if (window.innerWidth <= 768) {
        alert(response.data.message);
      } else {
        console.log(response.data.message);
      }
      // После остановки проверяем статус
      setTimeout(checkBotStatus, 1000);
    } catch (err) {
      // На мобильных устройствах показываем уведомление через alert
      if (window.innerWidth <= 768) {
        alert("Ошибка остановки: " + (err.response?.data?.message || err.message));
      } else {
        console.error("Ошибка остановки:", err.response?.data?.message || err.message);
      }
    } finally {
      setLoadingStatus(false);
    }
  }, [botId, checkBotStatus]);

  const onNodesChange = useCallback(
    changes => {
      console.log('Nodes changed:', changes);
      setInitialNodes(nds => {
        const updatedNodes = applyNodeChanges(changes, nds);
        console.log('Updated nodes:', updatedNodes);
        return updatedNodes;
      });
    },
    []
  );

  const onEdgesChange = useCallback(
    changes => {
      setEdges(eds => {
        const updatedEdges = applyEdgeChanges(changes, eds);
        // Применяем стили в зависимости от состояния выделения
        return updatedEdges.map(edge => ({
          ...edge,
          style: {
            strokeWidth: edge.selected ? 3 : 2,
            stroke: edge.selected ? "#1976d2" : "black"
          },
          markerEnd: {
            type: "arrowclosed",
            color: edge.selected ? "#1976d2" : "black"
          }
        }));
      });
    },
    []
  );

  const onConnect = useCallback(
    connection => setEdges(eds => addEdge({
      ...connection,
      animated: true,
      style: { strokeWidth: 2, stroke: "black" },
      markerEnd: { type: "arrowclosed", color: "black" },
    }, eds)),
    []
  );

  return {
    botId,
    initialNodes,
    edges,
    botToken,
    setBotToken,
    botName, // Возвращаем имя бота
    setBotName, // Возвращаем функцию для установки имени бота
    isBotRunning,
    loadingStatus,
    onDataChange,
    deleteNodeById,
    deleteSelectedNodes,
    deleteAllNodes,
    saveScenario,
    saveToken,
    saveBotName, // Возвращаем функцию сохранения имени бота
    runBot,
    restartBot,
    stopBot,
    onNodesChange,
    onEdgesChange,
    onConnect,
    onDrop,
    onDragOver,
    onInit,
    navigateBack: () => navigate('/'),
    nodesCount: initialNodes.length,
    edgesCount: edges.length,
    selectedCount: initialNodes.filter(n => n.selected).length
  };
};