import express from 'express';
import cors from 'cors';
import http from 'http';
import { Server } from 'socket.io';

const port = 8000;
const app = express();

app.use(cors({ origin: '*' }));
app.use(express.json({ limit: '50mb' }));
app.use(express.urlencoded({ extended: true }));

const server = http.createServer(app);
const io = new Server(server, { cors: { origin: '*' } });

app.post('/robot/:id', (req, res) => {
  // body {
  //   map: (str),
  //   size: [(int), (int)],
  //   pixels: [{ pos: [(int),(int)], state: (-1/0/1) }, ...],
  //   pos: [(float),(float)],
  //   deg: (float),
  //   sensors: { (str): (float), ...}
  // }
  const id = parseInt(req.params.id.replace('e-puck', ''));
  const map = req.body.map;
  const size = req.body.size;
  const pos = req.body.pos;
  io.emit('robot', {
    name: `${map}::${x}::${y}`,
    size: { x: size[0], y: size[1] },
    pixels: req.body.pixels,
    id,
    pos: { x: pos[0], y: pos[1] },
    deg: req.body.deg,
    // deg: req.body.deg + Math.PI / 2,
    sensors: Object.values(req.body.distance_sensors), // from indexed object to array
  });
  res.send(`robot: ${id}`);
});

io.on('connection', () => {
  console.log('a user connected');
});

server.listen(port, () => {
  console.log('We have lift off! 🚀');
  console.log(`Port: ${port}`);
});
