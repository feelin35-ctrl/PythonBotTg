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
      zIndex: 1000
    }}>
      <div>Nodes: {nodes.length}</div>
      <div>Edges: {edges.length}</div>
      <div>Selected: {nodes.filter(n => n.selected).length}</div>
    </div>
  );
};