const express = require('express');
const app = express();
const http = require('http').createServer(app);
const io = require('socket.io')(http, {
  cors: {
    origin: "*",
    methods: ["GET", "POST"]
  }
});

const axios = require('axios');

const Redis = require('ioredis');
const redisHost = process.env.REDIS_HOST || 'redis';
const redisPort = process.env.REDIS_PORT || 6379;
const redisClient = new Redis({ host: redisHost, port: redisPort });

redisClient.on('connect', () => {
  console.log('Connected to Redis');
});
redisClient.on('error', (err) => {
  console.error('Redis error:', err);
});

app.get('/', (req, res) => {
  res.sendFile(__dirname + '/index.html');
});

io.on('connection', (socket) => {
  console.log('Socket Connected...');

  socket.on('new user', async (username, callback) => {
    try {
      const exists = await redisClient.sismember('usernames', username);
      if (exists) {
        callback(false);
      } else {
        callback(true);
        socket.username = username;
        await redisClient.sadd('usernames', username);
        const users = await redisClient.smembers('usernames');
        io.emit('usernames', users);
      }
    } catch (err) {
      console.error('Redis operation failed:', err);
      callback(false);
    }
  });

  socket.on('send message', async (msg) => {
    const messagePayload = {
      user: socket.username,
      msg: msg,
      timestamp: new Date().toISOString()
    };

    console.log('Sending message to VM:', messagePayload);

    try {
      await axios.post('http://34.133.242.23:3001/store-message', messagePayload); // insert VM external IP here, keep socket as 3001
    } catch (err) {
      console.error('Failed to store message:', err.message);
    }

    io.emit('new message', messagePayload);
  });


  socket.on('disconnect', async () => {
    if (!socket.username) return;
    try {
      await redisClient.srem('usernames', socket.username);
      const users = await redisClient.smembers('usernames');
      io.emit('usernames', users);
    } catch (err) {
      console.error('Redis operation failed:', err);
    }
  });
});

http.listen(process.env.PORT || 3000, () => {
  console.log('Server listening on port', process.env.PORT || 3000);
});
