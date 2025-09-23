import React from 'react';
import { Routes, Route } from 'react-router-dom';
import SuperAdminNavigation from './SuperAdminNavigation';
import SuperAdminDashboard from './SuperAdminDashboard';
import UserManagement from './UserManagement';
import BotManagement from './BotManagement';
import SystemSettings from './SystemSettings';
import BotDetails from './BotDetails';
import CreateBot from './CreateBot';

const SuperAdminLayout = () => {
  return (
    <div>
      <SuperAdminNavigation />
      <Routes>
        <Route path="/" element={<SuperAdminDashboard />} />
        <Route path="/users" element={<UserManagement />} />
        <Route path="/bots" element={<BotManagement />} />
        <Route path="/bots/:botId" element={<BotDetails />} />
        <Route path="/bots/create" element={<CreateBot />} />
        <Route path="/settings" element={<SystemSettings />} />
      </Routes>
    </div>
  );
};

export default SuperAdminLayout;