import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../Auth/AuthContext';
import api from '../../api';

const UserManagement = () => {
  const { user } = useAuth();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [editingUser, setEditingUser] = useState(null);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    role: 'user'
  });

  const fetchUsers = useCallback(async () => {
    try {
      setLoading(true);
      // Используем ID текущего пользователя вместо жестко закодированного '9'
      const userId = user?.id || '9'; // Fallback to '9' if user ID is not available
      const response = await api.get('/api/get_all_users/', {
        params: { user_id: userId }
      });
      
      // The API returns an array directly, not an object with a users property
      setUsers(response.data || []);
      setError(null);
    } catch (err) {
      console.error('Error fetching users:', err);
      setError('Failed to load users');
    } finally {
      setLoading(false);
    }
  }, [user]);

  useEffect(() => {
    fetchUsers();
  }, [fetchUsers]); // Теперь fetchUsers мемоизирован и безопасен для использования в зависимостях

  const handleEdit = (user) => {
    setEditingUser(user.id);
    setFormData({
      username: user.username,
      email: user.email,
      role: user.role
    });
  };

  const handleCancelEdit = () => {
    setEditingUser(null);
    setFormData({
      username: '',
      email: '',
      role: 'user'
    });
  };

  const handleSave = async () => {
    try {
      // Используем ID текущего пользователя вместо жестко закодированного '9'
      const currentUserId = user?.id || '9'; // Fallback to '9' if user ID is not available
      await api.post('/api/update_user_role/', null, {
        params: {
          user_id: editingUser,
          new_role: formData.role,
          updated_by_user_id: currentUserId
        }
      });
      
      // Обновляем список пользователей
      fetchUsers();
      handleCancelEdit();
    } catch (err) {
      console.error('Error updating user:', err);
      alert('Failed to update user');
    }
  };

  const handleDelete = async (userId) => {
    if (window.confirm('Are you sure you want to delete this user?')) {
      try {
        // Используем ID текущего пользователя вместо жестко закодированного '9'
        const currentUserId = user?.id || '9'; // Fallback to '9' if user ID is not available
        // Отправляем запрос на удаление пользователя
        await api.delete(`/api/user/${userId}/`, {
          params: {
            deleted_by_user_id: currentUserId
          }
        });
        
        // Обновляем список пользователей после удаления
        fetchUsers();
        alert('User deleted successfully');
      } catch (err) {
        console.error('Error deleting user:', err);
        alert('Failed to delete user');
      }
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  if (loading) {
    return <div>Loading users...</div>;
  }

  if (error) {
    return <div>Error: {error}</div>;
  }

  return (
    <div style={{ padding: '20px' }}>
      <h1>User Management</h1>
      
      <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '20px' }}>
        <thead>
          <tr>
            <th style={{ border: '1px solid #ddd', padding: '8px', backgroundColor: '#f5f5f5' }}>ID</th>
            <th style={{ border: '1px solid #ddd', padding: '8px', backgroundColor: '#f5f5f5' }}>Username</th>
            <th style={{ border: '1px solid #ddd', padding: '8px', backgroundColor: '#f5f5f5' }}>Email</th>
            <th style={{ border: '1px solid #ddd', padding: '8px', backgroundColor: '#f5f5f5' }}>Role</th>
            <th style={{ border: '1px solid #ddd', padding: '8px', backgroundColor: '#f5f5f5' }}>Actions</th>
          </tr>
        </thead>
        <tbody>
          {users.map(user => (
            <tr key={user.id}>
              {editingUser === user.id ? (
                <>
                  <td style={{ border: '1px solid #ddd', padding: '8px' }}>{user.id}</td>
                  <td style={{ border: '1px solid #ddd', padding: '8px' }}>
                    <input
                      type="text"
                      name="username"
                      value={formData.username}
                      onChange={handleChange}
                      style={{ width: '100%', padding: '4px' }}
                      disabled
                    />
                  </td>
                  <td style={{ border: '1px solid #ddd', padding: '8px' }}>
                    <input
                      type="email"
                      name="email"
                      value={formData.email}
                      onChange={handleChange}
                      style={{ width: '100%', padding: '4px' }}
                      disabled
                    />
                  </td>
                  <td style={{ border: '1px solid #ddd', padding: '8px' }}>
                    <select
                      name="role"
                      value={formData.role}
                      onChange={handleChange}
                      style={{ width: '100%', padding: '4px' }}
                    >
                      <option value="user">User</option>
                      <option value="admin">Admin</option>
                      <option value="super_admin">Super Admin</option>
                    </select>
                  </td>
                  <td style={{ border: '1px solid #ddd', padding: '8px' }}>
                    <button 
                      onClick={handleSave}
                      style={{ marginRight: '5px', padding: '4px 8px' }}
                    >
                      Save
                    </button>
                    <button 
                      onClick={handleCancelEdit}
                      style={{ padding: '4px 8px' }}
                    >
                      Cancel
                    </button>
                  </td>
                </>
              ) : (
                <>
                  <td style={{ border: '1px solid #ddd', padding: '8px' }}>{user.id}</td>
                  <td style={{ border: '1px solid #ddd', padding: '8px' }}>{user.username}</td>
                  <td style={{ border: '1px solid #ddd', padding: '8px' }}>{user.email}</td>
                  <td style={{ border: '1px solid #ddd', padding: '8px' }}>{user.role}</td>
                  <td style={{ border: '1px solid #ddd', padding: '8px' }}>
                    <button 
                      onClick={() => handleEdit(user)}
                      style={{ marginRight: '5px', padding: '4px 8px' }}
                    >
                      Edit
                    </button>
                    <button 
                      onClick={() => handleDelete(user.id)}
                      style={{ padding: '4px 8px', backgroundColor: '#dc3545', color: 'white', border: 'none' }}
                    >
                      Delete
                    </button>
                  </td>
                </>
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default UserManagement;