import React, { useRef } from 'react';
import ReactFlow, { Background, Controls } from 'reactflow';
import SidebarComponent from '../Sidebar';
import ControlPanel from '../ControlPanel';
import { EditableNode } from '../NodeTypes';
import { nodeTypes as registeredNodeTypes } from '../NodeTypes/index';
import { useBotEditor } from './useBotEditor';
import 'reactflow/dist/style.css';
import CustomBackground from '../CustomBackground';

const nodeTypes = {
  editable: EditableNode,
  ...registeredNodeTypes
};

const BotEditor = () => {
  const reactFlowWrapper = useRef(null);
  const {
    initialNodes,
    edges,
    botToken,
    setBotToken,
    botName, // Получаем имя бота
    setBotName, // Получаем функцию для установки имени бота
    isBotRunning,
    loadingStatus,
    onDataChange,
    deleteNodeById,
    deleteSelectedNodes,
    deleteAllNodes,
    saveScenario,
    saveToken,
    saveBotName, // Получаем функцию сохранения имени бота
    runBot,
    restartBot,
    stopBot, // ← Новая функция остановки
    onNodesChange,
    onEdgesChange,
    onConnect,
    onDrop,
    onDragOver,
    onInit,
    navigateBack,
    nodesCount,
    edgesCount,
    selectedCount,
    botId
  } = useBotEditor();

  return (
    <div style={{ display: "flex", height: "100vh" }}>
      <SidebarComponent />
      <div
        ref={reactFlowWrapper}
        style={{
          flexGrow: 1,
          position: "relative",
          background: '#f0f0f0'
        }}
        onDrop={onDrop}
        onDragOver={onDragOver}
      >
        <ReactFlow
          nodes={initialNodes}
          edges={edges}
          nodeTypes={nodeTypes}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onInit={onInit}
          fitView
          deleteKeyCode={"Delete"}
        >
          <CustomBackground/>
          <Controls />
        </ReactFlow>

        <ControlPanel
          botToken={botToken}
          setBotToken={setBotToken}
          botName={botName} // Передаем имя бота
          setBotName={setBotName} // Передаем функцию для установки имени бота
          onSaveToken={saveToken}
          onSaveBotName={saveBotName} // Передаем функцию сохранения имени бота
          onSaveScenario={saveScenario}
          onDeleteSelected={deleteSelectedNodes}
          onDeleteAll={deleteAllNodes}
          onRunBot={runBot}
          onRestartBot={restartBot}
          onStopBot={stopBot} // ← Передаем функцию остановки
          onNavigateBack={navigateBack}
          nodesCount={nodesCount}
          edgesCount={edgesCount}
          selectedCount={selectedCount}
          botId={botId}
          isBotRunning={isBotRunning} // ← Передаем статус
          loadingStatus={loadingStatus} // ← Передаем состояние загрузки
        />
      </div>
    </div>
  );
};

export default BotEditor;