import React, { useRef } from 'react';
import ReactFlow, { Background, Controls } from 'reactflow';
import SidebarComponent from '../Sidebar';
import ControlPanel from '../ControlPanel';
import { EditableNode } from '../NodeTypes';
import { useBotEditor } from './useBotEditor';
import 'reactflow/dist/style.css';
import CustomBackground from '../CustomBackground';

const nodeTypes = {
  editable: EditableNode,
};

const BotEditor = () => {
  const reactFlowWrapper = useRef(null);
  const {
    initialNodes,
    edges,
    botToken,
    setBotToken,
    isBotRunning,
    loadingStatus,
    onDataChange,
    deleteNodeById,
    deleteSelectedNodes,
    deleteAllNodes,
    saveScenario,
    saveToken,
    runBot,
    restartBot,
    stopBot, // ← Новая функция остановки
    onNodesChange,
    onEdgesChange,
    onConnect,
    onDrop,
    onDragOver,
    onInit,
    undo,
    redo,
    canUndo,
    canRedo,
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
          onSaveToken={saveToken}
          onSaveScenario={saveScenario}
          onDeleteSelected={deleteSelectedNodes}
          onDeleteAll={deleteAllNodes}
          onUndo={undo}
          onRedo={redo}
          onRunBot={runBot}
          onRestartBot={restartBot}
          onStopBot={stopBot} // ← Передаем функцию остановки
          onNavigateBack={navigateBack}
          nodesCount={nodesCount}
          edgesCount={edgesCount}
          selectedCount={selectedCount}
          canUndo={canUndo}
          canRedo={canRedo}
          botId={botId}
          isBotRunning={isBotRunning} // ← Передаем статус
          loadingStatus={loadingStatus} // ← Передаем состояние загрузки
        />
      </div>
    </div>
  );
};

export default BotEditor;