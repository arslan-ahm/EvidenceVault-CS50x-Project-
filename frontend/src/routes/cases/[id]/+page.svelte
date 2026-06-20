<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/stores';

  import AppShell from '$lib/components/AppShell.svelte';
  import EvidenceUpload from '$lib/components/EvidenceUpload.svelte';
  import SearchBar from '$lib/components/SearchBar.svelte';
  import TimelineList from '$lib/components/TimelineList.svelte';
  import { apiGet, apiPost, getApiBaseUrl } from '$lib/api';
  import type { Case, Evidence, SearchResult, TimelineEvent } from '$lib/types';

  let caseItem: Case | null = null;
  let evidence: Evidence[] = [];
  let timeline: TimelineEvent[] = [];
  let searchResults: SearchResult[] = [];
  let loading = true;
  let message = '';
  let query = '';
  let caseId = '';
  let exportUrl = '';
  $: caseId = $page.params.id;
  $: exportUrl = `${getApiBaseUrl()}/cases/${caseId}/export`;

  async function loadCase() {
    loading = true;
    try {
      caseItem = await apiGet<Case>(`/cases/${caseId}`);
      evidence = await apiGet<Evidence[]>(`/cases/${caseId}/evidence`);
      timeline = await apiGet<TimelineEvent[]>(`/cases/${caseId}/timeline`);
    } catch (error) {
      message = error instanceof Error ? error.message : 'Unable to load case';
    } finally {
      loading = false;
    }
  }

  async function uploadEvidence(file: File) {
    const formData = new FormData();
    formData.append('case_id', caseId);
    formData.append('file', file);
    await apiPost('/evidence/upload', formData);
    message = 'Evidence uploaded and processed';
    await loadCase();
  }

  async function searchCase(value: string) {
    query = value;
    searchResults = value.trim() ? await apiGet<SearchResult[]>(`/search?q=${encodeURIComponent(value)}`) : [];
  }

  onMount(() => {
    void loadCase();
  });
</script>

<AppShell title={caseItem ? `${caseItem.title} | EvidenceVault AI` : 'Case | EvidenceVault AI'}>
  <svelte:fragment slot="actions">
    <a class="button-secondary" href="/">Back to dashboard</a>
    <a class="button-primary" href={exportUrl} target="_blank" rel="noreferrer">Export PDF</a>
  </svelte:fragment>

  {#if loading}
    <div class="panel p-8 text-sm text-slate-600">Loading case details...</div>
  {:else if caseItem}
    <section class="grid gap-6 lg:grid-cols-[0.95fr_1.05fr]">
      <div class="space-y-6">
        <div class="panel p-6">
          <p class="text-xs font-semibold uppercase tracking-[0.2em] text-blue-600">Case detail</p>
          <h2 class="mt-2 text-3xl font-semibold tracking-tight">{caseItem.title}</h2>
          <p class="mt-3 text-sm text-slate-600">{caseItem.description || 'No description yet.'}</p>
        </div>

        <EvidenceUpload on:upload={(event) => uploadEvidence(event.detail.file)} />

        <div class="panel p-6">
          <h3 class="text-lg font-semibold">Evidence</h3>
          {#if evidence.length === 0}
            <p class="mt-3 text-sm text-slate-600">No evidence uploaded yet.</p>
          {:else}
            <ul class="mt-4 space-y-3">
              {#each evidence as item}
                <li class="rounded-2xl border border-slate-200 bg-slate-50 p-4 text-sm">
                  <div class="flex items-center justify-between gap-3">
                    <span class="font-medium text-ink">{item.file_name}</span>
                    <span class="text-xs text-slate-500">{item.file_type}</span>
                  </div>
                  <p class="mt-2 line-clamp-3 text-slate-600">{item.extracted_text || 'No extracted text available yet.'}</p>
                </li>
              {/each}
            </ul>
          {/if}
        </div>
      </div>

      <div class="space-y-6">
        <SearchBar bind:value={query} on:search={(event) => searchCase(event.detail)} />
        {#if searchResults.length > 0}
          <div class="panel p-5">
            <h3 class="text-lg font-semibold">Search results</h3>
            <div class="mt-4 space-y-3">
              {#each searchResults as result}
                <div class="rounded-2xl border border-slate-200 bg-slate-50 p-4 text-sm">
                  <p class="font-medium text-ink">{result.case_title}</p>
                  <p class="mt-1 text-slate-600">{result.snippet}</p>
                </div>
              {/each}
            </div>
          </div>
        {/if}

        <TimelineList items={timeline} />
        {#if message}
          <div class="panel p-5 text-sm text-slate-700">{message}</div>
        {/if}
      </div>
    </section>
  {/if}
</AppShell>
