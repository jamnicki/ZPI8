import express from 'express';
import cors from 'cors';
import http from 'http';
import { Server } from 'socket.io';

const port = 8000;

const app = express();

// setup cors
app.use(cors({ origin: '*' }));
app.use(express.json({ limit: '50mb' }));
app.use(express.urlencoded());

const server = http.createServer(app);
const io = new Server(server, { cors: { origin: '*' } });

app.post('/robot/:id/distance-sensors', (req, res) => {
  const id = parseInt(req.params.id.replace('e-puck', ''));
  const [x, y, z] = req.body.robot_position;
  io.emit('data', {
    id,
    position: { x, y, z },
    rotation: req.body.robot_rotation + Math.PI / 2,
    sensors: Object.values(req.body.distance_sensors),
  });
  res.send('Got a POST request');
});

io.on('connection', socket => {
  console.log('a user connected');
  // io.emit('data', { test: 0 });
});

server.listen(port, () => {
  console.log(`Port: ${port}`);
});
