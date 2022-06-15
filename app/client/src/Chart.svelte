<script>
  import Dygraph from 'dygraphs';

  import { logAmount, testTimes, colors } from './config.js';

  let chart;

  const head = ['Date', 'Unknown', 'Visited', 'Wall', 'Explored'];
  let data = [];

  let startTime = new Date();

  let values = [];
  let now;

  export function plot(states) {
    now = new Date();
    data.push([now, Number(states.unknown), Number(states.visited), Number(states.wall), Number(states.explored)]);
    const first = data[0][0].getTime();
    const last = data[data.length - 1][0].getTime();
    const diff = last - first;
    const seconds = diff / 1000;
    const minutes = seconds / 60;
    for (const time of testTimes) {
      if (minutes > time) {
        values.push(states);
      }
    }
    new Dygraph(chart, data, {
      labels: head,
      colors: [
        `rgba(${colors.red.toString()})`,
        `rgba(${colors.green.toString()})`,
        `rgba(${colors.black.toString()})`,
        `rgba(${colors.blue.toString()})`,
      ],
      legend: 'always',
      valueRange: [-10, 110],
    });
  }
</script>

<div class="graph" bind:this={chart} />

{#if now}
  <div class="time">{(now.getTime() - startTime.getTime()) / 1000}sec</div>
{/if}

<style>
  .time {
    font-size: 2rem;
  }
</style>
