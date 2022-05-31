<script>
  const orient = [1.27, 0.77, 0, 5.21, 4.21, 3.14159, 2.37, 1.87];
  const colors = {
    white: [255, 255, 255, 255],
    green: [48, 138, 55, 200],
    black: [0, 0, 0, 255],
  };

  export let name;
  export let size;
  export let robots = [];

  let canvas;
  let ctx;
  let ctxImg;
  $: if (canvas) {
    ctx = canvas.getContext('2d');
    canvasData = ctx.getImageData(0, 0, canvas.width, canvas.height);
  }

  function drawPixel(pos, r, g, b, a) {
    const i = (pos[0] + pos[1] * canvas.width) * 4;
    ctxImg.data[i + 0] = r;
    ctxImg.data[i + 1] = g;
    ctxImg.data[i + 2] = b;
    ctxImg.data[i + 3] = a;
  }

  function drawSquare(size, [x, y], r, g, b, a) {
    for (let i = 0; i < size; i++) {
      for (let j = 0; j < size; j++) {
        drawPixel([x + i, y + j], r, g, b, a);
      }
    }
  }

  export function updateCanvas(pixels) {
    for (const { pos, state } of pixels) {
      // state: -1 - white, 0 - green, 1 - black
      const color = state == -1 ? colors.white : state == 0 ? colors.green : colors.black;
      drawPixel(pos, ...color);
    }
    ctx.putImageData(ctxImg, 0, 0);
    // for (const robot of robots) {
    //   let { x, y } = robot.position;
    //   if (ctxImg) {
    //     drawSquare(3, [x, y], ...green);
    //     for (let i in robot.sensors) {
    //       let sensor = robot.sensors[i];
    //       const xn = Math.round(Math.abs(Math.cos(orient[i] + robot.rotation) * sensor * 1000 - x), 0);
    //       const yn = Math.round(Math.abs(Math.sin(orient[i] + robot.rotation) * sensor * 1000 + y), 0);
    //       if (sensor < 0.05) {
    //         drawSquare(20, [xn, yn], ...colors.black);
    //       }
    //     }
    //   }
    // }
    // ctx.putImageData(ctxImg, 0, 0);
  }
</script>

<div class="wrapper">
  <h1>{name} {size.x}x{size.y}</h1>
  <canvas width={size.x} height={size.y} bind:this={canvas} />
  {#each robots as robot}
    <div
      class="robot"
      style="top: calc({robot.pos.y}% / 20); left: calc({robot.pos
        .x}% / 20); transform: translate(-50%, -50%) rotate({robot.deg}rad);"
    >
      <span>x{robot.pos.y}</span><br />
      <span>y{robot.pos.y}</span>
      {#each robot.sensors as sensor, s}
        <div class="laser" style="transform: rotate({-orient[s]}rad); width: {sensor * 1000}px">
          <span>{s}</span>
        </div>
      {/each}
    </div>
  {/each}
</div>

<style>
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
