<script lang="ts">
  import type { TimelineEvent } from '$lib/types';

  export let items: TimelineEvent[] = [];
</script>

<div class="card p-5">
  <h3 class="text-lg font-semibold text-slate-900 dark:text-white">Timeline</h3>
  {#if items.length === 0}
    <div class="mt-4 flex items-center gap-3 rounded-xl border border-dashed border-slate-300 p-4 dark:border-slate-700/60">
      <div class="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-slate-100 dark:bg-slate-700/50">
        <svg class="h-4 w-4 text-slate-400 dark:text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
      </div>
      <p class="text-sm text-slate-500 dark:text-slate-400">No timeline events yet — dates found in uploaded evidence will appear here.</p>
    </div>
  {:else}
    <ol class="mt-4 space-y-3">
      {#each items as item}
        <li class="rounded-2xl border border-slate-200 bg-slate-50 p-4 dark:border-slate-700/60 dark:bg-slate-800/30">
          <div class="flex items-center justify-between gap-3">
            <p class="font-medium text-slate-900 dark:text-white">{item.event_text}</p>
            <span class="text-xs text-slate-400 dark:text-slate-500">{item.event_date ?? 'Undated'}</span>
          </div>
        </li>
      {/each}
    </ol>
  {/if}
</div>
