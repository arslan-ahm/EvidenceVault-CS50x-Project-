<script lang="ts">
  import { resolvedTheme } from '$lib/stores/theme';
  import { pick, sequentialBlue, chrome } from '$lib/charts/palette';

  export let data: { date: string; count: number }[] = [];
  export let color: { light: string; dark: string } = sequentialBlue;
  export let emptyLabel = 'No data yet';

  const width = 600;
  const height = 180;
  const padLeft = 34;
  const padBottom = 20;
  const padTop = 10;
  const padRight = 8;

  function niceMax(n: number): number {
    if (n <= 0) return 4;
    const magnitude = 10 ** Math.floor(Math.log10(n));
    const residual = n / magnitude;
    const step = residual <= 1 ? 1 : residual <= 2 ? 2 : residual <= 5 ? 5 : 10;
    return step * magnitude;
  }

  $: maxCount = niceMax(Math.max(1, ...data.map((d) => d.count)));
  $: innerW = width - padLeft - padRight;
  $: innerH = height - padTop - padBottom;
  $: points = data.map((d, i) => ({
    x: padLeft + (data.length > 1 ? (i / (data.length - 1)) * innerW : innerW / 2),
    y: padTop + innerH - (d.count / maxCount) * innerH,
    ...d
  }));
  $: linePath = points.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ');
  $: areaPath = points.length ? `${linePath} L ${points[points.length - 1].x} ${padTop + innerH} L ${points[0].x} ${padTop + innerH} Z` : '';

  $: strokeColor = pick(color, $resolvedTheme);
  $: gridColor = pick(chrome.gridline, $resolvedTheme);
  $: axisColor = pick(chrome.muted, $resolvedTheme);

  let hoverIndex: number | null = null;
  let svgEl: SVGSVGElement;

  function onMove(e: MouseEvent) {
    if (!points.length) return;
    const rect = svgEl.getBoundingClientRect();
    const relX = ((e.clientX - rect.left) / rect.width) * width;
    let nearest = 0;
    let best = Infinity;
    points.forEach((p, i) => {
      const dist = Math.abs(p.x - relX);
      if (dist < best) {
        best = dist;
        nearest = i;
      }
    });
    hoverIndex = nearest;
  }
  function onLeave() {
    hoverIndex = null;
  }

  function formatDate(iso: string): string {
    const d = new Date(iso + 'T00:00:00Z');
    return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric', timeZone: 'UTC' });
  }
</script>

<div class="viz-root relative">
  {#if data.every((d) => d.count === 0)}
    <p class="py-6 text-center text-sm text-slate-400 dark:text-slate-500">{emptyLabel}</p>
  {:else}
    <svg
      bind:this={svgEl}
      viewBox={`0 0 ${width} ${height}`}
      class="w-full"
      role="img"
      aria-label="Time series chart"
      on:mousemove={onMove}
      on:mouseleave={onLeave}
    >
      {#each [0, 0.5, 1] as frac}
        <line
          x1={padLeft}
          x2={width - padRight}
          y1={padTop + innerH * (1 - frac)}
          y2={padTop + innerH * (1 - frac)}
          stroke={gridColor}
          stroke-width="1"
        />
        <text x={padLeft - 6} y={padTop + innerH * (1 - frac) + 3} text-anchor="end" fill={axisColor} style="font-size:9px">
          {Math.round(maxCount * frac)}
        </text>
      {/each}

      <path d={areaPath} fill={strokeColor} opacity="0.1" stroke="none" />
      <path d={linePath} fill="none" stroke={strokeColor} stroke-width="2" stroke-linejoin="round" stroke-linecap="round" />

      {#if hoverIndex !== null}
        <line
          x1={points[hoverIndex].x}
          x2={points[hoverIndex].x}
          y1={padTop}
          y2={padTop + innerH}
          stroke={axisColor}
          stroke-width="1"
          stroke-dasharray="3,3"
        />
        <circle cx={points[hoverIndex].x} cy={points[hoverIndex].y} r="4" fill={strokeColor} stroke={pick(chrome.surface, $resolvedTheme)} stroke-width="2" />
      {/if}

      {#if points.length > 1}
        <text x={points[0].x} y={height - 4} text-anchor="start" fill={axisColor} style="font-size:9px">{formatDate(points[0].date)}</text>
        <text x={points[points.length - 1].x} y={height - 4} text-anchor="end" fill={axisColor} style="font-size:9px">{formatDate(points[points.length - 1].date)}</text>
      {/if}
    </svg>

    {#if hoverIndex !== null}
      <div
        class="pointer-events-none absolute z-10 -translate-x-1/2 -translate-y-full rounded-lg border border-slate-200 bg-white px-2.5 py-1.5 text-xs shadow-lg dark:border-slate-700 dark:bg-slate-800"
        style={`left:${(points[hoverIndex].x / width) * 100}%; top:${(points[hoverIndex].y / height) * 100}%`}
      >
        <p class="font-semibold text-slate-900 dark:text-white">{points[hoverIndex].count}</p>
        <p class="text-slate-500 dark:text-slate-400">{formatDate(points[hoverIndex].date)}</p>
      </div>
    {/if}
  {/if}
</div>
