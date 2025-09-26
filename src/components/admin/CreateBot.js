import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../Auth/AuthContext';
import api from '../../api';

const CreateBot = () => {
  const { user } = useAuth();
  const [botId, setBotId] = useState('');
  const [botToken, setBotToken] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      // Use a more robust way to get user ID
      if (!user || !user.id) {
        setError("User is not authenticated. Please log in again.");
        setLoading(false);
        return;
      }
      const userId = user.id;
      
      // 1. Create the bot
      await api.post('/api/create_bot/', null, {
        params: {
          bot_id: botId,
          user_id: userId
        }
      });

      // 2. Save the bot token to the database if provided
      if (botToken) {
        try {
          // Use the new, correct endpoint
          await api.post(`/api/users/${userId}/bots/${botId}/token`, {
            token: botToken
          });
          console.log("Токен успешно сохранен в базе данных");
        } catch (tokenError) {
          console.error('Error saving token to database:', tokenError);
          // In case of an error, save to localStorage as a backup
          localStorage.setItem(`botToken_${botId}`, botToken);
          console.log("Токен сохранен локально (резервный вариант)");
          // Optionally, inform the user that the token was saved locally
          // setError("Bot created, but failed to save token to the database. It has been saved locally.");
        }
      }

      // 3. Create initial scenario for the new bot
      const initialScenario = {
        nodes: [
          {
            id: "1",
            type: "start",
            data: {
              blockType: "start",
              label: "Добро пожаловать! Бот работает."
            },
            position: { x: 250, y: 100 }
          },
          {
            id: "2",
            type: "message",
            data: {
              blockType: "message",
              label: "Это тестовое сообщение от вашего бота!"
            },
            position: { x: 250, y: 200 }
          }
        ],
        edges: [
          {
            source: "1",
            target: "2"
          }
        ]
      };

      // 4. Save the initial scenario, passing user_id
      await api.post(`/api/save_scenario/${botId}/`, initialScenario, {
        params: { user_id: userId }
      });
      
      // 5. Navigate to the bot editor
      navigate(`/editor/${botId}`);

    } catch (err) {
      console.error('Error creating bot:', err);
      const errorMessage = err.response?.data?.detail || err.response?.data?.message || 'Failed to create bot. Please check the console for details.';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '20px' }}>
      <h1>Create New Bot</h1>
      
      {error && (
        <div style={{ 
          backgroundColor: '#f8d7da', 
          color: '#721c24', 
          padding: '10px', 
          borderRadius: '4px', 
          marginBottom: '20px'
        }}>
          {error}
        </div>
      )}
      
      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: '20px' }}>
          <label htmlFor="botId" style={{ display: 'block', marginBottom: '5px' }}>
            Bot ID
          </label>
          <input
            id="botId"
            type="text"
            value={botId}
            onChange={(e) => setBotId(e.target.value)}
            required
            style={{ 
              width: '100%', 
              maxWidth: '400px',
              padding: '10px', 
              border: '1px solid #ddd', 
              borderRadius: '4px',
              boxSizing: 'border-box'
            }}
            placeholder="Enter unique bot identifier"
          />
          <p style={{ 
            marginTop: '5px', 
            fontSize: '14px', 
            color: '#666' 
          }}>
            The bot ID should be unique and will be used to identify your bot in the system.
          </p>
        </div>
        
        <div style={{ marginBottom: '20px' }}>
          <label htmlFor="botToken" style={{ display: 'block', marginBottom: '5px' }}>
            Bot Token (optional)
          </label>
          <input
            id="botToken"
            type="password"
            value={botToken}
            onChange={(e) => setBotToken(e.target.value)}
            style={{ 
              width: '100%', 
              maxWidth: '400px',
              padding: '10px', 
              border: '1px solid #ddd', 
              borderRadius: '4px',
              boxSizing: 'border-box'
            }}
            placeholder="Enter bot token from @BotFather"
          />
          <p style={{ 
            marginTop: '5px', 
            fontSize: '14px', 
            color: '#666' 
          }}>
            The bot token from @BotFather. You can add it later in the editor.
          </p>
        </div>
        
        <button 
          type="submit" 
          disabled={loading || !botId.trim()}
          style={{ 
            padding: '12px 24px', 
            backgroundColor: '#007bff', 
            color: 'white', 
            border: 'none', 
            borderRadius: '4px',
            cursor: loading || !botId.trim() ? 'not-allowed' : 'pointer',
            opacity: loading || !botId.trim() ? 0.7 : 1
          }}
        >
          {loading ? 'Creating...' : 'Create Bot'}
        </button>
        
        <button 
          type="button"
          onClick={() => navigate('/superadmin/bots')}
          style={{ 
            marginLeft: '10px',
            padding: '12px 24px', 
            backgroundColor: '#6c757d', 
            color: 'white', 
            border: 'none', 
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          Cancel
        </button>
      </form>
    </div>
  );
};

export default CreateBot;
