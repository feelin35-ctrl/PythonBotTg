import React from 'react';

export const ContextMenu = ({ position, onDelete, onClose }) => {
  if (!position) return null;

  return (
    <>
      <div
        style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          zIndex: 999,
        }}
        onClick={onClose}
      />
      <div
        style={{
          position: 'fixed',
          left: position.x,
          top: position.y,
          background: 'white',
          border: '1px solid #ccc',
          borderRadius: '4px',
          boxShadow: '0 2px 10px rgba(0,0,0,0.2)',
          zIndex: 1000,
          minWidth: '120px',
        }}
      >
        <div
          style={{
            padding: '10px',
            cursor: 'pointer',
            color: '#dc3545',
            borderBottom: '1px solid #eee',
          }}
          onClick={onDelete}
        >
          🗑️ Удалить блок
        </div>
        <div
          style={{
            padding: '10px',
            cursor: 'pointer',
            color: '#6c757d',
          }}
          onClick={onClose}
        >
          ✕ Отмена
        </div>
      </div>
    </>
  );
};