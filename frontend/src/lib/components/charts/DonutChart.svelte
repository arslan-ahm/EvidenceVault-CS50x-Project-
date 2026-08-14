<script lang="ts">
  import { resolvedTheme } from '$lib/stores/theme';
  import { pick } from '$lib/charts/palette';

  export let data: { key: string; label: string; count: number; color: { light: string; dark: string } }[] = [];
  export let emptyLabel = 'No data yet';

  const cx = 80;
  const cy = 80;
  const rOuter = 68;
  const rInner = 42;
  const pad = 0.035; // radians of surface gap between segments

  function polar(r: number, angle: number) {
    return { x: cx + r * Math.cos(angle), y: cy + r * Math.sin(angle) };
  }

  function segmentPath(start: number, end: number) {
    const large = end - start > Math.PI ? 1 : 0;
    const so = polar(rOuter, start);
    const eo = polar(rOuter, end);
    const si = polar(rInner, end);
    const ei = polar(rInner, start);
    return `M ${so.x} ${so.y} A ${rOuter} ${rOuter} 0 ${large} 1 ${eo.x} ${eo.y} L ${si.x} ${si.y} A ${rInner} ${rInner} 0 ${large} 0 ${ei.x} ${ei.y} Z`;
  }

  $: total = data.reduce((sum, d) => sum + d.count, 0);
  $: segments = (() => {
    let angle = -Math.PI / 2;
    const visible = data.filter((d) => d.count > 0);
    return visible.map((d) => {
      const sweep = total > 0 ? (d.count / total) * (Math.PI * 2) : 0;
      const start = angle + (visible.length > 1 ? pad / 2 : 0);
      const end = angle + sweep - (visible.length > 1 ? pad / 2 : 0);
      angle += sweep;
      return { ...d, path: segmentPath(start, Math.max(start, end)) };
    });
  })();

  let hovered: { label: string; count: number; x: number; y: number } | null = null;

  function onEnter(e: MouseEvent, d: { label: string; count: number }) {
    const parent = (e.currentTarget as SVGElement).closest('.viz-root')!.getBoundingClientRect();
    hovered = { label: d.label, count: d.count, x: e.clientX - parent.left, y: e.clientY - parent.top };
  }
  function onFocusSeg(e: FocusEvent, d: { label: string; count: number }) {
    const target = e.currentTarget as SVGElement;
    const rect = target.getBoundingClientRect();
    const parent = target.closest('.viz-root')!.getBoundingClientRect();
    hovered = { label: d.label, count: d.count, x: rect.left - parent.left + rect.width / 2, y: rect.top - parent.top + rect.height / 2 };
  }
  function onLeave() {
    hovered = null;
  }
</script>

<div class="viz-root relative flex flex-col items-center gap-4 sm:flex-row sm:items-center">
  {#if total === 0}
    <p class="w-full py-6 text-center text-sm text-slate-400 dark:text-slate-500">{emptyLabel}</p>
  {:else}
    <svg viewBox="0 0 160 160" class="h-40 w-40 shrink-0">
      {#each segments as seg (seg.key)}
        <path
          d={seg.path}
          fill={pick(seg.color, $resolvedTheme)}
          class="cursor-pointer transition-opacity duration-200 hover:opacity-80"
          role="button"
          aria-label={`${seg.label}: ${seg.count}`}
          tabindex="0"
          on:mouseenter={(e) => onEnter(e, seg)}
          on:mousemove={(e) => onEnter(e, seg)}
          on:mouseleave={onLeave}
          on:focus={(e) => onFocusSeg(e, seg)}
          on:blur={onLeave}
        />
      {/each}
      <text x={cx} y={cy - 4} text-anchor="middle" class="fill-slate-900 dark:fill-white" style="font-size:22px; font-weight:600">{total}</text>
      <text x={cx} y={cy + 14} text-anchor="middle" class="fill-slate-400 dark:fill-slate-500" style="font-size:10px">total</text>
    </svg>

    <ul class="w-full space-y-1.5 text-xs">
      {#each data as d (d.key)}
        <li class="flex items-center justify-between gap-2">
          <span class="flex items-center gap-2 text-slate-600 dark:text-slate-300">
            <span class="h-2.5 w-2.5 shrink-0 rounded-full" style={`background-color:${pick(d.color, $resolvedTheme)}`}></span>
            {d.label}
          </span>
          <span class="font-semibold tabular-nums text-slate-800 dark:text-slate-100">{d.count}</span>
        </li>
      {/each}
    </ul>
  {/if}

  {#if hovered}
    <div
      class="pointer-events-none absolute z-10 -translate-x-1/2 -translate-y-full rounded-lg border border-slate-200 bg-white px-2.5 py-1.5 text-xs shadow-lg dark:border-slate-700 dark:bg-slate-800"
      style={`left:${hovered.x}px; top:${hovered.y - 10}px`}
    >
      <p class="font-semibold text-slate-900 dark:text-white">{hovered.count}</p>
      <p class="text-slate-500 dark:text-slate-400">{hovered.label}</p>
    </div>
  {/if}
</div>
