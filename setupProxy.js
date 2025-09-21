const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  // Определяем целевой URL для прокси
  const target = process.env.REACT_APP_API_URL || 'http://127.0.0.1:8001';
  
  app.use(
    '/api',
    createProxyMiddleware({
      target: target,
      changeOrigin: true,
      pathRewrite: {
        '^/api': '/api',
      },
      onError: (err, req, res) => {
        console.error('Proxy error:', err);
        res.writeHead(500, {
          'Content-Type': 'text/plain',
        });
        res.end('Proxy error: ' + err.message);
      }
    })
  );
  
  console.log('Proxy setup for /api requests to:', target);
};