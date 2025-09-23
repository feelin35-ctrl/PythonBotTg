import React, { useState, useEffect } from 'react';
import { useAuth } from './AuthContext';
import { getApiBaseUrl } from '../../utils/apiHelper';

const TestUserContext = () => {
  const { user, login, logout } = useAuth();
  const [testResult, setTestResult] = useState('');

  useEffect(() => {
    // Log user data when component mounts
    console.log('TestUserContext - Current user:', user);
    setTestResult(`Current user: ${JSON.stringify(user, null, 2)}`);
  }, [user]);

  const testLogin = async () => {
    try {
      const API_BASE_URL = getApiBaseUrl();
      // Simulate API login
      const response = await fetch(`${API_BASE_URL}/api/login/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username: 'Feelin',
          password: 'newpassword'
        })
      });
      
      const data = await response.json();
      console.log('TestUserContext - API response:', data);
      
      if (data.status === 'success') {
        console.log('TestUserContext - Testing login with:', data.user);
        login(data.user);
      }
    } catch (error) {
      console.error('TestUserContext - Login error:', error);
    }
  };

  const checkLocalStorage = () => {
    const storedUser = localStorage.getItem('user');
    console.log('TestUserContext - localStorage user:', storedUser);
    setTestResult(`localStorage user: ${storedUser}`);
  };

  return (
    <div style={{ padding: '20px', border: '1px solid #ccc', margin: '10px' }}>
      <h3>Test User Context</h3>
      <pre>{testResult}</pre>
      <button onClick={testLogin}>Test Login</button>
      <button onClick={checkLocalStorage} style={{ marginLeft: '10px' }}>Check LocalStorage</button>
      <button onClick={logout} style={{ marginLeft: '10px' }}>Logout</button>
    </div>
  );
};

export default TestUserContext;