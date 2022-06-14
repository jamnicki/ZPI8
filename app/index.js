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
  //   name: (str),
  //   mapSize: [(float), (float)],
  //   matrixSize: [(int),(int)],
  //   pixels: [{ pos: [(int),(int)], state: (-1/0/1) }, ...],
  //   pos: [(float),(float)],
  //   deg: (float),
  //   sensors: { (str): (float), ...}
  // }
  const { name, mapSize, matrixSize, pixels, pos, deg, sensors } = req.body;
  const id = parseInt(req.params.id.replace('e-puck', ''));
  // convert position values to percentages
  // ONLY WORKS IF THE (0,0) POINT IS IN THE CENTER OF THE MAP!
  pos[0] = ((1 + pos[0]) / mapSize[0]) * 100;
  pos[1] = ((1 + pos[1]) / mapSize[1]) * 100;
  io.emit('robot', {
    name: `${name} ${mapSize[0]}x${mapSize[1]} [${matrixSize[0]}x${matrixSize[1]}]`,
    mapSize: { x: mapSize[0], y: mapSize[1] },
    matrixSize: { x: matrixSize[0], y: matrixSize[1] },
    pixels,
    id,
    pos: { x: pos[0], y: 100 - pos[1] },
    deg: deg, // Math.PI / 2 to add 90 deg
    sensors: Object.values(sensors), // from indexed object to array
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
