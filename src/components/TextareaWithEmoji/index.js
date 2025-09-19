import React, { useState, useRef } from 'react';
import EmojiPicker from '../EmojiPicker';

const TextareaWithEmoji = ({ 
  value, 
  onChange, 
  placeholder, 
  style, 
  className,
  ...props 
}) => {
  const [showEmojiPicker, setShowEmojiPicker] = useState(false);
  const [emojiButtonPosition, setEmojiButtonPosition] = useState({ x: 0, y: 0 });
  const textareaRef = useRef(null);
  const emojiButtonRef = useRef(null);

  const handleEmojiButtonClick = (e) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (emojiButtonRef.current) {
      const rect = emojiButtonRef.current.getBoundingClientRect();
      setEmojiButtonPosition({
        x: rect.left,
        y: rect.bottom + 5
      });
    }
    
    setShowEmojiPicker(!showEmojiPicker);
  };

  const handleEmojiSelect = (emoji) => {
    if (textareaRef.current) {
      const textarea = textareaRef.current;
      const start = textarea.selectionStart;
      const end = textarea.selectionEnd;
      const currentValue = value || '';
      
      const newValue = currentValue.slice(0, start) + emoji + currentValue.slice(end);
      
      // Создаем событие для onChange
      const syntheticEvent = {
        target: {
          value: newValue
        }
      };
      
      onChange(syntheticEvent);
      
      // Устанавливаем курсор после эмодзи
      setTimeout(() => {
        if (textarea) {
          textarea.focus();
          textarea.setSelectionRange(start + emoji.length, start + emoji.length);
        }
      }, 0);
    }
    
    setShowEmojiPicker(false);
  };

  const handleCloseEmojiPicker = () => {
    setShowEmojiPicker(false);
  };

  return (
    <div style={{ position: 'relative', width: '100%' }}>
      <textarea
        ref={textareaRef}
        value={value || ''}
        onChange={onChange}
        placeholder={placeholder}
        style={{
          ...style,
          paddingRight: '35px' // Место для кнопки эмодзи
        }}
        className={className}
        {...props}
      />
      
      <button
        ref={emojiButtonRef}
        type="button"
        onClick={handleEmojiButtonClick}
        style={{
          position: 'absolute',
          right: '8px',
          top: '8px',
          width: '24px',
          height: '24px',
          border: 'none',
          background: 'transparent',
          cursor: 'pointer',
          fontSize: '16px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          borderRadius: '4px',
          transition: 'background 0.2s ease',
          zIndex: 1
        }}
        onMouseEnter={(e) => {
          e.target.style.background = '#f0f0f0';
        }}
        onMouseLeave={(e) => {
          e.target.style.background = 'transparent';
        }}
        title="Добавить эмодзи"
      >
        😊
      </button>
      
      {showEmojiPicker && (
        <EmojiPicker
          onEmojiSelect={handleEmojiSelect}
          onClose={handleCloseEmojiPicker}
          position={emojiButtonPosition}
        />
      )}
    </div>
  );
};

export default TextareaWithEmoji;