// BotControls.js
import React from "react";

function BotControls({ botId, saveScenario, runBot, deleteSelectedNode, navigate }) {
  return (
    <div style={{ 
      padding: "10px", 
      background: "#f0f0f0", 
      borderBottom: "1px solid #ccc",
      display: "flex",
      flexWrap: "wrap",
      gap: "10px",
      alignItems: "center"
    }}>
      <h2 style={{ 
        margin: 0, 
        fontSize: "1.2rem",
        flex: "1 1 auto",
        minWidth: "200px"
      }}>
        Редактор бота: {botId}
      </h2>
      
      <div style={{ 
        display: "flex", 
        flexWrap: "wrap",
        gap: "5px",
        alignItems: "center",
        flex: "1 1 auto"
      }}>
        <button 
          onClick={saveScenario} 
          style={{ 
            padding: "8px 12px", 
            background: "#28a745", 
            color: "white", 
            border: "none", 
            borderRadius: "4px", 
            cursor: "pointer",
            fontSize: "14px"
          }}
        >
          💾 Сохранить
        </button>
        
        <button 
          onClick={() => { saveScenario(); navigate("/"); }} 
          style={{ 
            padding: "8px 12px", 
            background: "#6c757d", 
            color: "white", 
            border: "none", 
            borderRadius: "4px", 
            cursor: "pointer",
            fontSize: "14px"
          }}
        >
          ⬅ Назад к списку ботов
        </button>
        
        <button 
          onClick={deleteSelectedNode} 
          style={{ 
            padding: "8px 12px", 
            background: "#dc3545", 
            color: "white", 
            border: "none", 
            borderRadius: "4px", 
            cursor: "pointer",
            fontSize: "14px"
          }}
        >
          ❌ Удалить выбранный блок
        </button>
        
        <button
          onClick={() => runBot("8495785437:AAFR_fwx0AlVTcVanFMwZ7Uf5Z4t3Sk-YdA")}
          style={{ 
            padding: "8px 12px", 
            background: "#17a2b8", 
            color: "white", 
            border: "none", 
            borderRadius: "4px", 
            cursor: "pointer",
            fontSize: "14px"
          }}
        >
          ▶️ Запустить бота
        </button>
      </div>
      
      {/* Адаптивные стили для мобильных устройств */}
      <style>
        {`
          @media (max-width: 768px) {
            div[style*="padding: \\"10px\\""] {
              padding: "8px";
            }
            
            h2 {
              fontSize: "1rem";
            }
            
            button {
              padding: "6px 10px";
              fontSize: "12px";
            }
          }
          
          @media (max-width: 480px) {
            div[style*="padding: \\"10px\\""] {
              padding: "6px";
              flexDirection: "column";
              alignItems: "stretch";
            }
            
            h2 {
              fontSize: "0.9rem";
              textAlign: "center";
            }
            
            div[style*="display: \\"flex\\""] {
              flexDirection: "column";
              gap: "5px";
            }
            
            button {
              padding: "5px 8px";
              fontSize: "11px";
              width: "100%";
            }
          }
        `}
      </style>
    </div>
  );
}

export default BotControls;