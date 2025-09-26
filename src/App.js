import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { ReactFlowProvider } from "reactflow";
import BotList from "./BotList";
import BotEditor from "./components/BotEditor";
import { useResizeObserverErrorHandler } from "./hooks/useResizeObserverErrorHandler";

// Import authentication components
import Login from "./components/Auth/Login";
import Register from "./components/Auth/Register";
import ProtectedRoute from "./components/Auth/ProtectedRoute";
import TestAuth from "./components/Auth/TestAuth";
import TestUserContext from "./components/Auth/TestUserContext";
import { AuthProvider } from "./components/Auth/AuthContext";

// Import super admin components
import SuperAdminLogin from "./components/admin/SuperAdminLogin";
import SuperAdminLayout from "./components/admin/SuperAdminLayout";
import SuperAdminDashboard from "./components/admin/SuperAdminDashboard";

// Import proxy test component
import ProxyTest from "./components/admin/ProxyTest";

function App() {
  // Use improved ResizeObserver error handler
  useResizeObserverErrorHandler();

  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/test-auth" element={<TestAuth />} />
          <Route path="/test-user-context" element={<TestUserContext />} />
          <Route path="/proxy-test" element={<ProxyTest />} />
          
          {/* Super Admin Routes */}
          <Route path="/superadmin/login" element={<SuperAdminLogin />} />
          <Route path="/superadmin/*" element={<SuperAdminLayout />} />
          
          <Route path="/" element={<ProtectedRoute><BotList /></ProtectedRoute>} />
          <Route
            path="/editor/:botId"
            element={
              <ProtectedRoute>
                <ReactFlowProvider>
                  <BotEditor />
                </ReactFlowProvider>
              </ProtectedRoute>
            }
          />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;