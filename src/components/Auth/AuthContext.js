import React, { createContext, useState, useContext, useEffect } from 'react';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  console.log('useAuth returned context:', context); // Добавляем логирование
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is already logged in
    const storedUser = localStorage.getItem('user');
    console.log('AuthProvider - storedUser from localStorage:', storedUser); // Добавляем логирование
    if (storedUser) {
      try {
        const parsedUser = JSON.parse(storedUser);
        console.log('AuthProvider - parsed user:', parsedUser); // Добавляем логирование
        // Проверяем, есть ли у пользователя ID
        if (parsedUser && parsedUser.id) {
          console.log('AuthProvider - user ID found:', parsedUser.id);
        } else {
          console.log('AuthProvider - no user ID found in stored data');
        }
        setUser(parsedUser);
      } catch (error) {
        console.error('Error parsing stored user:', error);
        localStorage.removeItem('user');
      }
    }
    setLoading(false);
  }, []);

  const login = (userData) => {
    console.log('AuthProvider - login called with userData:', userData); // Добавляем логирование
    // Проверяем, есть ли у пользователя ID
    if (userData && userData.id) {
      console.log('AuthProvider - user ID in login data:', userData.id);
    } else {
      console.log('AuthProvider - no user ID in login data');
    }
    setUser(userData);
    localStorage.setItem('user', JSON.stringify(userData));
  };

  const logout = () => {
    console.log('AuthProvider - logout called'); // Добавляем логирование
    setUser(null);
    localStorage.removeItem('user');
  };

  const value = {
    user,
    login,
    logout,
    loading
  };

  console.log('AuthProvider - providing value:', value); // Добавляем логирование
  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
};