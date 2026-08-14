<script lang="ts">
  import { resolvedTheme } from '$lib/stores/theme';
  import { pick, sequentialBlue, chrome } from '$lib/charts/palette';

  export let data: { key: string; label: string; count: number }[] = [];
  export let color: { light: string; dark: string } = sequentialBlue;
  export let emptyLabel = 'No data yet';

  $: barColor = pick(color, $resolvedTheme);
  $: gridColor = pick(chrome.gridline, $resolvedTheme);
  $: maxCount = Math.max(1, ...data.map((d) => d.count));

  let hovered: { label: string; count: number; x: number; y: number } | null = null;

  function onEnter(e: MouseEvent | FocusEvent, d: { label: string; count: number }) {
    const rect = (e.currentTarget as HTMLElement).getBoundingClientRect();
    const parent = (e.currentTarget as HTMLElement).closest('.viz-root')!.getBoundingClientRect();
    hovered = { label: d.label, count: d.count, x: rect.left - parent.left + rect.width / 2, y: rect.top - parent.top };
  }
  function onLeave() {
    hovered = null;
  }
</script>

<div class="viz-root relative">
  {#if data.length === 0}
    <p class="py-6 text-center text-sm text-slate-400 dark:text-slate-500">{emptyLabel}</p>
  {:else}
    <div class="space-y-2.5">
      {#each data as d (d.key)}
        <div
          class="group flex items-center gap-3"
          role="button"
          aria-label={`${d.label}: ${d.count}`}
          on:mouseenter={(e) => onEnter(e, d)}
          on:mouseleave={onLeave}
          on:focus={(e) => onEnter(e, d)}
          on:blur={onLeave}
          tabindex="0"
        >
          <span class="w-32 shrink-0 truncate text-xs text-slate-500 dark:text-slate-400" title={d.label}>{d.label}</span>
          <div class="relative h-5 flex-1 rounded-full" style={`background-color: ${gridColor}`}>
            <div
              class="h-5 rounded-full transition-all duration-500 ease-out group-hover:opacity-80"
              style={`width:${(d.count / maxCount) * 100}%; background-color:${barColor}`}
            ></div>
          </div>
          <span class="w-10 shrink-0 text-right text-xs font-semibold tabular-nums text-slate-700 dark:text-slate-200">{d.count}</span>
        </div>
      {/each}
    </div>
  {/if}

  {#if hovered}
    <div
      class="pointer-events-none absolute z-10 -translate-x-1/2 -translate-y-full rounded-lg border border-slate-200 bg-white px-2.5 py-1.5 text-xs shadow-lg dark:border-slate-700 dark:bg-slate-800"
      style={`left:${hovered.x}px; top:${hovered.y - 6}px`}
    >
      <p class="font-semibold text-slate-900 dark:text-white">{hovered.count}</p>
      <p class="text-slate-500 dark:text-slate-400">{hovered.label}</p>
    </div>
  {/if}
</div>
