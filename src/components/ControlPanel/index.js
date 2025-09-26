import React, { useState, useEffect, useRef } from 'react';
import { controlPanelStyles, mobileControlPanelStyles } from './styles';

const ControlPanel = ({
  botToken,
  setBotToken,
  botName, // Получаем имя бота
  setBotName, // Получаем функцию для установки имени бота
  adminChatId, // Получаем adminChatId
  setAdminChatId, // Получаем функцию для установки adminChatId
  onSaveToken,
  onSaveBotName, // Получаем функцию сохранения имени бота
  onSaveAdminChatId, // Получаем функцию сохранения adminChatId
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
  const [showAdminChatIdInput, setShowAdminChatIdInput] = useState(false); // Состояние для отображения поля adminChatId
  const [showStats, setShowStats] = useState(false);
  const [isRestarting, setIsRestarting] = useState(false);
  const [isMobile, setIsMobile] = useState(window.innerWidth <= 768);
  const tokenButtonRef = useRef(null);
  const botNameButtonRef = useRef(null);
  const adminChatIdButtonRef = useRef(null); // Ref для кнопки adminChatId
  const statsButtonRef = useRef(null);
  const tokenPopupRef = useRef(null);
  const botNamePopupRef = useRef(null);
  const adminChatIdPopupRef = useRef(null); // Ref для попапа adminChatId
  const statsPopupRef = useRef(null);

  const [tokenPopupVisible, setTokenPopupVisible] = useState(false);
  const [botNamePopupVisible, setBotNamePopupVisible] = useState(false);
  const [adminChatIdPopupVisible, setAdminChatIdPopupVisible] = useState(false); // Состояние видимости попапа adminChatId
  const [statsPopupVisible, setStatsPopupVisible] = useState(false);

  // Удаляем эффекты позиционирования, которые вызывали перемещение попапов после появления
  // Эти эффекты были здесь:
  // useEffect для позиционирования попапа токена
  // useEffect для позиционирования попапа имени бота
  // useEffect для позиционирования попапа статистики

  // Оставляем только эффект для обработки изменения размера окна
  // Отслеживаем изменение размера экрана
  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth <= 768);
      // Перепозиционируем попапы при изменении размера окна
      if (showTokenInput && tokenPopupVisible && tokenPopupRef.current) {
        positionPopup(tokenButtonRef, tokenPopupRef);
      }
      if (showBotNameInput && botNamePopupVisible && botNamePopupRef.current) {
        positionPopup(botNameButtonRef, botNamePopupRef);
      }
      if (showAdminChatIdInput && adminChatIdPopupVisible && adminChatIdPopupRef.current) {
        positionPopup(adminChatIdButtonRef, adminChatIdPopupRef);
      }
      if (showStats && statsPopupVisible && statsPopupRef.current) {
        positionPopup(statsButtonRef, statsPopupRef);
      }
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [showTokenInput, tokenPopupVisible, showBotNameInput, botNamePopupVisible, showAdminChatIdInput, adminChatIdPopupVisible, showStats, statsPopupVisible]);

  // Обработчик для закрытия попапов при клике вне их области
  useEffect(() => {
    const handleClickOutside = (event) => {
      // Проверяем каждый попап отдельно
      
      // Токен попап
      if (showTokenInput && tokenPopupVisible && tokenPopupRef.current) {
        const isClickInsidePopup = tokenPopupRef.current.contains(event.target);
        const isClickOnButton = tokenButtonRef.current && tokenButtonRef.current.contains(event.target);
        
        // Если клик был вне попапа и вне кнопки, закрываем попап
        if (!isClickInsidePopup && !isClickOnButton) {
          setShowTokenInput(false);
          setTokenPopupVisible(false);
        }
      }
      
      // Попап имени бота
      if (showBotNameInput && botNamePopupVisible && botNamePopupRef.current) {
        const isClickInsidePopup = botNamePopupRef.current.contains(event.target);
        const isClickOnButton = botNameButtonRef.current && botNameButtonRef.current.contains(event.target);
        
        // Если клик был вне попапа и вне кнопки, закрываем попап
        if (!isClickInsidePopup && !isClickOnButton) {
          setShowBotNameInput(false);
          setBotNamePopupVisible(false);
        }
      }
      
      // Попап adminChatId
      if (showAdminChatIdInput && adminChatIdPopupVisible && adminChatIdPopupRef.current) {
        const isClickInsidePopup = adminChatIdPopupRef.current.contains(event.target);
        const isClickOnButton = adminChatIdButtonRef.current && adminChatIdButtonRef.current.contains(event.target);
        
        // Если клик был вне попапа и вне кнопки, закрываем попап
        if (!isClickInsidePopup && !isClickOnButton) {
          setShowAdminChatIdInput(false);
          setAdminChatIdPopupVisible(false);
        }
      }
      
      // Попап статистики
      if (showStats && statsPopupVisible && statsPopupRef.current) {
        const isClickInsidePopup = statsPopupRef.current.contains(event.target);
        const isClickOnButton = statsButtonRef.current && statsButtonRef.current.contains(event.target);
        
        // Если клик был вне попапа и вне кнопки, закрываем попап
        if (!isClickInsidePopup && !isClickOnButton) {
          setShowStats(false);
          setStatsPopupVisible(false);
        }
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [showTokenInput, tokenPopupVisible, showBotNameInput, botNamePopupVisible, showAdminChatIdInput, adminChatIdPopupVisible, showStats, statsPopupVisible]);

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

  // Оставляем только базовую функцию позиционирования для обработки изменения размера окна
  // Функция для позиционирования попапов по центру сверху экрана (для коррекции при изменении размера окна)
  const positionPopup = (buttonRef, popupRef) => {
    if (!popupRef.current) return;
    
    // Получаем реальные размеры попапа
    const popupRect = popupRef.current.getBoundingClientRect();
    
    // Используем реальные размеры попапа, если они доступны
    const popupWidth = popupRect.width > 0 ? popupRect.width : 200;
    
    // Минимальные отступы от краев экрана
    const minOffset = 10;
    
    // Центрируем попап по горизонтали
    let left = (window.innerWidth - popupWidth) / 2;
    
    // Убеждаемся, что попап не выходит за границы экрана
    if (left < minOffset) {
      left = minOffset;
    }
    
    if (left + popupWidth > window.innerWidth - minOffset) {
      left = window.innerWidth - popupWidth - minOffset;
    }
    
    // Применяем позицию
    popupRef.current.style.left = `${left}px`;
    // Вертикальная позиция остается фиксированной
    popupRef.current.style.top = '20px';
  };

  // Функция для показа попапа токена
  const showTokenPopup = () => {
    setShowTokenInput(true);
    setTokenPopupVisible(true);
  };

  // Функция для показа попапа имени бота
  const showBotNamePopup = () => {
    setShowBotNameInput(true);
    setBotNamePopupVisible(true);
  };

  // Функция для показа попапа статистики
  const showStatsPopup = () => {
    setShowStats(true);
    setStatsPopupVisible(true);
  };

  // Функция для показа попапа adminChatId
  const showAdminChatIdPopup = () => {
    setShowAdminChatIdInput(true);
    setAdminChatIdPopupVisible(true);
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
        <button 
          ref={tokenButtonRef}
          onClick={() => {
            if (showTokenInput) {
              setShowTokenInput(false);
              setTokenPopupVisible(false);
            } else {
              showTokenPopup();
            }
          }} 
          style={{
            ...styles.button,
            ...styles.successButton
          }} 
          title="Управление токеном"
        >
          🔑
        </button>

        {showTokenInput && tokenPopupVisible && (
          <div 
            ref={tokenPopupRef} 
            style={{
              position: 'fixed',
              background: 'white',
              padding: '10px',
              borderRadius: '4px',
              boxShadow: '0 2px 10px rgba(0,0,0,0.2)',
              zIndex: 10000,
              minWidth: '150px',
              fontSize: isMobile ? '10px' : '12px',
              maxWidth: '90vw',
              maxHeight: '90vh',
              opacity: tokenPopupVisible ? 1 : 0,
              transform: tokenPopupVisible ? 'scale(1)' : 'scale(0.95)',
              transition: 'opacity 0.2s ease, transform 0.2s ease',
              // Позиционируем попап по центру сверху сразу при рендере
              left: '50%',
              top: '20px',
              transformOrigin: 'top center',
              marginLeft: '-100px' // Половина ширины попапа (примерно)
            }}
          >
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
            <button onClick={() => {
              onSaveToken();
              setShowTokenInput(false);
              setTokenPopupVisible(false);
            }} style={{
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
        <button 
          ref={botNameButtonRef}
          onClick={() => {
            if (showBotNameInput) {
              setShowBotNameInput(false);
              setBotNamePopupVisible(false);
            } else {
              showBotNamePopup();
            }
          }} 
          style={{
            ...styles.button,
            ...styles.infoButton
          }} 
          title="Управление именем бота"
        >
          📝
        </button>

        {showBotNameInput && botNamePopupVisible && (
          <div 
            ref={botNamePopupRef} 
            style={{
              position: 'fixed',
              background: 'white',
              padding: '10px',
              borderRadius: '4px',
              boxShadow: '0 2px 10px rgba(0,0,0,0.2)',
              zIndex: 10000,
              minWidth: '150px',
              fontSize: isMobile ? '10px' : '12px',
              maxWidth: '90vw',
              maxHeight: '90vh',
              opacity: botNamePopupVisible ? 1 : 0,
              transform: botNamePopupVisible ? 'scale(1)' : 'scale(0.95)',
              transition: 'opacity 0.2s ease, transform 0.2s ease',
              // Позиционируем попап по центру сверху сразу при рендере
              left: '50%',
              top: '20px',
              transformOrigin: 'top center',
              marginLeft: '-100px' // Половина ширины попапа (примерно)
            }}
          >
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
            <button onClick={() => {
              onSaveBotName();
              setShowBotNameInput(false);
              setBotNamePopupVisible(false);
            }} style={{
              ...styles.button,
              ...styles.infoButton,
              width: "100%"
            }}>
              Сохранить имя
            </button>
          </div>
        )}
      </div>

      {/* Управление Chat ID администратора */}
      <div style={{ position: "relative" }}>
        <button 
          ref={adminChatIdButtonRef}
          onClick={() => {
            if (showAdminChatIdInput) {
              setShowAdminChatIdInput(false);
              setAdminChatIdPopupVisible(false);
            } else {
              showAdminChatIdPopup();
            }
          }} 
          style={{
            ...styles.button,
            ...styles.warningButton
          }} 
          title="Управление Chat ID администратора"
        >
          👤
        </button>

        {showAdminChatIdInput && adminChatIdPopupVisible && (
          <div 
            ref={adminChatIdPopupRef} 
            style={{
              position: 'fixed',
              background: 'white',
              padding: '10px',
              borderRadius: '4px',
              boxShadow: '0 2px 10px rgba(0,0,0,0.2)',
              zIndex: 10000,
              minWidth: '150px',
              fontSize: isMobile ? '10px' : '12px',
              maxWidth: '90vw',
              maxHeight: '90vh',
              opacity: adminChatIdPopupVisible ? 1 : 0,
              transform: adminChatIdPopupVisible ? 'scale(1)' : 'scale(0.95)',
              transition: 'opacity 0.2s ease, transform 0.2s ease',
              // Позиционируем попап по центру сверху сразу при рендере
              left: '50%',
              top: '20px',
              transformOrigin: 'top center',
              marginLeft: '-100px' // Половина ширины попапа (примерно)
            }}
          >
            <input
              type="text"
              value={adminChatId || ""}
              onChange={(e) => {
                // Разрешаем только цифры
                const value = e.target.value.replace(/[^0-9]/g, '');
                setAdminChatId(value);
              }}
              placeholder="Chat ID администратора"
              style={{
                width: "100%",
                padding: isMobile ? "4px" : "6px",
                border: "1px solid #ccc",
                borderRadius: "4px",
                marginBottom: "5px",
                fontSize: isMobile ? "10px" : "12px"
              }}
            />
            <div style={{ 
              fontSize: "10px", 
              color: "#999", 
              marginBottom: "5px",
              fontStyle: "italic"
            }}>
              Только цифры
            </div>
            <button onClick={() => {
              onSaveAdminChatId();
              setShowAdminChatIdInput(false);
              setAdminChatIdPopupVisible(false);
            }} style={{
              ...styles.button,
              ...styles.warningButton,
              width: "100%"
            }}>
              Сохранить Chat ID
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
        <button 
          ref={statsButtonRef}
          onClick={() => {
            if (showStats) {
              setShowStats(false);
              setStatsPopupVisible(false);
            } else {
              showStatsPopup();
            }
          }} 
          style={{
            ...styles.button,
            background: "#f8f9fa",
            color: "#6c757d",
            border: "1px solid #dee2e6"
          }} 
          title="Статистика"
        >
          📊
        </button>

        {showStats && statsPopupVisible && (
          <div 
            ref={statsPopupRef} 
            style={{
              position: 'fixed',
              background: 'white',
              padding: '10px',
              borderRadius: '4px',
              boxShadow: '0 2px 10px rgba(0,0,0,0.2)',
              zIndex: 10000,
              minWidth: '150px',
              fontSize: isMobile ? '10px' : '12px',
              maxWidth: '90vw',
              maxHeight: '90vh',
              opacity: statsPopupVisible ? 1 : 0,
              transform: statsPopupVisible ? 'scale(1)' : 'scale(0.95)',
              transition: 'opacity 0.2s ease, transform 0.2s ease',
              // Позиционируем попап по центру сверху сразу при рендере
              left: '50%',
              top: '20px',
              transformOrigin: 'top center',
              marginLeft: '-100px' // Половина ширины попапа (примерно)
            }}
          >
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