import React from 'react';

const DebugEnv = () => {
  // В браузере переменные окружения доступны через process.env
  const apiUrl = process.env.REACT_APP_API_URL;
  
  return (
    <div style={{ padding: '20px' }}>
      <h1>Environment Variables Debug</h1>
      <p>REACT_APP_API_URL: {apiUrl || 'Not set'}</p>
      <p>Expected value: http://localhost:8002</p>
    </div>
  );
};

export default DebugEnv;