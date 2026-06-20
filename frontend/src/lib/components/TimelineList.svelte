<script lang="ts">
  import type { TimelineEvent } from '$lib/types';

  export let items: TimelineEvent[] = [];
</script>

<div class="panel p-5">
  <h3 class="text-lg font-semibold">Timeline</h3>
  {#if items.length === 0}
    <p class="mt-3 text-sm text-slate-600">No timeline events yet.</p>
  {:else}
    <ol class="mt-4 space-y-3">
      {#each items as item}
        <li class="rounded-2xl border border-slate-200 bg-slate-50 p-4">
          <div class="flex items-center justify-between gap-3">
            <p class="font-medium text-ink">{item.event_text}</p>
            <span class="text-xs text-slate-500">{item.event_date ?? 'Undated'}</span>
          </div>
        </li>
      {/each}
    </ol>
  {/if}
</div>
