import React from 'react';
import styled from 'styled-components';

const Backdrop = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 999;
`;

const MenuContainer = styled.div`
  position: fixed;
  left: ${props => props.position?.x || 0}px;
  top: ${props => props.position?.y || 0}px;
  background: white;
  border: 1px solid #ccc;
  border-radius: 4px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.2);
  z-index: 1000;
  min-width: 120px;
  
  @media (max-width: 768px) {
    left: ${props => props.position?.x > window.innerWidth - 150 ? window.innerWidth - 150 : props.position?.x || 0}px;
    top: ${props => props.position?.y > window.innerHeight - 100 ? window.innerHeight - 100 : props.position?.y || 0}px;
    min-width: 100px;
  }
  
  @media (max-width: 480px) {
    left: ${props => props.position?.x > window.innerWidth - 120 ? window.innerWidth - 120 : props.position?.x || 0}px;
    top: ${props => props.position?.y > window.innerHeight - 80 ? window.innerHeight - 80 : props.position?.y || 0}px;
    min-width: 80px;
  }
`;

const MenuItem = styled.div`
  padding: 10px;
  cursor: pointer;
  color: ${props => props.color || '#333'};
  border-bottom: 1px solid #eee;
  font-size: 14px;
  
  &:hover {
    background: #f5f5f5;
  }
  
  &:last-child {
    border-bottom: none;
  }
  
  @media (max-width: 768px) {
    padding: 8px;
    font-size: 12px;
  }
  
  @media (max-width: 480px) {
    padding: 6px;
    font-size: 11px;
  }
`;

export const ContextMenu = ({ position, onDelete, onClose }) => {
  if (!position) return null;

  return (
    <>
      <Backdrop onClick={onClose} />
      <MenuContainer position={position}>
        <MenuItem color="#dc3545" onClick={onDelete}>
          🗑️ Удалить блок
        </MenuItem>
        <MenuItem color="#6c757d" onClick={onClose}>
          ✕ Отмена
        </MenuItem>
      </MenuContainer>
    </>
  );
};