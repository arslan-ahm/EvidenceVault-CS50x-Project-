<script lang="ts">
  import { currentUser } from '$lib/stores/auth';

  export let title = 'EvidenceVault AI';
</script>

<svelte:head>
  <title>{title}</title>
</svelte:head>

<div class="min-h-screen bg-dashboard-grid text-ink">
  <div class="mx-auto flex min-h-screen w-full max-w-7xl flex-col px-4 py-6 sm:px-6 lg:px-8">
    <header class="panel mb-6 flex items-center justify-between px-5 py-4">
      <div>
        <p class="text-xs font-semibold uppercase tracking-[0.2em] text-blue-600">EvidenceVault AI</p>
        <h1 class="text-xl font-semibold">Secure evidence workspace</h1>
      </div>
      <div class="flex items-center gap-3 text-sm text-slate-600">
        {#if $currentUser}
          <span class="rounded-full bg-blue-50 px-3 py-1 font-medium text-blue-700">{$currentUser.email}</span>
        {/if}
        <slot name="actions" />
      </div>
    </header>
    <main class="flex-1">
      <slot />
    </main>
  </div>
</div>
