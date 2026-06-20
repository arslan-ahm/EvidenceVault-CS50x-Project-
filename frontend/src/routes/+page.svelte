<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';

  import AppShell from '$lib/components/AppShell.svelte';
  import CaseCard from '$lib/components/CaseCard.svelte';
  import { apiGet, apiPost } from '$lib/api';
  import { authReady, currentUser } from '$lib/stores/auth';
  import type { Case, User } from '$lib/types';

  let cases: Case[] = [];
  let title = '';
  let description = '';
  let loading = true;
  let errorMessage = '';

  async function loadDashboard() {
    try {
      const me = await apiGet<User>('/auth/me');
      currentUser.set(me);
      const items = await apiGet<Case[]>('/cases');
      cases = items;
    } catch (error) {
      await goto('/login');
    } finally {
      authReady.set(true);
      loading = false;
    }
  }

  async function createCase() {
    errorMessage = '';
    try {
      const created = await apiPost<Case>('/cases', { title, description });
      cases = [created, ...cases];
      title = '';
      description = '';
    } catch (error) {
      errorMessage = error instanceof Error ? error.message : 'Unable to create case';
    }
  }

  async function logout() {
    await apiPost('/auth/logout');
    currentUser.set(null);
    await goto('/login');
  }

  onMount(() => {
    void loadDashboard();
  });
</script>

<AppShell title="Dashboard | EvidenceVault AI">
  <svelte:fragment slot="actions">
    <button class="button-secondary" on:click={logout}>Log out</button>
  </svelte:fragment>

  {#if loading}
    <div class="panel p-8 text-sm text-slate-600">Loading your workspace...</div>
  {:else}
    <section class="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
      <div class="space-y-6">
        <div class="panel overflow-hidden p-6">
          <p class="text-xs font-semibold uppercase tracking-[0.2em] text-blue-600">Evidence management</p>
          <h2 class="mt-2 text-3xl font-semibold tracking-tight">Track cases, evidence, OCR text, and timelines in one place.</h2>
          <p class="mt-3 max-w-2xl text-sm text-slate-600">Upload files, extract text automatically, and export a polished PDF report for each case.</p>
        </div>

        <div class="grid gap-4 md:grid-cols-2">
          {#each cases as item}
            <a class="block" href={`/cases/${item.id}`}>
              <CaseCard {item} />
            </a>
          {/each}
          {#if cases.length === 0}
            <div class="panel p-6 text-sm text-slate-600 md:col-span-2">No cases yet. Create the first one on the right.</div>
          {/if}
        </div>
      </div>

      <aside class="space-y-6">
        <div class="panel p-6">
          <h3 class="text-lg font-semibold">Create case</h3>
          <div class="mt-4 space-y-3">
            <input class="field" bind:value={title} placeholder="Case title" />
            <textarea class="field min-h-32" bind:value={description} placeholder="Describe the incident, people involved, and context"></textarea>
            <button class="button-primary w-full" on:click={createCase}>Create case</button>
            {#if errorMessage}
              <p class="text-sm text-red-600">{errorMessage}</p>
            {/if}
          </div>
        </div>
      </aside>
    </section>
  {/if}
</AppShell>
