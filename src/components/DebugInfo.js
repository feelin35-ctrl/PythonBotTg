// src/components/DebugInfo.js
import React from 'react';

export const DebugInfo = ({ nodes, edges }) => {
  return (
    <div style={{
      position: 'absolute',
      bottom: 10,
      right: 10,
      background: 'rgba(255,255,255,0.9)',
      padding: 10,
      borderRadius: 5,
      fontSize: 12,
      zIndex: 1000,
      boxShadow: '0 2px 5px rgba(0,0,0,0.2)'
    }}>
      <div>Nodes: {nodes.length}</div>
      <div>Edges: {edges.length}</div>
      <div>Selected: {nodes.filter(n => n.selected).length}</div>
      
      {/* Адаптивное отображение на мобильных устройствах */}
      <style>
        {`
          @media (max-width: 768px) {
            div[style*="position: 'absolute'"] {
              bottom: 60px;
              left: 10px;
              right: 10px;
              font-size: 10px;
              padding: 8px;
            }
          }
          
          @media (max-width: 480px) {
            div[style*="position: 'absolute'"] {
              bottom: 70px;
              left: 5px;
              right: 5px;
              font-size: 9px;
              padding: 6px;
            }
          }
        `}
      </style>
    </div>
  );
};