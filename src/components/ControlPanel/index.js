import React, { useState, useEffect } from 'react';
import { controlPanelStyles, mobileControlPanelStyles } from './styles';

const ControlPanel = ({
  botToken,
  setBotToken,
  botName, // Получаем имя бота
  setBotName, // Получаем функцию для установки имени бота
  onSaveToken,
  onSaveBotName, // Получаем функцию сохранения имени бота
  onSaveScenario,
  onDeleteSelected,
  onDeleteAll,
  onRunBot,
  onRestartBot,
  onStopBot, // ← Новая функция остановки
  onNavigateBack,
  nodesCount,
  edgesCount,
  selectedCount,
  botId,
  isBotRunning, // ← Статус бота
  loadingStatus // ← Состояние загрузки
}) => {
  const [showTokenInput, setShowTokenInput] = useState(false);
  const [showBotNameInput, setShowBotNameInput] = useState(false); // Состояние для отображения поля имени бота
  const [showStats, setShowStats] = useState(false);
  const [isRestarting, setIsRestarting] = useState(false);
  const [isMobile, setIsMobile] = useState(window.innerWidth <= 768);

  // Отслеживаем изменение размера экрана
  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth <= 768);
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Используем разные стили для мобильных и десктопных устройств
  const styles = isMobile ? mobileControlPanelStyles : controlPanelStyles;

  const handleRestart = async () => {
    if (typeof onRestartBot !== 'function') {
      console.error('onRestartBot is not a function');
      alert('Функция перезапуска недоступна');
      return;
    }

    setIsRestarting(true);
    try {
      await onRestartBot();
    } catch (error) {
      console.error('Error restarting bot:', error);
      alert('Ошибка при перезапуске бота');
    } finally {
      setIsRestarting(false);
    }
  };

  const handleStop = async () => {
    if (typeof onStopBot !== 'function') {
      console.error('onStopBot is not a function');
      alert('Функция остановки недоступна');
      return;
    }

    try {
      await onStopBot();
    } catch (error) {
      console.error('Error stopping bot:', error);
      alert('Ошибка при остановке бота');
    }
  };

  return (
    <div style={styles.panel}>
      {/* Индикатор статуса бота */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        marginRight: '5px',
        padding: isMobile ? '3px 6px' : '4px 8px',
        borderRadius: '12px',
        background: isBotRunning ? '#28a745' : '#dc3545',
        color: 'white',
        fontSize: isMobile ? '10px' : '12px',
        fontWeight: 'bold'
      }} title={isBotRunning ? 'Бот запущен' : 'Бот остановлен'}>
        <div style={{
          width: isMobile ? '6px' : '8px',
          height: isMobile ? '6px' : '8px',
          borderRadius: '50%',
          background: 'white',
          marginRight: isMobile ? '4px' : '6px',
          animation: isBotRunning ? 'pulse 1.5s infinite' : 'none'
        }} />
        {isBotRunning ? 'ON' : 'OFF'}
      </div>

      {/* Кнопка назад */}
      <button onClick={onNavigateBack} style={{
        ...styles.button,
        ...styles.secondaryButton
      }} title="Назад к списку">
        ⬅
      </button>

      {/* Удаление */}
      <button onClick={onDeleteSelected} style={{
        ...styles.button,
        ...styles.dangerButton
      }} title="Удалить выбранные блоки и связи (Delete)">
        🗑️
      </button>

      <button onClick={onDeleteAll} style={{
        ...styles.button,
        ...styles.warningButton
      }} title="Удалить все блоки">
        🗑️ ALL
      </button>

      {/* Сохранение */}
      <button onClick={onSaveScenario} style={{
        ...styles.button,
        ...styles.primaryButton
      }} title="Сохранить сценарий">
        💾
      </button>

      {/* Управление токеном */}
      <div style={{ position: "relative" }}>
        <button onClick={() => setShowTokenInput(!showTokenInput)} style={{
          ...styles.button,
          ...styles.successButton
        }} title="Управление токеном">
          🔑
        </button>

        {showTokenInput && (
          <div style={styles.dropdown}>
            <input
              type="password"
              value={botToken}
              onChange={(e) => setBotToken(e.target.value)}
              placeholder="Токен бота"
              style={{
                width: "100%",
                padding: isMobile ? "4px" : "6px",
                border: "1px solid #ccc",
                borderRadius: "4px",
                marginBottom: "5px",
                fontSize: isMobile ? "10px" : "12px"
              }}
            />
            <button onClick={onSaveToken} style={{
              ...styles.button,
              ...styles.successButton,
              width: "100%"
            }}>
              Сохранить токен
            </button>
          </div>
        )}
      </div>

      {/* Управление именем бота */}
      <div style={{ position: "relative" }}>
        <button onClick={() => setShowBotNameInput(!showBotNameInput)} style={{
          ...styles.button,
          ...styles.infoButton
        }} title="Управление именем бота">
          📝
        </button>

        {showBotNameInput && (
          <div style={styles.dropdown}>
            <input
              type="text"
              value={botName}
              onChange={(e) => setBotName(e.target.value)}
              placeholder="Имя бота"
              style={{
                width: "100%",
                padding: isMobile ? "4px" : "6px",
                border: "1px solid #ccc",
                borderRadius: "4px",
                marginBottom: "5px",
                fontSize: isMobile ? "10px" : "12px"
              }}
            />
            <button onClick={onSaveBotName} style={{
              ...styles.button,
              ...styles.infoButton,
              width: "100%"
            }}>
              Сохранить имя
            </button>
          </div>
        )}
      </div>

      {/* Запуск бота */}
      <button
        onClick={onRunBot}
        disabled={loadingStatus || isBotRunning || !botToken}
        style={{
          ...styles.button,
          ...styles.infoButton,
          opacity: (loadingStatus || isBotRunning || !botToken) ? 0.6 : 1
        }}
        title={!botToken ? "Сначала сохраните токен" : isBotRunning ? "Бот уже запущен" : "Запустить бота"}
      >
        {loadingStatus ? '⏳' : '▶️'}
      </button>

      {/* Перезапуск бота */}
      <button
        onClick={handleRestart}
        disabled={loadingStatus || !isBotRunning || !botToken}
        style={{
          ...styles.button,
          ...styles.warningButton,
          opacity: (loadingStatus || !isBotRunning || !botToken) ? 0.6 : 1
        }}
        title={!botToken ? "Сначала сохраните токен" : !isBotRunning ? "Сначала запустите бота" : "Перезапустить бота"}
      >
        {isRestarting ? '⏳' : '🔄'}
      </button>

      {/* Остановка бота */}
      <button
        onClick={handleStop}
        disabled={loadingStatus || !isBotRunning}
        style={{
          ...styles.button,
          ...styles.dangerButton,
          opacity: (loadingStatus || !isBotRunning) ? 0.6 : 1
        }}
        title={!isBotRunning ? "Бот не запущен" : "Остановить бота"}
      >
        {loadingStatus ? '⏳' : '⏹️'}
      </button>

      {/* Статистика */}
      <div style={{ position: "relative" }}>
        <button onClick={() => setShowStats(!showStats)} style={{
          ...styles.button,
          background: "#f8f9fa",
          color: "#6c757d",
          border: "1px solid #dee2e6"
        }} title="Статистика">
          📊
        </button>

        {showStats && (
          <div style={styles.dropdown}>
            <div>Блоки: {nodesCount}</div>
            <div>Связи: {edgesCount}</div>
            <div>Выбрано: {selectedCount}</div>
            <div>Статус: {isBotRunning ? '🟢 Запущен' : '🔴 Остановлен'}</div>
            <div style={{marginTop: '5px', paddingTop: '5px', borderTop: '1px solid #eee'}}>
              ID: {botId}
            </div>
          </div>
        )}
      </div>

      {/* Стили для анимации пульсации */}
      <style>
        {`
          @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
          }
          
          /* Скроллбар для панели управления */
          ::-webkit-scrollbar {
            height: 6px;
          }
          
          ::-webkit-scrollbar-track {
            background: #f1f1f1;
          }
          
          ::-webkit-scrollbar-thumb {
            background: #c1c1c1;
            border-radius: 3px;
          }
          
          ::-webkit-scrollbar-thumb:hover {
            background: #a8a8a8;
          }
        `}
      </style>
    </div>
  );
};

export default ControlPanel;