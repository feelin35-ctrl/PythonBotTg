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
  const [isBotRunning, setIsBotRunning] = useState(false);
  const [loadingStatus, setLoadingStatus] = useState(false);

  const { saveToHistory, undo, redo, canUndo, canRedo } = useUndoRedo({
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
    if (selectedNodes.length === 0) {
      alert("Выберите блок(и) для удаления");
      return;
    }

    const selectedNodeIds = selectedNodes.map(node => node.id);
    const newNodes = initialNodes.filter(node => !selectedNodeIds.includes(node.id));
    const newEdges = edges.filter(edge =>
      !selectedNodeIds.includes(edge.source) && !selectedNodeIds.includes(edge.target)
    );

    setInitialNodes(newNodes);
    setEdges(newEdges);
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
    onDeleteAll: deleteAllNodes,
    onUndo: undo,
    onRedo: redo
  });

  useEffect(() => {
    axios.get(`http://127.0.0.1:8001/get_scenario/${botId}/`)
      .then((res) => {
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
          style: { strokeWidth: 2, stroke: "black" },
          markerEnd: { type: "arrowclosed", color: "black" },
        }));

        setInitialNodes(loadedNodes);
        setEdges(loadedEdges);
      })
      .catch(console.error);

    axios.get(`http://127.0.0.1:8001/get_token/${botId}/`)
      .then(res => setBotToken(res.data.token || ''))
      .catch(console.error);
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
    .then(() => alert("Сценарий сохранен!"))
    .catch(err => alert("Ошибка сохранения: " + err.message));
  }, [botId, initialNodes, edges]);

  const saveToken = useCallback(() => {
    axios.post(`http://127.0.0.1:8001/save_token/${botId}/`, { token: botToken })
      .then(() => alert("Токен сохранен!"))
      .catch(err => alert("Ошибка сохранения токена: " + err.message));
  }, [botId, botToken]);

  const runBot = useCallback(async () => {
    if (!botToken) {
      alert("Сначала сохраните токен");
      return;
    }

    setLoadingStatus(true);
    try {
      const response = await axios.post(`http://127.0.0.1:8001/run_bot/${botId}/`, { token: botToken });
      alert(response.data.message);
      // После запуска проверяем статус
      setTimeout(checkBotStatus, 1000);
    } catch (err) {
      alert("Ошибка запуска: " + (err.response?.data?.message || err.message));
    } finally {
      setLoadingStatus(false);
    }
  }, [botId, botToken, checkBotStatus]);

  // Функция перезапуска бота
  const restartBot = useCallback(async () => {
    if (!botToken) {
      alert("Сначала сохраните токен");
      return;
    }

    setLoadingStatus(true);
    try {
      const response = await axios.post(`http://127.0.0.1:8001/restart_bot/${botId}/`);
      alert(response.data.message);
      // После перезапуска проверяем статус
      setTimeout(checkBotStatus, 1000);
    } catch (err) {
      alert("Ошибка перезапуска: " + (err.response?.data?.message || err.message));
    } finally {
      setLoadingStatus(false);
    }
  }, [botId, botToken, checkBotStatus]);

  // Функция остановки бота
  const stopBot = useCallback(async () => {
    setLoadingStatus(true);
    try {
      const response = await axios.get(`http://127.0.0.1:8001/stop_bot/${botId}/`);
      alert(response.data.message);
      setIsBotRunning(false);
    } catch (err) {
      alert("Ошибка остановки: " + (err.response?.data?.message || err.message));
    } finally {
      setLoadingStatus(false);
    }
  }, [botId]);

  const onNodesChange = useCallback(
    changes => setInitialNodes(nds => applyNodeChanges(changes, nds)),
    []
  );

  const onEdgesChange = useCallback(
    changes => setEdges(eds => applyEdgeChanges(changes, eds)),
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
    isBotRunning,
    loadingStatus,
    onDataChange,
    deleteNodeById,
    deleteSelectedNodes,
    deleteAllNodes,
    saveScenario,
    saveToken,
    runBot,
    restartBot,
    stopBot,
    onNodesChange,
    onEdgesChange,
    onConnect,
    onDrop,
    onDragOver,
    onInit,
    undo,
    redo,
    canUndo,
    canRedo,
    navigateBack: () => navigate('/'),
    nodesCount: initialNodes.length,
    edgesCount: edges.length,
    selectedCount: initialNodes.filter(n => n.selected).length
  };
};