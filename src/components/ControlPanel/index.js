import React, { useState } from 'react';
import { controlPanelStyles } from './styles';

const ControlPanel = ({
  botToken,
  setBotToken,
  onSaveToken,
  onSaveScenario,
  onDeleteSelected,
  onDeleteAll,
  onUndo,
  onRedo,
  onRunBot,
  onRestartBot,
  onStopBot, // ← Новая функция остановки
  onNavigateBack,
  nodesCount,
  edgesCount,
  selectedCount,
  canUndo,
  canRedo,
  botId,
  isBotRunning, // ← Статус бота
  loadingStatus // ← Состояние загрузки
}) => {
  const [showTokenInput, setShowTokenInput] = useState(false);
  const [showStats, setShowStats] = useState(false);
  const [isRestarting, setIsRestarting] = useState(false);

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
    <div style={controlPanelStyles.panel}>
      {/* Индикатор статуса бота */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        marginRight: '10px',
        padding: '4px 8px',
        borderRadius: '12px',
        background: isBotRunning ? '#28a745' : '#dc3545',
        color: 'white',
        fontSize: '12px',
        fontWeight: 'bold'
      }} title={isBotRunning ? 'Бот запущен' : 'Бот остановлен'}>
        <div style={{
          width: '8px',
          height: '8px',
          borderRadius: '50%',
          background: 'white',
          marginRight: '6px',
          animation: isBotRunning ? 'pulse 1.5s infinite' : 'none'
        }} />
        {isBotRunning ? 'ON' : 'OFF'}
      </div>

      {/* Кнопка назад */}
      <button onClick={onNavigateBack} style={{
        ...controlPanelStyles.button,
        ...controlPanelStyles.secondaryButton
      }} title="Назад к списку">
        ⬅
      </button>

      {/* Управление историей */}
      <button onClick={onUndo} disabled={!canUndo} style={{
        ...controlPanelStyles.button,
        ...controlPanelStyles.secondaryButton,
        opacity: canUndo ? 1 : 0.5
      }} title="Отменить (Ctrl+Z)">
        ↩️
      </button>

      <button onClick={onRedo} disabled={!canRedo} style={{
        ...controlPanelStyles.button,
        ...controlPanelStyles.secondaryButton,
        opacity: canRedo ? 1 : 0.5
      }} title="Повторить (Ctrl+Y)">
        ↪️
      </button>

      {/* Удаление */}
      <button onClick={onDeleteSelected} style={{
        ...controlPanelStyles.button,
        ...controlPanelStyles.dangerButton
      }} title="Удалить выбранные блоки и связи (Delete)">
        🗑️
      </button>

      <button onClick={onDeleteAll} style={{
        ...controlPanelStyles.button,
        ...controlPanelStyles.warningButton
      }} title="Удалить все блоки">
        🗑️ ALL
      </button>

      {/* Сохранение */}
      <button onClick={onSaveScenario} style={{
        ...controlPanelStyles.button,
        ...controlPanelStyles.primaryButton
      }} title="Сохранить сценарий">
        💾
      </button>

      {/* Управление токеном */}
      <div style={{ position: "relative" }}>
        <button onClick={() => setShowTokenInput(!showTokenInput)} style={{
          ...controlPanelStyles.button,
          ...controlPanelStyles.successButton
        }} title="Управление токеном">
          🔑
        </button>

        {showTokenInput && (
          <div style={controlPanelStyles.dropdown}>
            <input
              type="password"
              value={botToken}
              onChange={(e) => setBotToken(e.target.value)}
              placeholder="Токен бота"
              style={{
                width: "100%",
                padding: "6px",
                border: "1px solid #ccc",
                borderRadius: "4px",
                marginBottom: "5px",
                fontSize: "12px"
              }}
            />
            <button onClick={onSaveToken} style={{
              ...controlPanelStyles.button,
              ...controlPanelStyles.successButton,
              width: "100%"
            }}>
              Сохранить токен
            </button>
          </div>
        )}
      </div>

      {/* Запуск бота */}
      <button
        onClick={onRunBot}
        disabled={loadingStatus || isBotRunning || !botToken}
        style={{
          ...controlPanelStyles.button,
          ...controlPanelStyles.infoButton,
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
          ...controlPanelStyles.button,
          ...controlPanelStyles.warningButton,
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
          ...controlPanelStyles.button,
          ...controlPanelStyles.dangerButton,
          opacity: (loadingStatus || !isBotRunning) ? 0.6 : 1
        }}
        title={!isBotRunning ? "Бот не запущен" : "Остановить бота"}
      >
        {loadingStatus ? '⏳' : '⏹️'}
      </button>

      {/* Статистика */}
      <div style={{ position: "relative" }}>
        <button onClick={() => setShowStats(!showStats)} style={{
          ...controlPanelStyles.button,
          background: "#f8f9fa",
          color: "#6c757d",
          border: "1px solid #dee2e6"
        }} title="Статистика">
          📊
        </button>

        {showStats && (
          <div style={controlPanelStyles.dropdown}>
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
        `}
      </style>
    </div>
  );
};

export default ControlPanel;