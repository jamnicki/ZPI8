<script>
  import { onMount } from 'svelte';

  import Chart from 'chart.js/auto';
  import 'chartjs-adapter-date-fns';
  import { pl } from 'date-fns/locale';

  import { logInterval, orient, colors } from './config.js';

  let canvas;
  let chart;

  function newChart(canvas) {
    return new Chart(canvas, {
      type: 'line',
      data: {
        datasets: [
          {
            label: 'Nieznane',
            backgroundColor: `rgba(${colors.white.toString()})`,
            borderColor: `rgba(${colors.white.toString()})`,
            radius: 4,
            showLine: true,
          },
          {
            label: 'Odwiedzone',
            backgroundColor: `rgba(${colors.green.toString()})`,
            borderColor: `rgba(${colors.green.toString()})`,
            radius: 4,
            showLine: true,
          },
          {
            label: 'Przeszkoda',
            backgroundColor: `rgba(${colors.black.toString()})`,
            borderColor: `rgba(${colors.black.toString()})`,
            radius: 4,
            showLine: true,
          },
        ],
      },
      options: {
        fill: false,
        interaction: { intersect: false },
        radius: 0,
        tension: 0,
        spanGaps: true,
        plugins: { legend: { position: 'bottom' } },
        scales: {
          x: {
            type: 'time',
            adapters: { date: { locale: pl } },
          },
          y: { min: -10, max: 110, grid: { drawOnChartArea: false }, type: 'linear' },
        },
      },
    });
  }

  export function plot(states, time) {
    chart.data.datasets[0].data = [...chart.data.datasets[0].data, { x: time, y: states.unknown }];
    chart.data.datasets[1].data = [...chart.data.datasets[1].data, { x: time, y: states.visited }];
    chart.data.datasets[2].data = [...chart.data.datasets[2].data, { x: time, y: states.wall }];
    chart.update();
  }

  onMount(() => {
    chart = newChart(canvas);
  });
</script>

<canvas width="100" height="100" bind:this={canvas} />
