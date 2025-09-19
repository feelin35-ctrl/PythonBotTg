import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { ReactFlowProvider } from "reactflow";
import BotList from "./BotList";
import BotEditor from "./components/BotEditor";
import { useResizeObserverErrorHandler } from "./hooks/useResizeObserverErrorHandler";

function App() {
  // Use improved ResizeObserver error handler
  useResizeObserverErrorHandler();

  return (
    <Router>
      <Routes>
        <Route path="/" element={<BotList />} />
        <Route
          path="/editor/:botId"
          element={
            <ReactFlowProvider>
              <BotEditor />
            </ReactFlowProvider>
          }
        />
      </Routes>
    </Router>
  );
}

export default App;