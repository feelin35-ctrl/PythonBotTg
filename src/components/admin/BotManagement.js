import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../Auth/AuthContext';
import api from '../../api';

const BotManagement = () => {
  const { user } = useAuth();
  console.log('BotManagement - current user:', user);
  const [bots, setBots] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const fetchBots = useCallback(async () => {
    try {
      setLoading(true);
      // Используем ID текущего пользователя вместо жестко закодированного '9'
      const userId = user?.id || '9'; // Fallback to '9' if user ID is not available
      const response = await api.get('/api/get_bots/', {
        params: { user_id: userId }
      });
      
      // The API returns an array directly, not an object with a bots property
      setBots(response.data || []);
      setError(null);
    } catch (err) {
      console.error('Error fetching bots:', err);
      setError('Failed to load bots');
    } finally {
      setLoading(false);
    }
  }, [user]);

  useEffect(() => {
    fetchBots();
  }, [fetchBots]);

  const handleViewDetails = (botId) => {
    // Переходим к странице деталей бота
    navigate(`/superadmin/bots/${botId}`);
  };

  const handleDeleteBot = async (botId) => {
    if (window.confirm(`Are you sure you want to delete bot ${botId}?`)) {
      try {
        // Передаем ID текущего пользователя в параметрах запроса
        const params = user ? { deleted_by_user_id: user.id } : {};
        console.log('Deleting bot with params:', { botId, params, user });
        await api.delete(`/api/delete_bot/${botId}/`, { params });
        // Обновляем список ботов
        fetchBots();
      } catch (err) {
        console.error('Error deleting bot:', err);
        alert('Failed to delete bot');
      }
    }
  };

  const handleStartBot = async (botId) => {
    try {
      // Здесь должна быть реализация запуска бота
      alert(`Starting bot: ${botId}`);
    } catch (err) {
      console.error('Error starting bot:', err);
      alert('Failed to start bot');
    }
  };

  const handleStopBot = async (botId) => {
    try {
      // Здесь должна быть реализация остановки бота
      alert(`Stopping bot: ${botId}`);
    } catch (err) {
      console.error('Error stopping bot:', err);
      alert('Failed to stop bot');
    }
  };

  const handleEditBot = (botId) => {
    // Переходим к редактору сценариев
    navigate(`/editor/${botId}`);
  };

  if (loading) {
    return <div>Loading bots...</div>;
  }

  if (error) {
    return <div>Error: {error}</div>;
  }

  return (
    <div style={{ padding: '20px' }}>
      <h1>Bot Management</h1>
      
      <div style={{ marginBottom: '20px' }}>
        <button 
          onClick={() => navigate('/superadmin/bots/create')}
          style={{ padding: '8px 16px', backgroundColor: '#28a745', color: 'white', border: 'none', borderRadius: '4px' }}
        >
          Create New Bot
        </button>
      </div>
      
      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead>
          <tr>
            <th style={{ border: '1px solid #ddd', padding: '8px', backgroundColor: '#f5f5f5' }}>Bot ID</th>
            <th style={{ border: '1px solid #ddd', padding: '8px', backgroundColor: '#f5f5f5' }}>Actions</th>
          </tr>
        </thead>
        <tbody>
          {bots.map(botId => (
            <tr key={botId}>
              <td style={{ border: '1px solid #ddd', padding: '8px' }}>{botId}</td>
              <td style={{ border: '1px solid #ddd', padding: '8px' }}>
                <button 
                  onClick={() => handleEditBot(botId)}
                  style={{ marginRight: '5px', padding: '4px 8px', backgroundColor: '#007bff', color: 'white', border: 'none' }}
                >
                  Edit
                </button>
                <button 
                  onClick={() => handleViewDetails(botId)}
                  style={{ marginRight: '5px', padding: '4px 8px' }}
                >
                  View Details
                </button>
                <button 
                  onClick={() => handleStartBot(botId)}
                  style={{ marginRight: '5px', padding: '4px 8px', backgroundColor: '#28a745', color: 'white', border: 'none' }}
                >
                  Start
                </button>
                <button 
                  onClick={() => handleStopBot(botId)}
                  style={{ marginRight: '5px', padding: '4px 8px', backgroundColor: '#ffc107', color: 'black', border: 'none' }}
                >
                  Stop
                </button>
                <button 
                  onClick={() => handleDeleteBot(botId)}
                  style={{ padding: '4px 8px', backgroundColor: '#dc3545', color: 'white', border: 'none' }}
                >
                  Delete
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default BotManagement;