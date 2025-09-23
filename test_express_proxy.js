const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');

const app = express();

// Настройка прокси точно так же, как в setupProxy.js
const target = process.env.REACT_APP_API_URL || 'http://127.0.0.1:8002';

app.use(
  '/api',
  createProxyMiddleware({
    target: target,
    changeOrigin: true,
    // Remove pathRewrite since we want to keep the /api prefix
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

app.listen(4000, () => {
  console.log('Test proxy server running on http://localhost:4000');
});