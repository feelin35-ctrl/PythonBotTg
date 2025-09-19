import React, { useState, useEffect, useRef } from 'react';
import './EmojiPicker.css';

// Популярные эмодзи по категориям (как в Телеграме)
const emojiCategories = {
  'Эмоции': [
    '😀', '😃', '😄', '😁', '😆', '😅', '🤣', '😂', '🙂', '🙃',
    '😉', '😊', '😇', '🥰', '😍', '🤩', '😘', '😗', '😚', '😙',
    '😋', '😛', '😜', '🤪', '😝', '🤑', '🤗', '🤭', '🤫', '🤔',
    '🤐', '🤨', '😐', '😑', '😶', '😏', '😒', '🙄', '😬', '🤥',
    '😔', '😪', '🤤', '😴', '😷', '🤒', '🤕', '🤢', '🤮', '🤧',
    '🥵', '🥶', '🥴', '😵', '🤯', '🤠', '🥳', '😎', '🤓', '🧐'
  ],
  'Люди': [
    '👋', '🤚', '🖐', '✋', '🖖', '👌', '🤌', '🤏', '✌', '🤞',
    '🤟', '🤘', '🤙', '👈', '👉', '👆', '🖕', '👇', '☝', '👍',
    '👎', '👊', '✊', '🤛', '🤜', '👏', '🙌', '👐', '🤲', '🤝',
    '🙏', '✍', '💅', '🤳', '💪', '🦾', '🦿', '🦵', '🦶', '👂',
    '🦻', '👃', '🧠', '🫀', '🫁', '🦷', '🦴', '👀', '👁', '👅'
  ],
  'Животные': [
    '🐶', '🐱', '🐭', '🐹', '🐰', '🦊', '🐻', '🐼', '🐨', '🐯',
    '🦁', '🐮', '🐷', '🐽', '🐸', '🐵', '🙈', '🙉', '🙊', '🐒',
    '🐔', '🐧', '🐦', '🐤', '🐣', '🐥', '🦆', '🦅', '🦉', '🦇',
    '🐺', '🐗', '🐴', '🦄', '🐝', '🐛', '🦋', '🐌', '🐞', '🐜',
    '🦗', '🕷', '🦂', '🐢', '🐍', '🦎', '🦖', '🦕', '🐙', '🦑'
  ],
  'Еда': [
    '🍏', '🍎', '🍐', '🍊', '🍋', '🍌', '🍉', '🍇', '🍓', '🫐',
    '🍈', '🍒', '🍑', '🥭', '🍍', '🥥', '🥝', '🍅', '🍆', '🥑',
    '🥦', '🥬', '🥒', '🌶', '🫑', '🌽', '🥕', '🫒', '🧄', '🧅',
    '🥔', '🍠', '🥐', '🥯', '🍞', '🥖', '🥨', '🧀', '🥚', '🍳',
    '🧈', '🥞', '🧇', '🥓', '🥩', '🍗', '🍖', '🦴', '🌭', '🍔'
  ],
  'Объекты': [
    '⌚', '📱', '📲', '💻', '⌨', '🖥', '🖨', '🖱', '🖲', '🕹',
    '🗜', '💽', '💾', '💿', '📀', '📼', '📷', '📸', '📹', '🎥',
    '📽', '🎞', '📞', '☎', '📟', '📠', '📺', '📻', '🎙', '🎚',
    '🎛', '🧭', '⏱', '⏲', '⏰', '🕰', '⌛', '⏳', '📡', '🔋',
    '🔌', '💡', '🔦', '🕯', '🪔', '🧯', '🛢', '💸', '💵', '💴'
  ],
  'Символы': [
    '❤', '🧡', '💛', '💚', '💙', '💜', '🖤', '🤍', '🤎', '💔',
    '❣', '💕', '💞', '💓', '💗', '💖', '💘', '💝', '💟', '☮',
    '✝', '☪', '🕉', '☸', '✡', '🔯', '🕎', '☯', '☦', '🛐',
    '⛎', '♈', '♉', '♊', '♋', '♌', '♍', '♎', '♏', '♐',
    '♑', '♒', '♓', '🆔', '⚛', '🉑', '☢', '☣', '📴', '📳'
  ]
};

const EmojiPicker = ({ onEmojiSelect, onClose, position }) => {
  const [activeCategory, setActiveCategory] = useState('Эмоции');
  const [searchTerm, setSearchTerm] = useState('');
  const pickerRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (pickerRef.current && !pickerRef.current.contains(event.target)) {
        onClose();
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [onClose]);

  const filteredEmojis = () => {
    if (!searchTerm) {
      return emojiCategories[activeCategory] || [];
    }
    
    // Поиск по всем категориям
    const allEmojis = Object.values(emojiCategories).flat();
    return allEmojis.filter(emoji => 
      emoji.includes(searchTerm) || 
      // Здесь можно добавить поиск по названиям эмодзи
      false
    );
  };

  const handleEmojiClick = (emoji) => {
    onEmojiSelect(emoji);
    onClose();
  };

  const pickerStyle = {
    position: 'fixed',
    left: position?.x || 0,
    top: position?.y || 0,
    zIndex: 10000,
    transform: position?.x > window.innerWidth - 320 ? 'translateX(-100%)' : 'none'
  };

  return (
    <div 
      ref={pickerRef}
      className="emoji-picker" 
      style={pickerStyle}
    >
      <div className="emoji-picker-header">
        <input
          type="text"
          placeholder="Поиск эмодзи..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="emoji-search"
        />
      </div>
      
      <div className="emoji-categories">
        {Object.keys(emojiCategories).map(category => (
          <button
            key={category}
            onClick={() => setActiveCategory(category)}
            className={`category-btn ${activeCategory === category ? 'active' : ''}`}
          >
            {category}
          </button>
        ))}
      </div>
      
      <div className="emoji-grid">
        {filteredEmojis().map((emoji, index) => (
          <button
            key={index}
            onClick={() => handleEmojiClick(emoji)}
            className="emoji-btn"
            title={emoji}
          >
            {emoji}
          </button>
        ))}
      </div>
    </div>
  );
};

export default EmojiPicker;