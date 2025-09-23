// Test script to verify frontend proxy is working
const axios = require('axios');

// Test making a request through the proxy
async function testProxy() {
  try {
    console.log('Testing proxy connection...');
    
    // This request will go through the proxy to /api/login/
    const response = await axios.post('http://localhost:3000/api/login/', {
      username: 'Feelin',
      password: 'newpassword'
    });
    
    console.log('Proxy test successful!');
    console.log('Status:', response.status);
    console.log('Data:', response.data);
  } catch (error) {
    console.error('Proxy test failed:');
    console.error('Error:', error.message);
    if (error.response) {
      console.error('Response status:', error.response.status);
      console.error('Response data:', error.response.data);
    }
  }
}

testProxy();