const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  // Определяем целевой URL для прокси
  const target = process.env.REACT_APP_API_URL || 'http://localhost:8002';
  
  app.use(
    '/api',
    createProxyMiddleware({
      target: target,
      changeOrigin: true,
      logLevel: 'debug'  // Add debug logging
    })
  );
  
  console.log('Proxy setup for /api requests to:', target);
};