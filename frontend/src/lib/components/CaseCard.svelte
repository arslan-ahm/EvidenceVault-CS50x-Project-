<script lang="ts">
  import RelativeTime from './RelativeTime.svelte';
  import { stripMarkdown } from '$lib/markdownExcerpt';
  import type { Case } from '$lib/types';

  export let item: Case;

  const severityStyles: Record<string, string> = {
    critical: 'text-red-600 bg-red-50 dark:text-red-400 dark:bg-red-500/10',
    high: 'text-orange-600 bg-orange-50 dark:text-orange-400 dark:bg-orange-500/10',
    medium: 'text-amber-600 bg-amber-50 dark:text-yellow-400 dark:bg-yellow-500/10',
    low: 'text-green-600 bg-green-50 dark:text-green-400 dark:bg-green-500/10'
  };

  function formatLabel(value?: string) {
    if (!value) return '';
    return value.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
  }
</script>

<article class="card-hover rounded-2xl border border-slate-200 bg-white p-5 shadow-sm hover:border-blue-300 dark:border-slate-700/60 dark:bg-slate-800/50 dark:shadow-xl dark:backdrop-blur dark:hover:border-blue-500/30">
  <div class="flex items-start justify-between gap-4">
    <div>
      <h3 class="text-lg font-semibold text-slate-900 dark:text-white">{item.title}</h3>
      <p class="mt-1 line-clamp-2 text-sm text-slate-500 dark:text-slate-400">{item.description ? stripMarkdown(item.description) : 'No description yet.'}</p>
    </div>
    <span class={`shrink-0 rounded-full px-3 py-1 text-xs font-semibold ${severityStyles[item.severity || ''] || 'bg-slate-100 text-slate-600 dark:bg-slate-700/50 dark:text-slate-300'}`}>
      {formatLabel(item.severity) || 'Case'}
    </span>
  </div>
  <div class="mt-4 flex flex-wrap items-center gap-1.5">
    {#if item.category}
      <span class="rounded-full bg-slate-100 px-2.5 py-0.5 text-[11px] font-medium text-slate-600 dark:bg-slate-700/50 dark:text-slate-300">{formatLabel(item.category)}</span>
    {/if}
    {#if item.status}
      <span class="rounded-full bg-slate-100 px-2.5 py-0.5 text-[11px] font-medium text-slate-600 dark:bg-slate-700/50 dark:text-slate-300">{formatLabel(item.status)}</span>
    {/if}
    {#if item.organization_name}
      <span class="rounded-full bg-blue-50 px-2.5 py-0.5 text-[11px] font-medium text-blue-600 dark:bg-blue-500/10 dark:text-blue-400">{item.organization_name}</span>
    {/if}
  </div>
  <div class="mt-4 flex items-center justify-between text-xs text-slate-400 dark:text-slate-500">
    <span>Created <RelativeTime date={item.created_at} /></span>
    {#if item.is_public === false}
      <span class="flex items-center gap-1">
        <svg class="h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/></svg>
        Private
      </span>
    {/if}
  </div>
</article>
