import React, { useState, useEffect } from 'react';

const SystemSettings = () => {
  const [settings, setSettings] = useState({
    maintenanceMode: false,
    maxBotsPerUser: 5,
    maxMessagesPerMinute: 100,
    backupFrequency: 'daily'
  });

  const handleSaveSettings = () => {
    // Здесь будет реализация сохранения настроек
    alert('Settings saved successfully!');
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setSettings(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  return (
    <div style={{ padding: '20px' }}>
      <h1>System Settings</h1>
      
      <div style={{ marginBottom: '20px' }}>
        <h2>General Settings</h2>
        
        <div style={{ marginBottom: '15px' }}>
          <label>
            <input
              type="checkbox"
              name="maintenanceMode"
              checked={settings.maintenanceMode}
              onChange={handleChange}
            />
            Maintenance Mode
          </label>
        </div>
        
        <div style={{ marginBottom: '15px' }}>
          <label>
            Max Bots Per User:
            <input
              type="number"
              name="maxBotsPerUser"
              value={settings.maxBotsPerUser}
              onChange={handleChange}
              style={{ marginLeft: '10px', padding: '4px' }}
            />
          </label>
        </div>
        
        <div style={{ marginBottom: '15px' }}>
          <label>
            Max Messages Per Minute:
            <input
              type="number"
              name="maxMessagesPerMinute"
              value={settings.maxMessagesPerMinute}
              onChange={handleChange}
              style={{ marginLeft: '10px', padding: '4px' }}
            />
          </label>
        </div>
        
        <div style={{ marginBottom: '15px' }}>
          <label>
            Backup Frequency:
            <select
              name="backupFrequency"
              value={settings.backupFrequency}
              onChange={handleChange}
              style={{ marginLeft: '10px', padding: '4px' }}
            >
              <option value="hourly">Hourly</option>
              <option value="daily">Daily</option>
              <option value="weekly">Weekly</option>
              <option value="monthly">Monthly</option>
            </select>
          </label>
        </div>
      </div>
      
      <div style={{ marginBottom: '20px' }}>
        <h2>Security Settings</h2>
        
        <div style={{ marginBottom: '15px' }}>
          <label>
            <input
              type="checkbox"
              name="twoFactorAuth"
              checked={settings.twoFactorAuth || false}
              onChange={handleChange}
            />
            Require Two-Factor Authentication for Admins
          </label>
        </div>
        
        <div style={{ marginBottom: '15px' }}>
          <label>
            Password Expiry (days):
            <input
              type="number"
              name="passwordExpiry"
              value={settings.passwordExpiry || 90}
              onChange={handleChange}
              style={{ marginLeft: '10px', padding: '4px' }}
            />
          </label>
        </div>
      </div>
      
      <div style={{ marginBottom: '20px' }}>
        <h2>Performance Settings</h2>
        
        <div style={{ marginBottom: '15px' }}>
          <label>
            <input
              type="checkbox"
              name="enableCaching"
              checked={settings.enableCaching || true}
              onChange={handleChange}
            />
            Enable Caching
          </label>
        </div>
        
        <div style={{ marginBottom: '15px' }}>
          <label>
            Cache Expiry (minutes):
            <input
              type="number"
              name="cacheExpiry"
              value={settings.cacheExpiry || 60}
              onChange={handleChange}
              style={{ marginLeft: '10px', padding: '4px' }}
            />
          </label>
        </div>
      </div>
      
      <button 
        onClick={handleSaveSettings}
        style={{ padding: '10px 20px', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: '4px' }}
      >
        Save Settings
      </button>
    </div>
  );
};

export default SystemSettings;