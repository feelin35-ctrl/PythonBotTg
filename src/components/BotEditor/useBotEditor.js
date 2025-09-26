import { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { applyNodeChanges, applyEdgeChanges, addEdge } from 'reactflow';
import api from '../../api'; // Импортируем наш настроенный экземпляр axios
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
  const [adminChatId, setAdminChatId] = useState(''); // Добавляем состояние для chat ID администратора
  const [isBotRunning, setIsBotRunning] = useState(false);
  const [loadingStatus, setLoadingStatus] = useState(false);

  // Функция для проверки статуса бота
  const checkBotStatus = useCallback(async () => {
    try {
      // Используем наш настроенный экземпляр axios
      const response = await api.get(`/api/bot_running_status/${botId}/`);
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

    // Инициализируем данные в зависимости от типа блока
    let initialData = {
      label: type === 'message' ? 'Новое сообщение' : '',
      blockType: type,
      onChange: onDataChange
    };

    // Для блока keyword_processor добавляем начальные значения
    if (type === 'keyword_processor') {
      initialData = {
        ...initialData,
        keywords: [],
        caseSensitive: false,
        matchMode: 'exact'
      };
    }

    const newNode = {
      id: uuidv4(),
      type: 'editable',
      position,
      data: initialData
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
    // Функция для обработки ошибок API
    const handleApiError = (error, operation) => {
      console.error(`Error ${operation}:`, error);
      
      // Проверяем таймаут
      if (error.code === 'ECONNABORTED') {
        console.error('Connection timeout - please check if the backend server is running');
        // Можно показать пользователю уведомление
        if (window.innerWidth <= 768) {
          alert(`Ошибка подключения к серверу. Пожалуйста, проверьте интернет-соединение.`);
        }
      } else if (!error.response) {
        console.error('Network error - please check your connection');
        if (window.innerWidth <= 768) {
          alert(`Ошибка сети. Пожалуйста, проверьте интернет-соединение.`);
        }
      }
    };

    api.get(`/api/get_scenario/${botId}/`)
      .then((res) => {
        console.log('Loaded scenario data:', res.data);
        const loadedNodes = (res.data.nodes || []).map(n => ({
          ...n,
          type: "editable",
          data: {
            ...n.data,
            blockType: n.data?.blockType || n.type,
            onChange: onDataChange,
            // Для блока keyword_processor восстанавливаем пользовательские данные
            keywords: n.data?.blockType === 'keyword_processor' ? (n.data?.keywords || []) : n.data?.keywords,
            caseSensitive: n.data?.blockType === 'keyword_processor' ? (n.data?.caseSensitive || false) : n.data?.caseSensitive,
            matchMode: n.data?.blockType === 'keyword_processor' ? (n.data?.matchMode || 'exact') : n.data?.matchMode
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
        
        // Устанавливаем adminChatId из данных сценария, если он есть
        if (res.data.adminChatId) {
          setAdminChatId(res.data.adminChatId);
        }
      })
      .catch(error => {
        handleApiError(error, 'loading scenario');
      });

    // Функция для загрузки токена из базы данных
    const loadTokenFromDatabase = async () => {
      try {
        // Получаем информацию о текущем пользователе из localStorage
        const storedUser = localStorage.getItem('user');
        if (!storedUser) {
          console.log("Пользователь не авторизован, не можем загрузить токен из базы данных");
          return;
        }

        let user;
        try {
          user = JSON.parse(storedUser);
        } catch (e) {
          console.log("Ошибка получения данных пользователя");
          return;
        }

        // Загружаем токен из базы данных
        const response = await api.get(`/api/user/get_token/${botId}/?user_id=${user.id}`);
        if (response.data && response.data.token) {
          setBotToken(response.data.token);
          // Также сохраняем в localStorage для резервной загрузки
          localStorage.setItem(`botToken_${botId}`, response.data.token);
          console.log("Токен успешно загружен из базы данных");
        }
      } catch (err) {
        console.error("Ошибка загрузки токена из базы данных:", err);
        // Если не удалось загрузить из базы данных, пробуем из localStorage
        const savedToken = localStorage.getItem(`botToken_${botId}`) || '';
        setBotToken(savedToken);
      }
    };

    // Загружаем токен из базы данных или localStorage
    loadTokenFromDatabase();
      
    // Устанавливаем имя бота равным его ID, так как у нас нет отдельного поля для имени
    setBotName(botId || '');
  }, [botId, onDataChange]);

  const saveScenario = useCallback(() => {
    const cleanNodes = initialNodes.map(({ data, ...rest }) => {
      const { onChange, ...cleanData } = data;
      // Для блока keyword_processor сохраняем пользовательские данные
      if (data.blockType === 'keyword_processor') {
        return { 
          ...rest, 
          type: data.blockType, 
          data: {
            ...cleanData,
            keywords: data.keywords || [],
            caseSensitive: data.caseSensitive || false,
            matchMode: data.matchMode || 'exact'
          } 
        };
      }
      return { ...rest, type: data.blockType, data: cleanData };
    });

    const cleanEdges = edges.map(({ animated, style, markerEnd, ...rest }) => rest);

    // Добавляем adminChatId в данные сценария
    const scenarioData = {
      nodes: cleanNodes,
      edges: cleanEdges,
      adminChatId: adminChatId || undefined // Добавляем adminChatId в данные сценария
    };

    // Получаем информацию о текущем пользователе из localStorage
    const storedUser = localStorage.getItem('user');
    let userId = null;
    if (storedUser) {
      try {
        const user = JSON.parse(storedUser);
        userId = user.id;
      } catch (e) {
        console.error("Ошибка получения данных пользователя:", e);
      }
    }

    // Формируем URL с user_id в query параметрах, если пользователь авторизован
    let url = `/api/save_scenario/${botId}/`;
    if (userId) {
      url += `?user_id=${userId}`;
    }

    api.post(url, scenarioData)
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
  }, [botId, initialNodes, edges, adminChatId]);

  const saveToken = useCallback(async () => {
    // Получаем информацию о текущем пользователе из localStorage
    const storedUser = localStorage.getItem('user');
    if (!storedUser) {
      // На мобильных устройствах показываем уведомление через alert
      if (window.innerWidth <= 768) {
        alert("Пользователь не авторизован");
      } else {
        console.log("Пользователь не авторизован");
      }
      return;
    }

    let user;
    try {
      user = JSON.parse(storedUser);
    } catch (e) {
      // На мобильных устройствах показываем уведомление через alert
      if (window.innerWidth <= 768) {
        alert("Ошибка получения данных пользователя");
      } else {
        console.log("Ошибка получения данных пользователя");
      }
      return;
    }

    try {
      // Сохраняем токен в базе данных
      await api.post(`/api/user/save_token/`, {
        user_id: user.id,
        bot_id: botId,
        token: botToken
      });

      // На мобильных устройствах показываем уведомление через alert
      if (window.innerWidth <= 768) {
        alert("Токен успешно сохранен в базе данных!");
      } else {
        console.log("Токен успешно сохранен в базе данных");
      }
      
      // Также сохраняем в localStorage как резервную копию
      localStorage.setItem(`botToken_${botId}`, botToken);
    } catch (err) {
      // На мобильных устройствах показываем уведомление через alert
      if (window.innerWidth <= 768) {
        alert("Ошибка сохранения токена: " + (err.response?.data?.message || err.message));
      } else {
        console.error("Ошибка сохранения токена:", err.response?.data?.message || err.message);
      }
      
      // В случае ошибки сохраняем в localStorage как резервный вариант
      localStorage.setItem(`botToken_${botId}`, botToken);
      if (window.innerWidth <= 768) {
        alert("Токен сохранен локально (резервный вариант)!");
      } else {
        console.log("Токен сохранен локально (резервный вариант)");
      }
    }
  }, [botId, botToken]);

  // Функция для сохранения имени бота (временно отключена, так как имя бота совпадает с его ID)
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

    // В текущей архитектуре botId и является именем бота, поэтому сохранение имени не требуется
    console.log("Имя бота совпадает с его ID, сохранение не требуется");
    if (window.innerWidth <= 768) {
      alert("Имя бота совпадает с его ID, сохранение не требуется");
    }
  }, [botId, botName]);

  // Функция для сохранения adminChatId
  const saveAdminChatId = useCallback(async () => {
    if (adminChatId && !/^\d+$/.test(adminChatId)) {
      // На мобильных устройствах показываем уведомление через alert
      if (window.innerWidth <= 768) {
        alert("Chat ID должен содержать только цифры");
      } else {
        console.log("Chat ID должен содержать только цифры");
      }
      return;
    }

    // Просто сохраняем сценарий, который уже включает adminChatId
    saveScenario();
    
    if (window.innerWidth <= 768) {
      alert("Chat ID администратора сохранен!");
    } else {
      console.log("Chat ID администратора сохранен");
    }
  }, [adminChatId, saveScenario]);

  const runBot = useCallback(async () => {
    console.log("=== НАЧАЛО ФУНКЦИИ RUN_BOT ===");
    console.log("botId:", botId);
    console.log("botToken:", botToken);
    console.log("botToken type:", typeof botToken);
    console.log("botToken length:", botToken ? botToken.length : "undefined");
    
    // Проверяем, что botToken определен и не пуст
    if (!botToken) {
      console.log("ОШИБКА: botToken не определен или пуст");
      // На мобильных устройствах показываем уведомление через alert
      if (window.innerWidth <= 768) {
        alert("Сначала сохраните токен");
      } else {
        console.log("Сначала сохраните токен");
      }
      return;
    }

    // Проверяем тип botToken
    if (typeof botToken !== 'string') {
      console.log("ОШИБКА: botToken не является строкой");
      if (window.innerWidth <= 768) {
        alert("Токен имеет неправильный формат");
      } else {
        console.log("Токен имеет неправильный формат");
      }
      return;
    }

    // Проверяем, что botToken не пустая строка
    if (botToken.trim() === '') {
      console.log("ОШИБКА: botToken пустая строка");
      if (window.innerWidth <= 768) {
        alert("Сначала сохраните токен");
      } else {
        console.log("Сначала сохраните токен");
      }
      return;
    }

    console.log("Токен прошел все проверки, отправляем запрос...");

    setLoadingStatus(true);
    try {
      console.log("Отправка запроса на запуск бота...");
      console.log("URL:", `/api/run_bot/${botId}/`);
      console.log("Данные запроса:", { token: botToken });
      
      // Исправляем отправку токена в правильном формате
      const response = await api.post(`/api/run_bot/${botId}/`, { token: botToken });
      console.log("Ответ от сервера:", response);
      
      // На мобильных устройствах показываем уведомление через alert
      if (window.innerWidth <= 768) {
        alert(response.data.message);
      } else {
        console.log(response.data.message);
      }
      // После запуска проверяем статус
      setTimeout(checkBotStatus, 1000);
    } catch (err) {
      console.error("ОШИБКА ЗАПУСКА БОТА:", err);
      console.error("Детали ошибки:", {
        message: err.message,
        response: err.response,
        request: err.request,
        config: err.config
      });
      
      // Проверяем, есть ли детали ошибки от сервера
      if (err.response) {
        console.error("Детали ответа сервера:", {
          status: err.response.status,
          statusText: err.response.statusText,
          headers: err.response.headers,
          data: err.response.data
        });
      }
      
      // На мобильных устройствах показываем уведомление через alert
      if (window.innerWidth <= 768) {
        alert("Ошибка запуска: " + (err.response?.data?.message || err.message));
      } else {
        console.error("Ошибка запуска:", err.response?.data?.message || err.message);
      }
    } finally {
      setLoadingStatus(false);
      console.log("=== КОНЕЦ ФУНКЦИИ RUN_BOT ===");
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
      // Останавливаем бота
      await api.get(`/api/stop_bot/${botId}/`);
      
      // Запускаем бота заново
      const response = await api.post(`/api/run_bot/${botId}/`, { token: botToken });
      
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
      const response = await api.get(`/api/stop_bot/${botId}/`);
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
    adminChatId, // Возвращаем adminChatId
    setAdminChatId, // Возвращаем функцию для установки adminChatId
    isBotRunning,
    loadingStatus,
    onDataChange,
    deleteNodeById,
    deleteSelectedNodes,
    deleteAllNodes,
    saveScenario,
    saveToken,
    saveBotName, // Возвращаем функцию сохранения имени бота
    saveAdminChatId, // Возвращаем функцию сохранения adminChatId
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