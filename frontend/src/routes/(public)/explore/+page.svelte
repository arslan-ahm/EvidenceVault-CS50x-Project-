<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/stores';

  import LoadingCard from '$lib/components/LoadingCard.svelte';
  import RelativeTime from '$lib/components/RelativeTime.svelte';
  import { apiGet } from '$lib/api';
  import { stripMarkdown } from '$lib/markdownExcerpt';
  import { currentUser } from '$lib/stores/auth';
  import type { PublicReport } from '$lib/types';

  const severityOptions = ['all', 'low', 'medium', 'high', 'critical'];
  const statusOptions = ['all', 'open', 'triaged', 'in_progress', 'resolved'];
  const sortOptions = ['recent', 'trending', 'popular'];

  let reports: PublicReport[] = [];
  let loading = true;
  let pageSize = 12;
  let query = '';
  let sort = 'recent';
  let severity = 'all';
  let status = 'all';

  async function loadReports() {
    loading = true;
    const params = new URLSearchParams();
    if (query.trim()) params.set('q', query.trim());
    if (sort) params.set('sort', sort);
    if (severity !== 'all') params.set('severity', severity);
    if (status !== 'all') params.set('status', status);
    params.set('limit', String(pageSize));

    reports = await apiGet<PublicReport[]>(`/public/reports?${params.toString()}`);
    loading = false;
  }

  async function loadMore() {
    pageSize += 12;
    await loadReports();
  }

  function handleSearchInput(event: Event) {
    query = (event.target as HTMLInputElement).value;
  }

  onMount(() => {
    query = $page.url.searchParams.get('q') ?? '';
    void loadReports();
  });
</script>

<svelte:head>
  <title>Explore Complaints | EvidenceVault</title>
</svelte:head>

<div class="min-h-screen bg-slate-50 px-4 pb-8 pt-24 text-slate-900 dark:bg-slate-900 dark:text-white sm:px-6 lg:px-8">
  <div class="mx-auto max-w-6xl space-y-6">
    <div class="card p-6">
      <div class="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <p class="text-xs font-semibold uppercase tracking-[0.18em] text-blue-600 dark:text-blue-400">Explore</p>
          <h1 class="mt-2 text-3xl font-semibold tracking-tight text-slate-900 dark:text-white">Browse public scam & complaint reports</h1>
          <p class="mt-2 max-w-2xl text-sm text-slate-500 dark:text-slate-400">
            Search, filter, and review public complaints across organizations and categories.
          </p>
        </div>
        <a class="button-primary" href={$currentUser ? '/cases/new' : '/register'}>File a complaint</a>
      </div>

      <div class="mt-6 grid gap-3 lg:grid-cols-[1.4fr_0.6fr_0.6fr_0.6fr_0.6fr]">
        <input class="field" placeholder="Search reports or organizations" value={query} maxlength={200} aria-label="Search reports or organizations" on:input={handleSearchInput} />
        <div class="select-wrapper">
          <select class="field" bind:value={sort} aria-label="Sort reports">
            {#each sortOptions as option}
              <option value={option}>{option}</option>
            {/each}
          </select>
          <svg class="select-chevron h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
        </div>
        <div class="select-wrapper">
          <select class="field" bind:value={severity} aria-label="Filter by severity">
            {#each severityOptions as option}
              <option value={option}>{option}</option>
            {/each}
          </select>
          <svg class="select-chevron h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
        </div>
        <div class="select-wrapper">
          <select class="field" bind:value={status} aria-label="Filter by status">
            {#each statusOptions as option}
              <option value={option}>{option}</option>
            {/each}
          </select>
          <svg class="select-chevron h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
        </div>
        <button class="button-primary" on:click={loadReports}>Apply</button>
      </div>
    </div>

    {#if loading}
      <LoadingCard label="Loading reports..." />
    {:else if reports.length === 0}
      <div class="card p-8 text-sm text-slate-500 dark:text-slate-400">No public reports match these filters.</div>
    {:else}
      <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {#each reports as report}
          <a class="card-hover block rounded-2xl border border-slate-200 bg-white p-5 shadow-sm hover:border-blue-300 dark:border-slate-700/60 dark:bg-slate-800/50 dark:shadow-xl dark:backdrop-blur dark:hover:border-blue-500/30" href={`/explore/${report.id}`}>
            <div class="flex items-start justify-between gap-4">
              <div class="min-w-0">
                <p class="text-xs font-semibold uppercase tracking-[0.18em] text-blue-600 dark:text-blue-400">{report.category}</p>
                <h2 class="mt-2 truncate text-lg font-semibold text-slate-900 dark:text-white">{report.title}</h2>
              </div>
              <span class="shrink-0 rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-600 dark:bg-slate-700/50 dark:text-slate-300">{report.severity}</span>
            </div>
            <p class="mt-3 line-clamp-3 text-sm text-slate-500 dark:text-slate-400">{report.description ? stripMarkdown(report.description) : 'No summary available.'}</p>
            <div class="mt-4 flex items-center justify-between text-xs text-slate-400 dark:text-slate-500">
              <span class="truncate">{report.organization_name || 'Community report'}</span>
              <RelativeTime date={report.created_at} className="shrink-0" />
            </div>
            <div class="mt-2 flex items-center gap-3 text-xs text-slate-400 dark:text-slate-500">
              <span class="flex items-center gap-1">
                <svg class="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
                {report.views_count}
              </span>
              <span class="flex items-center gap-1">
                <svg class="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7"/></svg>
                {report.upvotes_count}
              </span>
            </div>
          </a>
        {/each}
      </div>

      <div class="flex justify-center">
        <button class="button-secondary" on:click={loadMore}>Load more</button>
      </div>
    {/if}
  </div>
</div>
