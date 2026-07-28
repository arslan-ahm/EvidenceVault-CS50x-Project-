<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';

  import CaseCard from '$lib/components/CaseCard.svelte';
  import LoadingCard from '$lib/components/LoadingCard.svelte';
  import { apiGet } from '$lib/api';
  import { authReady, currentUser } from '$lib/stores/auth';
  import type { Case, User } from '$lib/types';

  let cases: Case[] = [];
  let loading = true;

  async function loadDashboard() {
    try {
      const me = await apiGet<User>('/auth/me');
      currentUser.set(me);
      const items = await apiGet<Case[]>('/cases');
      cases = items;
    } catch {
      await goto('/login');
    } finally {
      authReady.set(true);
      loading = false;
    }
  }

  onMount(() => {
    void loadDashboard();
  });
</script>

<svelte:head>
  <title>Dashboard | EvidenceVault</title>
</svelte:head>

{#if loading}
  <LoadingCard label="Loading your workspace..." />
{:else}
  <div class="mb-8 flex items-center justify-between">
    <div>
      <p class="text-xs font-semibold uppercase tracking-[0.2em] text-blue-600 dark:text-blue-400">Evidence management</p>
      <h1 class="mt-1 text-3xl font-bold tracking-tight text-slate-900 dark:text-white">Your complaints</h1>
    </div>
    <a href="/cases/new" class="button-primary gap-2 px-5 py-2.5">
      <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
      File a complaint
    </a>
  </div>

  <div class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
    {#each cases as item}
      <a class="block" href={`/cases/${item.id}`}>
        <CaseCard {item} />
      </a>
    {:else}
      <div class="card col-span-full p-10 text-center">
        <div class="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-slate-100 dark:bg-slate-700/50">
          <svg class="h-7 w-7 text-slate-400 dark:text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
        </div>
        <h3 class="mt-4 text-lg font-semibold text-slate-900 dark:text-white">No complaints yet</h3>
        <p class="mt-2 text-sm text-slate-500 dark:text-slate-400">File your first complaint to start tracking evidence and progress.</p>
        <a href="/cases/new" class="button-primary mt-5 inline-flex gap-2">
          <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
          File a complaint
        </a>
      </div>
    {/each}
  </div>
{/if}
