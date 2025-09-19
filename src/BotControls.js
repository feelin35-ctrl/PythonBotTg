// BotControls.js
import React from "react";

function BotControls({ botId, saveScenario, runBot, deleteSelectedNode, navigate }) {
  return (
    <div style={{ padding: 10, background: "#f0f0f0", borderBottom: "1px solid #ccc" }}>
      <h2>Редактор бота: {botId}</h2>
      <div style={{ marginTop: 10 }}>
        <button onClick={saveScenario}>💾 Сохранить</button>
        <button onClick={() => { saveScenario(); navigate("/"); }} style={{ marginLeft: 5 }}>
          ⬅ Назад к списку ботов
        </button>
        <button onClick={deleteSelectedNode} style={{ marginLeft: 5 }}>
          ❌ Удалить выбранный блок
        </button>
        <button
          onClick={() => runBot("8495785437:AAFR_fwx0AlVTcVanFMwZ7Uf5Z4t3Sk-YdA")}
          style={{ marginLeft: 5 }}
        >
          ▶️ Запустить бота
        </button>
      </div>
    </div>
  );
}

export default BotControls;
