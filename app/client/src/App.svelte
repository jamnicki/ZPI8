<script>
  import { io } from 'socket.io-client';
  import Map from './Map.svelte';

  const socket = io('http://localhost:8000');

  let maps = [];

  socket.on('robot', data => {
    const { name, mapSize, matrixSize, pixels, id, pos, deg, sensors } = data;
    const robot = { id, pos, deg, sensors };
    // check if the map already exists
    let i = maps.findIndex(m => m.name == name);
    if (i == -1) {
      // insert a new map and robot
      const map = { map: null, name, mapSize, matrixSize, robots: [robot] };
      maps = [...maps, map];
      i = maps.length - 1;
    } else {
      // update the robot
      let j = maps[i].robots.findIndex(r => r.id == robot.id);
      maps[i].robots[j] = robot;
    }
    if (maps[i].map) {
      // update the canvas when if it's mounted
      maps[i].map.updateCanvas(pixels);
    }
  });
</script>

<main>
  {#each maps as { map, name, mapSize, matrixSize, robots }}
    <div class="map">
      <div class="robots">
        {#each robots as { pos, deg }, i}
          <div class="robot">
            <b>epuck {i + 1}:</b><br />
            x: {Math.round(pos.x * 100) / 100}<br />
            y: {Math.round(pos.y * 100) / 100}<br />
            deg: {Math.round(deg * 100) / 100}
          </div>
        {/each}
      </div>
      <br />
      <Map {name} {mapSize} {matrixSize} {robots} bind:this={map} />
    </div>
  {/each}
</main>

<style>
  main {
    display: grid;
    grid-auto-columns: 1fr;
    padding: 1rem;
    font-size: 1.2rem;
    text-align: center;
  }
  .map {
    max-width: 500px;
  }
  .robots {
    display: flex;
    justify-content: center;
    gap: 2rem;
  }
  .robot {
    background-color: rgb(240, 240, 240);
    border-radius: 1rem;
    padding: 1rem;
  }
</style>
