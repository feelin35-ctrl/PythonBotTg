import React, { useState } from 'react';
import axios from 'axios';

const ProxyTest = () => {
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const testProxy = async () => {
    setLoading(true);
    setError(null);
    setResponse(null);
    
    try {
      // Проверяем прямое подключение к бэкенду
      const directResponse = await fetch('http://localhost:8002/api/login/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username: 'superadmin',
          password: 'admin123'
        })
      });
      
      const directData = await directResponse.json();
      console.log('Direct connection response:', directData);
      
      // Проверяем подключение через прокси
      const proxyResponse = await axios.post('/api/login/', {
        username: 'superadmin',
        password: 'admin123'
      });
      
      setResponse({
        direct: directData,
        proxy: proxyResponse.data
      });
    } catch (err) {
      console.error('Proxy test error:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '20px' }}>
      <h1>Proxy Test</h1>
      <button onClick={testProxy} disabled={loading}>
        {loading ? 'Testing...' : 'Test Proxy Connection'}
      </button>
      
      {error && (
        <div style={{ 
          backgroundColor: '#f8d7da', 
          color: '#721c24', 
          padding: '10px', 
          borderRadius: '4px', 
          marginTop: '20px'
        }}>
          <h2>Error:</h2>
          <pre>{error}</pre>
        </div>
      )}
      
      {response && (
        <div style={{ 
          backgroundColor: '#d4edda', 
          color: '#155724', 
          padding: '10px', 
          borderRadius: '4px', 
          marginTop: '20px'
        }}>
          <h2>Success:</h2>
          <h3>Direct Connection:</h3>
          <pre>{JSON.stringify(response.direct, null, 2)}</pre>
          <h3>Proxy Connection:</h3>
          <pre>{JSON.stringify(response.proxy, null, 2)}</pre>
        </div>
      )}
    </div>
  );
};

export default ProxyTest;