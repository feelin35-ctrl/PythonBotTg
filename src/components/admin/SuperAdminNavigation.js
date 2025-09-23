import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';

const SuperAdminNavigation = () => {
  const [currentUser, setCurrentUser] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    // Получаем информацию о текущем пользователе из localStorage
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      try {
        const user = JSON.parse(storedUser);
        setCurrentUser(user);
      } catch (error) {
        console.error('Error parsing user data:', error);
      }
    }
  }, []);

  const handleLogout = () => {
    // Удаляем информацию о пользователе из localStorage
    localStorage.removeItem('user');
    // Перенаправляем на страницу логина
    navigate('/superadmin/login');
  };

  const navItems = [
    { name: 'Dashboard', path: '/superadmin' },
    { name: 'User Management', path: '/superadmin/users' },
    { name: 'Bot Management', path: '/superadmin/bots' },
    { name: 'System Settings', path: '/superadmin/settings' }
  ];

  return (
    <nav style={{ 
      backgroundColor: '#333', 
      padding: '10px',
      marginBottom: '20px'
    }}>
      <ul style={{ 
        listStyleType: 'none', 
        margin: 0, 
        padding: 0,
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <div style={{ display: 'flex' }}>
          {navItems.map((item, index) => (
            <li key={index} style={{ marginRight: '20px' }}>
              <Link 
                to={item.path} 
                style={{ 
                  color: 'white', 
                  textDecoration: 'none',
                  padding: '8px 16px',
                  borderRadius: '4px',
                  transition: 'background-color 0.3s'
                }}
                onMouseOver={(e) => e.target.style.backgroundColor = '#555'}
                onMouseOut={(e) => e.target.style.backgroundColor = 'transparent'}
              >
                {item.name}
              </Link>
            </li>
          ))}
        </div>
        
        <div style={{ display: 'flex', alignItems: 'center', color: 'white' }}>
          {currentUser && (
            <span style={{ marginRight: '20px' }}>
              Welcome, {currentUser.username}!
            </span>
          )}
          <button 
            onClick={handleLogout}
            style={{
              backgroundColor: '#dc3545',
              color: 'white',
              border: 'none',
              padding: '8px 16px',
              borderRadius: '4px',
              cursor: 'pointer',
              transition: 'background-color 0.3s'
            }}
            onMouseOver={(e) => e.target.style.backgroundColor = '#c82333'}
            onMouseOut={(e) => e.target.style.backgroundColor = '#dc3545'}
          >
            Logout
          </button>
        </div>
      </ul>
    </nav>
  );
};

export default SuperAdminNavigation;