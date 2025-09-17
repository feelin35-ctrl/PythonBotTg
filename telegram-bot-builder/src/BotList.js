import React, { useState, useEffect } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";

function BotList() {
  const [bots, setBots] = useState([]);
  const [newBotName, setNewBotName] = useState("");
  const [botToken, setBotToken] = useState("");
  const [showTokenInput, setShowTokenInput] = useState(false);
  const navigate = useNavigate();
  const API_URL = "http://127.0.0.1:8001";

  const fetchBots = async () => {
    try {
      const response = await axios.get(`${API_URL}/get_bots/`);
      setBots(response.data.bots);
    } catch (error) {
      console.error("Ошибка при получении списка ботов:", error);
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
    await axios.post(`${API_URL}/create_bot/?bot_id=${newBotName}`);

    // 2. Сохраняем токен (исправленный URL)
    console.log("Сохраняем токен...");
    await axios.post(`${API_URL}/save_token/${newBotName}/`, {
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

    await axios.post(`${API_URL}/save_scenario/${newBotName}/`, initialScenario);

    // 4. Проверяем, что токен сохранился
    console.log("Проверяем сохранение токена...");
    const tokenCheck = await axios.get(`${API_URL}/get_token/${newBotName}/`);
    console.log("Токен сохранен:", tokenCheck.data.token ? "да" : "нет");

    // Сбрасываем форму
    setNewBotName("");
    setBotToken("");
    setShowTokenInput(false);

    // Обновляем список
    fetchBots();

    alert(`Бот "${newBotName}" успешно создан с токеном!`);

  } catch (error) {
    console.error("Полная ошибка:", error);
    alert("Ошибка при создании бота: " + (error.response?.data?.message || error.message));
  }
};

  const handleDeleteBot = async (botId) => {
    if (window.confirm(`Удалить бота "${botId}"?`)) {
      try {
        await axios.delete(`${API_URL}/delete_bot/${botId}/`);
        await axios.delete(`${API_URL}/delete_token/${botId}/`);
        fetchBots();
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

  return (
    <div style={{ padding: "20px", maxWidth: "600px", margin: "0 auto" }}>
      <h1>Конструктор Telegram ботов</h1>

      <div style={{ marginBottom: "30px", padding: "20px", border: "1px solid #ddd", borderRadius: "8px", backgroundColor: "#f9f9f9" }}>
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

        <div style={{ display: "flex", gap: "10px" }}>
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

      <div>
        <h3>Мои боты ({bots.length})</h3>
        {bots.length === 0 ? (
          <p>Нет созданных ботов</p>
        ) : (
          <div style={{ border: "1px solid #ddd", borderRadius: "8px" }}>
            {bots.map((bot) => (
              <div key={bot} style={{ padding: "15px", borderBottom: "1px solid #eee", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span style={{ fontWeight: "bold" }}>{bot}</span>
                <div>
                  <button onClick={() => navigate(`/editor/${bot}`)} style={{ padding: "5px 10px", backgroundColor: "#007bff", color: "white", border: "none", borderRadius: "4px", cursor: "pointer", marginRight: "5px" }}>
                    Редактировать
                  </button>
                  <button onClick={() => handleDeleteBot(bot)} style={{ padding: "5px 10px", backgroundColor: "#dc3545", color: "white", border: "none", borderRadius: "4px", cursor: "pointer" }}>
                    Удалить
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default BotList;