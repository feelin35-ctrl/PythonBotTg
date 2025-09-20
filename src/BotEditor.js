import React, { useState, useEffect, useCallback, useRef } from 'react';
import ReactFlow, {
  Controls,
  Background,
  addEdge,
  useNodesState,
  useEdgesState,
  MiniMap,
  Panel,
} from 'reactflow';
import 'reactflow/dist/style.css';
import styled from 'styled-components';
import { nodeTypes } from './components/NodeTypes';
import Sidebar from './components/Sidebar';
import ControlPanel from './components/ControlPanel';
import { useBotEditor } from './components/BotEditor/useBotEditor';

// Добавляем отладочный вывод
console.log('Imported nodeTypes:', nodeTypes);

const EditorContainer = styled.div`
  display: flex;
  height: 100vh;
  overflow: hidden;
  
  @media (max-width: 768px) {
    flex-direction: column;
  }
`;

const FlowContainer = styled.div`
  flex: 1;
  height: 100%;
  
  @media (max-width: 768px) {
    height: calc(100vh - 200px);
  }
`;

const MobileSidebar = styled.div`
  display: none;
  
  @media (max-width: 768px) {
    display: block;
    height: 200px;
    overflow-y: auto;
    border-top: 1px solid #ccc;
    background: #f0f0f0;
    padding: 10px;
  }
`;

const BotEditor = ({ botId }) => {
  const {
    nodes,
    edges,
    setNodes,
    setEdges,
    onNodesChange,
    onEdgesChange,
    onSave,
    onLoad,
    onAddNode,
    onDeleteNode,
  } = useBotEditor(botId);

  const reactFlowWrapper = useRef(null);
  const [reactFlowInstance, setReactFlowInstance] = useState(null);
  const [isMobile, setIsMobile] = useState(window.innerWidth <= 768);

  // Отслеживаем изменение размера экрана
  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth <= 768);
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Добавляем отладочный вывод
  console.log('Current nodes:', nodes);
  console.log('Current edges:', edges);

  const onConnect = useCallback(
    (params) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  const onDragOver = useCallback((event) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  }, []);

  const onDrop = useCallback(
    (event) => {
      event.preventDefault();

      const type = event.dataTransfer.getData('application/reactflow');

      // Проверяем, что тип узла поддерживается
      console.log('Dropped node type:', type);
      console.log('Available node types:', nodeTypes);
      if (!type || !nodeTypes[type]) {
        console.log('Unsupported node type:', type);
        return;
      }

      const position = reactFlowInstance.screenToFlowPosition({
        x: event.clientX,
        y: event.clientY,
      });

      onAddNode(type, position);
    },
    [reactFlowInstance, onAddNode]
  );

  return (
    <EditorContainer>
      {/* Отображаем боковую панель слева на десктопе и снизу на мобильных устройствах */}
      {!isMobile && <Sidebar />}
      
      <FlowContainer ref={reactFlowWrapper}>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onInit={setReactFlowInstance}
          onDrop={onDrop}
          onDragOver={onDragOver}
          fitView
          nodeTypes={nodeTypes}
          connectionLineStyle={{ stroke: '#ddd', strokeWidth: 2 }}
          connectionLineType="bezier"
        >
          <Controls />
          <MiniMap />
          <Background variant="dots" gap={12} size={1} />
          <Panel position="top-right">
            <ControlPanel 
              botToken={botToken}
              setBotToken={setBotToken}
              botName={botName}
              setBotName={setBotName}
              onSaveToken={saveToken}
              onSaveBotName={saveBotName}
              onSaveScenario={saveScenario}
              onDeleteSelected={deleteSelectedNodes}
              onDeleteAll={deleteAllNodes}
              onRunBot={() => runBot(botToken)}
              onRestartBot={restartBot}
              onStopBot={stopBot}
              onNavigateBack={() => navigate('/')}
              nodesCount={initialNodes.length}
              edgesCount={edges.length}
              selectedCount={initialNodes.filter(n => n.selected).length}
              botId={botId}
              isBotRunning={isBotRunning}
              loadingStatus={loadingStatus}
            />
          </Panel>
        </ReactFlow>
      </FlowContainer>
      
      {/* На мобильных устройствах отображаем боковую панель внизу */}
      {isMobile && (
        <MobileSidebar>
          <h4>Доступные блоки:</h4>
          <Sidebar />
        </MobileSidebar>
      )}
    </EditorContainer>
  );
};

export default BotEditor;