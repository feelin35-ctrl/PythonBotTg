import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import api from '../../api';

const BotDetails = () => {
  const { botId } = useParams();
  const [botInfo, setBotInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchBotDetails();
  }, [botId]);

  const fetchBotDetails = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/api/bot_info/${botId}/`);
      setBotInfo(response.data);
      setError(null);
    } catch (err) {
      console.error('Error fetching bot details:', err);
      setError('Failed to load bot details');
    } finally {
      setLoading(false);
    }
  };

  const handleStartBot = async () => {
    try {
      await api.post(`/api/run_bot/${botId}/`, {
        token: '' // Токен будет взят из переменных окружения или файла
      });
      // Обновляем информацию о боте
      fetchBotDetails();
    } catch (err) {
      console.error('Error starting bot:', err);
      alert('Failed to start bot');
    }
  };

  const handleStopBot = async () => {
    try {
      await api.get(`/api/stop_bot/${botId}/`);
      // Обновляем информацию о боте
      fetchBotDetails();
    } catch (err) {
      console.error('Error stopping bot:', err);
      alert('Failed to stop bot');
    }
  };

  const handleDeleteBot = async () => {
    if (window.confirm(`Are you sure you want to delete bot ${botId}?`)) {
      try {
        await api.delete(`/api/delete_bot/${botId}/`);
        alert(`Bot ${botId} deleted successfully`);
        // Здесь можно добавить навигацию назад к списку ботов
      } catch (err) {
        console.error('Error deleting bot:', err);
        alert('Failed to delete bot');
      }
    }
  };

  if (loading) {
    return <div>Loading bot details...</div>;
  }

  if (error) {
    return <div>Error: {error}</div>;
  }

  if (!botInfo) {
    return <div>No bot information available</div>;
  }

  return (
    <div style={{ padding: '20px' }}>
      <h1>Bot Details: {botId}</h1>
      
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: '1fr 1fr', 
        gap: '20px', 
        marginBottom: '20px' 
      }}>
        <div style={{ 
          border: '1px solid #ddd', 
          padding: '15px', 
          borderRadius: '4px' 
        }}>
          <h2>Bot Information</h2>
          <p><strong>ID:</strong> {botInfo.bot_id}</p>
          <p><strong>Has Token:</strong> {botInfo.has_token ? 'Yes' : 'No'}</p>
          <p><strong>Nodes Count:</strong> {botInfo.nodes_count}</p>
          <p><strong>Edges Count:</strong> {botInfo.edges_count}</p>
          <p><strong>Is Running:</strong> {botInfo.is_running ? 'Yes' : 'No'}</p>
        </div>
        
        <div style={{ 
          border: '1px solid #ddd', 
          padding: '15px', 
          borderRadius: '4px' 
        }}>
          <h2>Node Statistics</h2>
          {Object.entries(botInfo.node_stats).map(([nodeType, count]) => (
            <p key={nodeType}><strong>{nodeType}:</strong> {count}</p>
          ))}
        </div>
      </div>
      
      <div style={{ marginBottom: '20px' }}>
        <h2>Actions</h2>
        <button 
          onClick={handleStartBot}
          style={{ 
            marginRight: '10px', 
            padding: '8px 16px', 
            backgroundColor: '#28a745', 
            color: 'white', 
            border: 'none', 
            borderRadius: '4px' 
          }}
          disabled={botInfo.is_running}
        >
          Start Bot
        </button>
        
        <button 
          onClick={handleStopBot}
          style={{ 
            marginRight: '10px', 
            padding: '8px 16px', 
            backgroundColor: '#ffc107', 
            color: 'black', 
            border: 'none', 
            borderRadius: '4px' 
          }}
          disabled={!botInfo.is_running}
        >
          Stop Bot
        </button>
        
        <button 
          onClick={handleDeleteBot}
          style={{ 
            padding: '8px 16px', 
            backgroundColor: '#dc3545', 
            color: 'white', 
            border: 'none', 
            borderRadius: '4px' 
          }}
        >
          Delete Bot
        </button>
      </div>
      
      <div>
        <h2>Bot Configuration</h2>
        <textarea
          value={JSON.stringify(botInfo, null, 2)}
          readOnly
          style={{ 
            width: '100%', 
            height: '300px', 
            fontFamily: 'monospace',
            padding: '10px'
          }}
        />
      </div>
    </div>
  );
};

export default BotDetails;