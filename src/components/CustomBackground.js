// src/components/CustomBackground.js
import React from 'react';

export const CustomBackground = () => {
  return (
    <svg
      style={{
        position: 'absolute',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
      }}
    >
      <defs>
        <pattern
          id="grid-pattern"
          width="20"
          height="20"
          patternUnits="userSpaceOnUse"
        >
          <path
            d="M 20 0 L 0 0 0 20"
            fill="none"
            stroke="rgba(0, 0, 0, 0.1)"
            strokeWidth="0.5"
          />
        </pattern>
      </defs>
      <rect width="100%" height="100%" fill="url(#grid-pattern)" />
      
      {/* Адаптивные стили для мобильных устройств */}
      <style>
        {`
          @media (max-width: 768px) {
            pattern {
              width: 15;
              height: 15;
            }
            path {
              strokeWidth: 0.3;
            }
          }
          
          @media (max-width: 480px) {
            pattern {
              width: 10;
              height: 10;
            }
            path {
              strokeWidth: 0.2;
            }
          }
        `}
      </style>
    </svg>
  );
};

export default CustomBackground;