import React, { useState, useEffect } from "react";
// Удаляем импорт axios по умолчанию
import api from './api'; // Импортируем наш настроенный экземпляр axios
import { useNavigate } from "react-router-dom";

// Удаляем axios.defaults.baseURL = 'http://localhost:8001'; так как теперь используем настроенный экземпляр

function BotList() {
  const [bots, setBots] = useState([]);
  const [newBotName, setNewBotName] = useState("");
  const [botToken, setBotToken] = useState("");
  const [showTokenInput, setShowTokenInput] = useState(false);
  const [showImportForm, setShowImportForm] = useState(false);
  const [importFile, setImportFile] = useState(null);
  const [importProgress, setImportProgress] = useState("");
  const [renamingBotId, setRenamingBotId] = useState(null);
  const [renameValue, setRenameValue] = useState("");
  const navigate = useNavigate();

  const fetchBots = async () => {
    try {
      console.log("Запрашиваем список ботов...");
      // Используем наш настроенный экземпляр axios
      console.log("Making API call to /api/get_bots/ with api instance");
      const response = await api.get(`/api/get_bots/`);
      console.log("Получен список ботов:", response.data);
      // Добавляем проверку, что response.data.bots является массивом
      if (response.data && Array.isArray(response.data.bots)) {
        setBots(response.data.bots);
      } else {
        setBots([]); // Устанавливаем пустой массив, если данные некорректны
      }
    } catch (error) {
      console.error("Ошибка при получении списка ботов:", error);
      
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
      
      setBots([]); // Устанавливаем пустой массив в случае ошибки
    }
  };

  useEffect(() => {
    fetchBots();
  }, []);

  const handleCreateBot = async () => {
  if (!newBotName.trim()) {
    alert("Имя бота не может быть пустым.");
    return;
  }

  if (!botToken.trim()) {
    alert("Токен бота не может быть пустым.");
    return;
  }

  try {
    // 1. Создаем бота
    console.log("Создаем бота...");
    await api.post(`/api/create_bot/?bot_id=${newBotName}`);

    // 2. Сохраняем токен (исправленный URL)
    console.log("Сохраняем токен...");
    await api.post(`/api/save_token/${newBotName}/`, {
      token: botToken
    });

    // 3. Создаем начальный сценарий
    console.log("Создаем сценарий...");
    const initialScenario = {
      nodes: [
        {
          id: "1",
          type: "start",
          data: {
            blockType: "start",
            label: "Добро пожаловать! Бот работает."
          },
          position: { x: 250, y: 100 }
        },
        {
          id: "2",
          type: "message",
          data: {
            blockType: "message",
            label: "Это тестовое сообщение от вашего бота!"
          },
          position: { x: 250, y: 200 }
        }
      ],
      edges: [
        {
          source: "1",
          target: "2"
        }
      ]
    };

    await api.post(`/api/save_scenario/${newBotName}/`, initialScenario);

    // 4. Проверяем, что токен сохранился
    console.log("Проверяем сохранение токена...");
    const tokenCheck = await api.get(`/api/get_token/${newBotName}/`);
    console.log("Токен сохранен:", tokenCheck.data.token ? "да" : "нет");

    // Сбрасываем форму
    setNewBotName("");
    setBotToken("");
    setShowTokenInput(false);

    // Обновляем список
    console.log("Обновляем список ботов...");
    await fetchBots();

    alert(`Бот "${newBotName}" успешно создан с токеном!`);

  } catch (error) {
    console.error("Полная ошибка:", error);
    alert("Ошибка при создании бота: " + (error.response?.data?.message || error.message));
  }
};

  const handleDeleteBot = async (botId) => {
    if (window.confirm(`Удалить бота "${botId}"?`)) {
      try {
        await api.delete(`/api/delete_bot/${botId}/`);
        await api.delete(`/api/delete_token/${botId}/`);
        console.log("Обновляем список ботов после удаления...");
        await fetchBots();
      } catch (error) {
        alert("Ошибка при удалении: " + (error.response?.data?.message || error.message));
      }
    }
  };

  const handleStartCreate = () => {
    if (!newBotName.trim()) {
      alert("Введите имя бота сначала.");
      return;
    }
    setShowTokenInput(true);
  };

  const handleCancelCreate = () => {
    setShowTokenInput(false);
    setBotToken("");
  };

  const handleImportBot = async () => {
    if (!importFile) {
      alert("Выберите файл для импорта");
      return;
    }

    try {
      setImportProgress("📂 Читаем файл...");
      
      const fileText = await importFile.text();
      const importData = JSON.parse(fileText);
      
      // Проверяем структуру данных
      if (!importData.bot_id || !importData.scenario || !importData.token) {
        throw new Error("Неверный формат файла для импорта");
      }
      
      setImportProgress("🚀 Импортируем бота...");
      
      const response = await api.post(`/api/import_bot/`, importData);
      
      if (response.data.status === "success") {
        setImportProgress("");
        setShowImportForm(false);
        setImportFile(null);
      
        // Обновляем список ботов
        console.log("Обновляем список ботов после импорта...");
        await fetchBots();
      
        alert(`✅ ${response.data.message}\n🔖 Бот: @${response.data.bot_info?.username || 'неизвестно'}`);
      } else {
        throw new Error(response.data.message || "Неизвестная ошибка");
      }
      
    } catch (error) {
      setImportProgress("");
      console.error("Ошибка импорта:", error);
      
      let errorMessage = "Ошибка импорта: ";
      
      if (error.response?.data?.message) {
        errorMessage += error.response.data.message;
      } else if (error.message) {
        errorMessage += error.message;
      } else {
        errorMessage += "Неизвестная ошибка";
      }
      
      alert(errorMessage);
    }
  };

  const handleExportBot = async (botId) => {
    try {
      // Use our configured API instance instead of direct fetch
      const response = await api.post(`/api/export_bot_zip/${botId}/`);
      
      // Since we're using axios, the response structure is different
      // The actual blob is in response.data
      const blob = new Blob([response.data], { type: 'application/zip' });
      const url = window.URL.createObjectURL(blob);
      
      // Create download link
      const link = document.createElement('a');
      link.href = url;
      link.download = `bot_${botId}_deploy.zip`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      alert(`✅ Бот "${botId}" экспортирован в ZIP-архив`);
    } catch (error) {
      console.error("Ошибка экспорта:", error);
      alert("Ошибка экспорта: " + (error.response?.data?.message || error.message || "Неизвестная ошибка"));
    }
  };

  const handleCancelImport = () => {
    setShowImportForm(false);
    setImportFile(null);
    setImportProgress("");
  };

  const startRename = (botId) => {
    setRenamingBotId(botId);
    setRenameValue(botId);
  };

  const cancelRename = () => {
    setRenamingBotId(null);
    setRenameValue("");
  };

  const confirmRename = async () => {
    if (!renameValue.trim()) {
      alert("Новое имя бота не может быть пустым.");
      return;
    }

    if (renameValue === renamingBotId) {
      cancelRename();
      return;
    }

    // Проверяем, что новое имя не совпадает с существующими ботами
    if (bots.includes(renameValue)) {
      alert(`Бот с именем "${renameValue}" уже существует.`);
      return;
    }

    try {
      const response = await api.post(`/api/rename_bot/${renamingBotId}/${renameValue}/`);
      if (response.data.status === "success") {
        setRenamingBotId(null);
        setRenameValue("");
        console.log("Обновляем список ботов после переименования...");
        await fetchBots();
        alert(response.data.message);
      }
    } catch (error) {
      alert("Ошибка переименования: " + (error.response?.data?.detail || error.message));
    }
  };

  return (
    <div style={{ padding: "20px", maxWidth: "1200px", margin: "0 auto" }}>
      <h1 style={{ textAlign: "center" }}>Конструктор Telegram ботов</h1>

      {/* Адаптивная сетка для форм */}
      <div style={{ 
        display: "grid", 
        gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))", 
        gap: "20px", 
        marginBottom: "30px" 
      }}>
        {/* Создание бота */}
        <div style={{ padding: "20px", border: "1px solid #ddd", borderRadius: "8px", backgroundColor: "#f9f9f9" }}>
          <h3>Создать нового бота</h3>

          <div style={{ marginBottom: "15px" }}>
            <input
              type="text"
              value={newBotName}
              onChange={(e) => setNewBotName(e.target.value)}
              placeholder="Имя бота"
              style={{ width: "100%", padding: "8px", border: "1px solid #ccc", borderRadius: "4px" }}
              disabled={showTokenInput}
            />
          </div>

          {showTokenInput && (
            <div style={{ marginBottom: "15px" }}>
              <input
                type="password"
                value={botToken}
                onChange={(e) => setBotToken(e.target.value)}
                placeholder="Токен бота от @BotFather"
                style={{ width: "100%", padding: "8px", border: "1px solid #ccc", borderRadius: "4px", fontFamily: "monospace" }}
              />
            </div>
          )}

          <div style={{ display: "flex", gap: "10px", flexWrap: "wrap" }}>
            {!showTokenInput ? (
              <button onClick={handleStartCreate} style={{ padding: "10px 15px", backgroundColor: "#007bff", color: "white", border: "none", borderRadius: "4px", cursor: "pointer" }}>
                Создать бота
              </button>
            ) : (
              <>
                <button onClick={handleCreateBot} style={{ padding: "10px 15px", backgroundColor: "#28a745", color: "white", border: "none", borderRadius: "4px", cursor: "pointer" }}>
                  Создать
                </button>
                <button onClick={handleCancelCreate} style={{ padding: "10px 15px", backgroundColor: "#6c757d", color: "white", border: "none", borderRadius: "4px", cursor: "pointer" }}>
                  Отмена
                </button>
              </>
            )}
          </div>
        </div>

        {/* Импорт бота */}
        <div style={{ padding: "20px", border: "1px solid #ddd", borderRadius: "8px", backgroundColor: "#f0f8ff" }}>
          <h3>📂 Импорт бота</h3>
          
          {!showImportForm ? (
            <div>
              <p style={{ color: "#666", marginBottom: "15px" }}>
                Импортируйте ранее экспортированного бота с полной конфигурацией
              </p>
              <button 
                onClick={() => setShowImportForm(true)} 
                style={{ 
                  padding: "10px 15px", 
                  backgroundColor: "#17a2b8", 
                  color: "white", 
                  border: "none", 
                  borderRadius: "4px", 
                  cursor: "pointer" 
                }}
              >
                Импортировать бота
              </button>
            </div>
          ) : (
            <div>
              <input
                type="file"
                accept=".json"
                onChange={(e) => setImportFile(e.target.files[0])}
                style={{ marginBottom: "15px", width: "100%" }}
              />
              
              {importProgress && (
                <p style={{ color: "#17a2b8", marginBottom: "15px" }}>{importProgress}</p>
              )}
              
              <div style={{ display: "flex", gap: "10px", flexWrap: "wrap" }}>
                <button 
                  onClick={handleImportBot}
                  disabled={!importFile || importProgress}
                  style={{ 
                    padding: "10px 15px", 
                    backgroundColor: importProgress ? "#6c757d" : "#28a745", 
                    color: "white", 
                    border: "none", 
                    borderRadius: "4px", 
                    cursor: importProgress ? "not-allowed" : "pointer",
                    opacity: importProgress ? 0.7 : 1
                  }}
                >
                  {importProgress ? "Импортируем..." : "Импортировать"}
                </button>
                <button 
                  onClick={handleCancelImport}
                  style={{ 
                    padding: "10px 15px", 
                    backgroundColor: "#6c757d", 
                    color: "white", 
                    border: "none", 
                    borderRadius: "4px", 
                    cursor: "pointer" 
                  }}
                >
                  Отмена
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Список ботов */}
      <div>
        <h2 style={{ marginBottom: "20px" }}>Список ботов</h2>
        
        {bots.length === 0 ? (
          <p style={{ textAlign: "center", color: "#666" }}>Нет созданных ботов. Создайте или импортируйте бота.</p>
        ) : (
          <div style={{ 
            display: "grid", 
            gridTemplateColumns: "repeat(auto-fill, minmax(250px, 1fr))", 
            gap: "20px" 
          }}>
            {bots.map(botId => (
              <div 
                key={botId} 
                style={{ 
                  padding: "15px", 
                  border: "1px solid #ddd", 
                  borderRadius: "8px",
                  display: "flex",
                  flexDirection: "column",
                  gap: "10px"
                }}
              >
                <div style={{ fontWeight: "bold", fontSize: "16px", textAlign: "center" }}>
                  {botId}
                </div>
                
                <div style={{ display: "flex", flexWrap: "wrap", gap: "5px", justifyContent: "center" }}>
                  <button 
                    onClick={() => navigate(`/editor/${botId}`)}
                    style={{ 
                      padding: "8px 12px", 
                      backgroundColor: "#007bff", 
                      color: "white", 
                      border: "none", 
                      borderRadius: "4px", 
                      cursor: "pointer",
                      display: "flex",
                      alignItems: "center",
                      gap: "5px",
                      flex: "1 1 auto",
                      minWidth: "100px",
                      justifyContent: "center"
                    }}
                  >
                    🖊️ Редактор
                  </button>
                  
                  <button 
                    onClick={() => handleExportBot(botId)}
                    style={{ 
                      padding: "8px 12px", 
                      backgroundColor: "#28a745", 
                      color: "white", 
                      border: "none", 
                      borderRadius: "4px", 
                      cursor: "pointer",
                      display: "flex",
                      alignItems: "center",
                      gap: "5px",
                      flex: "1 1 auto",
                      minWidth: "100px",
                      justifyContent: "center"
                    }}
                  >
                    📤 Экспорт
                  </button>
                  
                  {renamingBotId === botId ? (
                    <div style={{ display: "flex", gap: "5px", width: "100%" }}>
                      <input
                        type="text"
                        value={renameValue}
                        onChange={(e) => setRenameValue(e.target.value)}
                        placeholder="Новое имя"
                        style={{ 
                          flex: "1", 
                          padding: "8px", 
                          border: "1px solid #ccc", 
                          borderRadius: "4px",
                          minWidth: "0"
                        }}
                      />
                      <button 
                        onClick={confirmRename}
                        style={{ 
                          padding: "8px 12px", 
                          backgroundColor: "#28a745", 
                          color: "white", 
                          border: "none", 
                          borderRadius: "4px", 
                          cursor: "pointer"
                        }}
                      >
                        ✓
                      </button>
                      <button 
                        onClick={cancelRename}
                        style={{ 
                          padding: "8px 12px", 
                          backgroundColor: "#6c757d", 
                          color: "white", 
                          border: "none", 
                          borderRadius: "4px", 
                          cursor: "pointer"
                        }}
                      >
                        ✕
                      </button>
                    </div>
                  ) : (
                    <button 
                      onClick={() => startRename(botId)}
                      style={{ 
                        padding: "8px 12px", 
                        backgroundColor: "#ffc107", 
                        color: "black", 
                        border: "none", 
                        borderRadius: "4px", 
                        cursor: "pointer",
                        display: "flex",
                        alignItems: "center",
                        gap: "5px",
                        flex: "1 1 auto",
                        minWidth: "100px",
                        justifyContent: "center"
                      }}
                    >
                      🔄 Переименовать
                    </button>
                  )}
                  
                  <button 
                    onClick={() => handleDeleteBot(botId)}
                    style={{ 
                      padding: "8px 12px", 
                      backgroundColor: "#dc3545", 
                      color: "white", 
                      border: "none", 
                      borderRadius: "4px", 
                      cursor: "pointer",
                      display: "flex",
                      alignItems: "center",
                      gap: "5px",
                      flex: "1 1 auto",
                      minWidth: "100px",
                      justifyContent: "center"
                    }}
                  >
                    🗑️ Удалить
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default BotList;