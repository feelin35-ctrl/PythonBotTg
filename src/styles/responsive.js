// Адаптивные стили для всего приложения

// Точки останова для медиазапросов
export const breakpoints = {
  mobile: 480,
  tablet: 768,
  desktop: 1024,
  large: 1200
};

// Медиазапросы
export const mediaQueries = {
  mobile: `@media (max-width: ${breakpoints.mobile}px)`,
  tablet: `@media (max-width: ${breakpoints.tablet}px)`,
  desktop: `@media (max-width: ${breakpoints.desktop}px)`,
  large: `@media (max-width: ${breakpoints.large}px)`,
  custom: (width) => `@media (max-width: ${width}px)`
};

// Адаптивные размеры шрифтов
export const fontSizes = {
  mobile: {
    h1: '1.3rem',
    h2: '1.2rem',
    h3: '1.1rem',
    h4: '1rem',
    body: '0.9rem',
    small: '0.8rem'
  },
  tablet: {
    h1: '1.5rem',
    h2: '1.3rem',
    h3: '1.1rem',
    h4: '1rem',
    body: '0.95rem',
    small: '0.85rem'
  },
  desktop: {
    h1: '2rem',
    h2: '1.5rem',
    h3: '1.25rem',
    h4: '1.1rem',
    body: '1rem',
    small: '0.9rem'
  }
};

// Адаптивные отступы
export const spacing = {
  mobile: {
    container: '10px',
    element: '8px',
    section: '15px'
  },
  tablet: {
    container: '15px',
    element: '10px',
    section: '20px'
  },
  desktop: {
    container: '20px',
    element: '12px',
    section: '30px'
  }
};

// Адаптивные размеры компонентов
export const componentSizes = {
  mobile: {
    button: {
      padding: '6px 10px',
      fontSize: '12px'
    },
    input: {
      padding: '6px',
      fontSize: '14px'
    },
    card: {
      padding: '10px',
      borderRadius: '6px'
    }
  },
  tablet: {
    button: {
      padding: '8px 12px',
      fontSize: '14px'
    },
    input: {
      padding: '8px',
      fontSize: '15px'
    },
    card: {
      padding: '15px',
      borderRadius: '8px'
    }
  },
  desktop: {
    button: {
      padding: '10px 15px',
      fontSize: '16px'
    },
    input: {
      padding: '10px',
      fontSize: '16px'
    },
    card: {
      padding: '20px',
      borderRadius: '10px'
    }
  }
};

// Цветовая палитра
export const colors = {
  primary: '#007bff',
  secondary: '#6c757d',
  success: '#28a745',
  danger: '#dc3545',
  warning: '#ffc107',
  info: '#17a2b8',
  light: '#f8f9fa',
  dark: '#343a40'
};

// Тени
export const shadows = {
  light: '0 2px 4px rgba(0,0,0,0.1)',
  medium: '0 4px 8px rgba(0,0,0,0.15)',
  heavy: '0 8px 16px rgba(0,0,0,0.2)'
};

// Адаптивные стили для сетки
export const grid = {
  mobile: {
    columns: 1,
    gap: '10px'
  },
  tablet: {
    columns: 2,
    gap: '15px'
  },
  desktop: {
    columns: 3,
    gap: '20px'
  }
};

// Адаптивные стили для навигации
export const navigation = {
  mobile: {
    height: '60px',
    fontSize: '14px'
  },
  tablet: {
    height: '70px',
    fontSize: '16px'
  },
  desktop: {
    height: '80px',
    fontSize: '18px'
  }
};

// Адаптивные стили для формы
export const form = {
  mobile: {
    label: {
      fontSize: '12px',
      marginBottom: '4px'
    },
    input: {
      height: '36px',
      fontSize: '14px'
    },
    button: {
      height: '36px',
      fontSize: '14px'
    }
  },
  tablet: {
    label: {
      fontSize: '14px',
      marginBottom: '6px'
    },
    input: {
      height: '40px',
      fontSize: '15px'
    },
    button: {
      height: '40px',
      fontSize: '15px'
    }
  },
  desktop: {
    label: {
      fontSize: '16px',
      marginBottom: '8px'
    },
    input: {
      height: '44px',
      fontSize: '16px'
    },
    button: {
      height: '44px',
      fontSize: '16px'
    }
  }
};