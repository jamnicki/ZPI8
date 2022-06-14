<script>
  import { onMount } from 'svelte';
  import Chart from './Chart.svelte';

  import { logInterval, orient, colors } from './config.js';

  export let name;
  export let mapSize;
  export let matrixSize;
  export let robots = [];

  let time;
  let chart;

  const robotSize = (0.074 / mapSize.x) * 100; //m

  const range = r => [...Array(r).keys()];
  let pixels = range(matrixSize.x).map(() => range(matrixSize.y).map(() => -1));
  let states = { unknown: null, visited: null, wall: null, explored: null };
  let statesPrcnt = { unknown: null, visited: null, wall: null, explored: null };
  $: {
    states = { unknown: 0, visited: 0, wall: 0, explored: 0 };
    for (const i of pixels) {
      for (const j of i) {
        if (j == -1) states.unknown += 1;
        else if (j == 0) states.visited += 1;
        else states.wall += 1;
        if (j == 0 || j == 1) states.explored += 1;
      }
    }
    for (let state of Object.keys(states)) {
      statesPrcnt[state] = Number(Math.round((states[state] / (matrixSize.x * matrixSize.y)) * 10000) / 100).toFixed(2);
    }
  }

  let canvas;
  let ctx;
  let ctxImg;
  $: if (canvas) {
    ctx = canvas.getContext('2d');
    ctxImg = ctx.getImageData(0, 0, canvas.width, canvas.height);
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

  export function updateCanvas(newPixels) {
    for (const { pos, state } of newPixels) {
      pixels[pos[0]][pos[1]] = state;
      // state: -1 - white, 0 - green, 1 - black
      const color = state == -1 ? colors.white : state == 0 ? colors.green : colors.black;
      drawPixel([pos[1], pos[0]], ...color); // x and y are switched
    }
    ctx.putImageData(ctxImg, 0, 0);
  }

  onMount(() => {
    const interval = setInterval(() => {
      time = Date.now();
      chart.plot(statesPrcnt, time);
    }, logInterval);
    return () => clearInterval(interval);
  });
</script>

<div class="wrapper">
  <h1>{name}</h1>
  <br />
  <div class="info">
    <div class="legend">
        <div>
          <div class="color" style="background-color: rgba({colors.white.toString()})" />
          Nieznane:<br />{statesPrcnt.unknown}%
        </div>
        <div>
          <div class="color" style="background-color: rgba({colors.green.toString()})" />
          Odwiedzone:<br />{statesPrcnt.visited}%
        </div>
        <div>
          <div class="color" style="background-color: rgba({colors.blue.toString()})" />
          Odkryte:<br />{statesPrcnt.explored}%
        </div>
        <div>
          <div class="color" style="background-color: rgba({colors.black.toString()})" />
          Przeszkoda:<br />{statesPrcnt.wall}%
        </div>
    </div>
  </div>
  <br />
  <div class="map">
    <canvas width={matrixSize.x} height={matrixSize.y} bind:this={canvas} />
    {#each robots as robot}
      <div
        class="robot"
        style="top: {robot.pos.y}%; left: {robot.pos
          .x}%; width: {robotSize}%; height: {robotSize}%; transform: translate(-50%, -50%) rotate({robot.deg}deg);"
      >
        {#each robot.sensors as sensor, s}
          <div class="laser" style="transform: rotate({-orient[s]}rad); width: {sensor * 400}px" />
        {/each}
      </div>
    {/each}
  </div>
  <Chart bind:this={chart} />
</div>

<style>
  .map {
    position: relative;
  }

  .legend {
    display: grid;
    grid-template-rows: 1fr 1fr;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
  }
  .legend > div {
    justify-self: center;
    display: flex;
    gap: 0.5rem;
  }
  .color {
    border: 1px solid rgba(0, 0, 0, 0.3);
    border-radius: 50%;
    width: 20px;
    height: 20px;
  }

  canvas {
    width: 100%;
    border: solid 1px rgb(0, 0, 0);
  }

  .robot {
    position: absolute;
    background-color: rgb(62, 79, 231);
    border-radius: 50%;
    line-height: 0.75;
  }

  .laser {
    z-index: -1;
    position: absolute;
    top: 50%;
    left: 50%;
    height: 2px;
    background-color: rgb(191, 81, 255);
    transform-origin: left center;
  }
</style>
