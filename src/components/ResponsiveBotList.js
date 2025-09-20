import React, { useState, useEffect } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import styled from 'styled-components';
import { breakpoints, mediaQueries } from '../styles/responsive';

// Стили для адаптивного дизайна
const Container = styled.div`
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
  
  ${mediaQueries.tablet} {
    padding: 15px;
  }
  
  ${mediaQueries.mobile} {
    padding: 10px;
  }
`;

const Title = styled.h1`
  text-align: center;
  margin-bottom: 30px;
  
  ${mediaQueries.tablet} {
    margin-bottom: 20px;
    font-size: 1.5rem;
  }
  
  ${mediaQueries.mobile} {
    margin-bottom: 15px;
    font-size: 1.3rem;
  }
`;

const FormGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
  
  ${mediaQueries.tablet} {
    grid-template-columns: 1fr;
    gap: 15px;
    margin-bottom: 20px;
  }
`;

const Card = styled.div`
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 8px;
  background-color: #f9f9f9;
  
  ${mediaQueries.tablet} {
    padding: 15px;
  }
  
  ${mediaQueries.mobile} {
    padding: 10px;
  }
`;

const Input = styled.input`
  width: 100%;
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
  margin-bottom: 15px;
  box-sizing: border-box;
  
  ${mediaQueries.mobile} {
    padding: 6px;
    margin-bottom: 10px;
  }
`;

const Button = styled.button`
  padding: 10px 15px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-right: 10px;
  
  &:hover {
    background-color: #0056b3;
  }
  
  ${mediaQueries.mobile} {
    padding: 8px 12px;
    margin-right: 5px;
    font-size: 14px;
  }
`;

const BotGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  
  ${mediaQueries.tablet} {
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 15px;
  }
  
  ${mediaQueries.mobile} {
    grid-template-columns: 1fr;
    gap: 10px;
  }
`;

const BotCard = styled.div`
  padding: 15px;
  border: 1px solid #ddd;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  
  ${mediaQueries.mobile} {
    padding: 10px;
  }
`;

const BotName = styled.div`
  font-weight: bold;
  font-size: 16px;
  text-align: center;
  
  ${mediaQueries.mobile} {
    font-size: 14px;
  }
`;

const ButtonGroup = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  justify-content: center;
  
  ${mediaQueries.mobile} {
    gap: 3px;
  }
`;

const ActionButton = styled.button`
  padding: 8px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 5px;
  flex: 1 1 auto;
  min-width: 100px;
  justify-content: center;
  font-size: 14px;
  
  ${mediaQueries.mobile} {
    padding: 6px 10px;
    font-size: 12px;
    min-width: 80px;
  }
`;

const ResponsiveBotList = () => {
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
      const response = await axios.get(`/api/get_bots/`);
      console.log("Получен список ботов:", response.data);
      // Добавляем проверку, что response.data.bots является массивом
      if (response.data && Array.isArray(response.data.bots)) {
        setBots(response.data.bots);
      } else {
        setBots([]); // Устанавливаем пустой массив, если данные некорректны
      }
    } catch (error) {
      console.error("Ошибка при получении списка ботов:", error);
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
      await axios.post(`/api/create_bot/?bot_id=${newBotName}`);

      // 2. Сохраняем токен (исправленный URL)
      console.log("Сохраняем токен...");
      await axios.post(`/api/save_token/${newBotName}/`, {
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

      await axios.post(`/api/save_scenario/${newBotName}/`, initialScenario);

      // 4. Проверяем, что токен сохранился
      console.log("Проверяем сохранение токена...");
      const tokenCheck = await axios.get(`/api/get_token/${newBotName}/`);
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
        await axios.delete(`/api/delete_bot/${botId}/`);
        await axios.delete(`/api/delete_token/${botId}/`);
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
      
      const response = await axios.post(`/api/import_bot/`, importData);
      
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
      // Используем новый endpoint для экспорта ZIP-архива
      const response = await fetch(`/api/export_bot_zip/${botId}/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (response.ok) {
        // Получаем blob и создаем ссылку для скачивания
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        
        // Создаем ссылку для скачивания
        const link = document.createElement('a');
        link.href = url;
        link.download = `bot_${botId}_deploy.zip`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
        
        alert(`✅ Бот "${botId}" экспортирован в ZIP-архив`);
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Ошибка экспорта");
      }
      
    } catch (error) {
      console.error("Ошибка экспорта:", error);
      alert("Ошибка экспорта: " + (error.message || "Неизвестная ошибка"));
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
      const response = await axios.post(`/api/rename_bot/${renamingBotId}/${renameValue}/`);
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
    <Container>
      <Title>Конструктор Telegram ботов</Title>

      <FormGrid>
        {/* Создание бота */}
        <Card>
          <h3>Создать нового бота</h3>

          <Input
            type="text"
            value={newBotName}
            onChange={(e) => setNewBotName(e.target.value)}
            placeholder="Имя бота"
            disabled={showTokenInput}
          />

          {showTokenInput && (
            <Input
              type="password"
              value={botToken}
              onChange={(e) => setBotToken(e.target.value)}
              placeholder="Токен бота от @BotFather"
              style={{ fontFamily: "monospace" }}
            />
          )}

          <div style={{ display: "flex", gap: "10px", flexWrap: "wrap" }}>
            {!showTokenInput ? (
              <Button onClick={handleStartCreate}>
                Создать бота
              </Button>
            ) : (
              <>
                <Button onClick={handleCreateBot} style={{ backgroundColor: "#28a745" }}>
                  Создать
                </Button>
                <Button onClick={handleCancelCreate} style={{ backgroundColor: "#6c757d" }}>
                  Отмена
                </Button>
              </>
            )}
          </div>
        </Card>

        {/* Импорт бота */}
        <Card style={{ backgroundColor: "#f0f8ff" }}>
          <h3>📂 Импорт бота</h3>
          
          {!showImportForm ? (
            <div>
              <p style={{ color: "#666", marginBottom: "15px" }}>
                Импортируйте ранее экспортированного бота с полной конфигурацией
              </p>
              <Button 
                onClick={() => setShowImportForm(true)} 
                style={{ backgroundColor: "#17a2b8" }}
              >
                📂 Импортировать бота
              </Button>
            </div>
          ) : (
            <div>
              <div style={{ marginBottom: "15px" }}>
                <label style={{ display: "block", marginBottom: "5px", fontWeight: "bold" }}>
                  Выберите файл экспорта (.json):
                </label>
                <Input
                  type="file"
                  accept=".json"
                  onChange={(e) => setImportFile(e.target.files[0])}
                />
              </div>
              
              {importProgress && (
                <div style={{ 
                  marginBottom: "15px", 
                  padding: "10px", 
                  backgroundColor: "#e7f3ff", 
                  border: "1px solid #bee5eb", 
                  borderRadius: "4px", 
                  color: "#0c5460" 
                }}>
                  {importProgress}
                </div>
              )}
              
              <div style={{ display: "flex", gap: "10px", flexWrap: "wrap" }}>
                <Button 
                  onClick={handleImportBot} 
                  disabled={!importFile || importProgress}
                  style={{ 
                    backgroundColor: importFile && !importProgress ? "#28a745" : "#6c757d",
                    cursor: importFile && !importProgress ? "pointer" : "not-allowed"
                  }}
                >
                  🚀 Импортировать
                </Button>
                <Button 
                  onClick={handleCancelImport}
                  disabled={importProgress}
                  style={{ 
                    backgroundColor: "#6c757d",
                    cursor: importProgress ? "not-allowed" : "pointer"
                  }}
                >
                  ❌ Отмена
                </Button>
              </div>
            </div>
          )}
        </Card>
      </FormGrid>

      {/* Список ботов */}
      <div>
        <h3>Мои боты ({Array.isArray(bots) ? bots.length : 0})</h3>
        {!Array.isArray(bots) || bots.length === 0 ? (
          <p>Нет созданных ботов</p>
        ) : (
          <BotGrid>
            {Array.isArray(bots) && bots.map((bot) => (
              <BotCard key={bot}>
                {renamingBotId === bot ? (
                  <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
                    <Input
                      type="text"
                      value={renameValue}
                      onChange={(e) => setRenameValue(e.target.value)}
                      placeholder="Новое имя бота"
                      onKeyDown={(e) => {
                        if (e.key === 'Enter') {
                          confirmRename();
                        } else if (e.key === 'Escape') {
                          cancelRename();
                        }
                      }}
                      autoFocus
                    />
                    <ButtonGroup>
                      <ActionButton 
                        onClick={confirmRename}
                        style={{ backgroundColor: "#28a745", color: "white" }}
                      >
                        ✓
                      </ActionButton>
                      <ActionButton 
                        onClick={cancelRename}
                        style={{ backgroundColor: "#6c757d", color: "white" }}
                      >
                        ✕
                      </ActionButton>
                    </ButtonGroup>
                  </div>
                ) : (
                  <>
                    <BotName>{bot}</BotName>
                    <ButtonGroup>
                      <ActionButton 
                        onClick={() => startRename(bot)}
                        style={{ backgroundColor: "#ffc107", color: "black" }}
                      >
                        ✏️ Переименовать
                      </ActionButton>
                      <ActionButton 
                        onClick={() => navigate(`/editor/${bot}`)}
                        style={{ backgroundColor: "#007bff", color: "white" }}
                      >
                        ✏️ Редактировать
                      </ActionButton>
                      <ActionButton 
                        onClick={() => handleExportBot(bot)}
                        style={{ backgroundColor: "#17a2b8", color: "white" }}
                      >
                        📤 Экспорт
                      </ActionButton>
                      <ActionButton 
                        onClick={() => handleDeleteBot(bot)}
                        style={{ backgroundColor: "#dc3545", color: "white" }}
                      >
                        🗑️ Удалить
                      </ActionButton>
                    </ButtonGroup>
                  </>
                )}
              </BotCard>
            ))}
          </BotGrid>
        )}
      </div>
    </Container>
  );
};

export default ResponsiveBotList;