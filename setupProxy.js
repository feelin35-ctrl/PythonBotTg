const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  app.use(
    '/api',
    createProxyMiddleware({
      target: 'http://127.0.0.1:8001',
      changeOrigin: true,
      pathRewrite: {
        '^/api': '/api', // Это важно для правильной маршрутизации
      },
    })
  );
};