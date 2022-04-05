<script>
  import { io } from 'socket.io-client';
  const socket = io('http://localhost:8000');

  const orient = [1.27, 0.77, 0, 5.21, 4.21, 3.14159, 2.37, 1.87];
  const eraser = false;

  function drawPixel(pos, r, g, b, a) {
    // console.log(pos);
    const i = (pos[0] + pos[1] * canvas.width) * 4;
    canvasData.data[i + 0] = r;
    canvasData.data[i + 1] = g;
    canvasData.data[i + 2] = b;
    canvasData.data[i + 3] = a;
  }

  function drawSquare(size, [x, y], r, g, b, a) {
    for (let i = 0; i < size; i++) {
      for (let j = 0; j < size; j++) {
        drawPixel([x + i, y + j], r, g, b, a);
      }
    }
  }
  function updateCanvas() {
    const green = [48, 138, 55, 200];
    const black = [0, 0, 0, 255];
    const white = [255, 255, 255, 50];
    for (const robot of robots) {
      let { x, y } = robot.position;
      if (canvasData) {
        drawSquare(3, [x, y], ...green);
        for (let i in robot.sensors) {
          let sensor = robot.sensors[i];
          const xn = Math.round(Math.abs(Math.cos(orient[i] + robot.rotation) * sensor * 1000 - x), 0);
          const yn = Math.round(Math.abs(Math.sin(orient[i] + robot.rotation) * sensor * 1000 + y), 0);
          if (sensor < 0.05) {
            drawSquare(20, [xn, yn], ...black);
          } else {
            if (eraser) drawSquare(5, [xn, yn], ...white);
          }
        }
      }
    }
    ctx.putImageData(canvasData, 0, 0);
  }

  let robots = [];

  socket.on('data', data => {
    data.position.x = Math.round(data.position.x * 1000 + 1000, 0);
    data.position.y = Math.round(-data.position.y * 1000 + 1000, 0);
    let i = robots.findIndex(robot => robot.id == data.id);
    if (i != -1) {
      robots[i] = data;
    } else {
      robots.push(data);
    }
    robots = robots;
    updateCanvas();
  });

  let canvas;
  let ctx;
  let canvasData;
  $: if (canvas) {
    ctx = canvas.getContext('2d');
    canvasData = ctx.getImageData(0, 0, canvas.width, canvas.height);
  }
</script>

<main>
  <div class="wrapper">
    <canvas width="2000" height="2000" bind:this={canvas} />
    {#each robots as robot}
      <div
        class="robot"
        style="top: calc({robot.position.y}% / 20); left: calc({robot.position
          .x}% / 20); transform: translate(-50%, -50%) rotate({robot.rotation}rad);"
      >
        <span>x{robot.position.y}</span><br />
        <span>y{robot.position.y}</span>
        {#each robot.sensors as sensor, s}
          <div class="laser" style="transform: rotate({-orient[s]}rad); width: {sensor * 1000}px">
            <span>{s}</span>
          </div>
        {/each}
      </div>
    {/each}
  </div>
</main>

<style>
  main {
    padding: 1rem;
    font-size: 1.2rem;
    text-align: center;
  }
  canvas {
    width: 100%;
    border: solid 1px blue;
  }

  .wrapper {
    position: relative;
  }
  .robot {
    position: absolute;
    width: 3.75%;
    height: 3.75%;
    background-color: rgb(48, 138, 55);
    border-radius: 50%;
    line-height: 0.75;
  }
  .robot span {
    position: relative;
    top: 20%;
    color: #000;
    font-size: 0.8rem;
  }
  .laser {
    z-index: -1;
    position: absolute;
    top: 50%;
    left: 50%;
    height: 2px;
    background-color: rgb(255, 75, 216);
    transform-origin: left center;
  }
  .laser span {
    position: absolute;
    top: 5px;
    right: 0;
  }
</style>
