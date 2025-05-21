const express = require('express');
const fs = require('fs');
const path = require('path');

const app = express();
app.use(express.json());

const logFilePath = path.join(__dirname, 'messages.log');

app.get('/', (req, res) => {
  res.send('Logger server is running.');
});

app.post('/store-message', (req, res) => {
  const { user, msg, timestamp } = req.body;
  const line = `${timestamp} [${user}]: ${msg}\n`;
  fs.appendFile(logFilePath, line, (err) => {
    if (err) {
      console.error('Failed to save message:', err);
      return res.status(500).send('Error saving message');
    }
    console.log('Message saved:', line.trim());
    res.sendStatus(200);
  });
});

const PORT = 3001;
app.listen(PORT, () => {
  console.log(`Logger server listening on port ${PORT}`);
});
