import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { ReactFlowProvider } from "reactflow";
import BotList from "./BotList";
import BotEditor from "./components/BotEditor";

function App() {
  // Исправленный обработчик ошибок ResizeObserver
  React.useEffect(() => {
    const ignoreResizeObserverError = (e) => {
      if (e.message && e.message.includes && e.message.includes("ResizeObserver loop")) {
        e.stopImmediatePropagation();
      }
    };

    const ignoreUnhandledRejection = (e) => {
      if (e.reason && e.reason.message && e.reason.message.includes && e.reason.message.includes("ResizeObserver")) {
        e.preventDefault();
      }
    };

    window.addEventListener("error", ignoreResizeObserverError);
    window.addEventListener("unhandledrejection", ignoreUnhandledRejection);

    return () => {
      window.removeEventListener("error", ignoreResizeObserverError);
      window.removeEventListener("unhandledrejection", ignoreUnhandledRejection);
    };
  }, []);

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