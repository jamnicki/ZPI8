<script>
  import { io } from 'socket.io-client';
  import Map from './Map.svelte';

  const socket = io('http://localhost:8000');

  let maps = [];

  socket.on('robot', data => {
    const { name, size, pixels, id, pos, deg, sensors } = data;
    const robot = { id, pos, deg, sensors };
    // append new maps
    let i = maps.findIndex(m => m.name == map.name);
    // if the map already exists
    if (i) {
      // update the robot
      let j = maps[i].robots(r => r.id == robot.id);
      maps[i].robots[j] = robot;
      // maps = maps ??
    } else {
      // insert new map and robot
      const map = { map: null, name, size, robots: [robot] };
      maps = [...maps, map];
      i = maps.length - 1;
    }
    // if (maps[i].map) ??
    maps[i].map.updateCanvas(pixels);
  });

  // socket.on('robot', data => {
  //   data.pos.x = Math.round(data.position.x * 1000 + 1000, 0);
  //   data.pos.y = Math.round(-data.position.y * 1000 + 1000, 0);
  //   let i = robots.findIndex(robot => robot.id == data.id);
  //   if (i != -1) {
  //     robots[i] = data;
  //   } else {
  //     robots.push(data);
  //   }
  //   robots = robots;
  //   updateCanvas();
  // });
</script>

<main>
  {#each maps as { map, name, size }}
    <Map {name} {size} bind:this={map} />
  {/each}
</main>

<style>
  main {
    padding: 1rem;
    font-size: 1.2rem;
    text-align: center;
  }
</style>
