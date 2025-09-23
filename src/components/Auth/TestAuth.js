import React from 'react';
import Login from './Login';
import Register from './Register';

const TestAuth = () => {
  return (
    <div>
      <h1>Тест аутентификации</h1>
      <div style={{ marginBottom: '2rem' }}>
        <h2>Форма входа</h2>
        <Login />
      </div>
      <div>
        <h2>Форма регистрации</h2>
        <Register />
      </div>
    </div>
  );
};

export default TestAuth;