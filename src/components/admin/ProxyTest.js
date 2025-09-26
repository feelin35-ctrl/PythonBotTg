import React, { useEffect, useState } from 'react';
import axios from 'axios';

const ProxyTest = () => {
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    const testProxy = async () => {
      try {
        // Test direct backend connection
        const directResponse = await axios.post('http://localhost:8002/api/login/', {
          username: 'testuser',
          password: 'testpass'
        });
        console.log('Direct response:', directResponse.data);
        
        // Test proxy connection
        const proxyResponse = await axios.post('/api/login/', {
          username: 'testuser',
          password: 'testpass'
        });
        console.log('Proxy response:', proxyResponse.data);
        
        setResult({
          direct: directResponse.data,
          proxy: proxyResponse.data
        });
      } catch (err) {
        console.error('Proxy test error:', err);
        setError(err.message);
      }
    };

    testProxy();
  }, []);

  return (
    <div>
      <h2>Proxy Test</h2>
      {error && <div style={{ color: 'red' }}>Error: {error}</div>}
      {result && (
        <div>
          <h3>Results:</h3>
          <pre>{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}
    </div>
  );
};

export default ProxyTest;