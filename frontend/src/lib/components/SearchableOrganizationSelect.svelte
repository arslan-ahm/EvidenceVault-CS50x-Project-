<script lang="ts">
  import { createEventDispatcher, onMount } from 'svelte';
  import { fly } from 'svelte/transition';

  import { apiGet, apiPost } from '$lib/api';
  import type { Organization, PublicOrganization } from '$lib/types';

  export let value = '';
  export let placeholder = 'Search or add an organization…';

  const dispatch = createEventDispatcher();

  let organizations: PublicOrganization[] = [];
  let open = false;
  let searchText = '';
  let creating = false;
  let highlightIndex = -1;
  let listboxId = 'org-list-' + Math.random().toString(36).substring(2, 10);

  $: filteredOrganizations = searchText.trim()
    ? organizations.filter((o) => o.name.toLowerCase().includes(searchText.toLowerCase()))
    : organizations;

  $: exactMatch = filteredOrganizations.some((o) => o.name.toLowerCase() === searchText.toLowerCase().trim());
  $: showAddNew = searchText.trim().length > 0 && !exactMatch;

  onMount(async () => {
    try {
      organizations = await apiGet<PublicOrganization[]>('/public/organizations?limit=100');
    } catch {
      // fallback: organizations unavailable
    }
  });

  function selectOrganization(org: PublicOrganization) {
    searchText = org.name;
    value = org.id;
    open = false;
    highlightIndex = -1;
    dispatch('change', { id: org.id, name: org.name });
  }

  async function createOrganization() {
    const name = searchText.trim();
    if (!name || creating) return;
    creating = true;
    try {
      const created = await apiPost<Organization>('/organizations', { name });
      organizations = [...organizations, { ...created, total_reports: 0, resolved_reports: 0, open_reports: 0 }];
      selectOrganization({ ...created, total_reports: 0, resolved_reports: 0, open_reports: 0 });
    } finally {
      creating = false;
    }
  }

  function handleInput() {
    open = true;
    highlightIndex = -1;
    if (value) value = '';
  }

  function handleFocus() {
    open = true;
  }

  function handleBlur() {
    setTimeout(() => {
      open = false;
      highlightIndex = -1;
    }, 200);
  }

  function clearSelection() {
    value = '';
    searchText = '';
    dispatch('change', { id: '', name: '' });
  }
</script>

<div class="relative">
  <div class="relative">
    <input
      type="text"
      class="field w-full pr-10"
      class:rounded-b-none={open && (filteredOrganizations.length > 0 || showAddNew)}
      {placeholder}
      maxlength={120}
      bind:value={searchText}
      on:focus={handleFocus}
      on:blur={handleBlur}
      on:input={handleInput}
      autocomplete="off"
      role="combobox"
      aria-expanded={open}
      aria-controls={listboxId}
      aria-haspopup="listbox"
    />
    {#if value}
      <button
        type="button"
        class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-900 dark:text-slate-500 dark:hover:text-white"
        on:mousedown|preventDefault={clearSelection}
        aria-label="Clear organization selection"
      >
        <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
      </button>
    {:else}
      <div class="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 dark:text-slate-500">
        <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
        </svg>
      </div>
    {/if}
  </div>

  {#if open && (filteredOrganizations.length > 0 || showAddNew)}
    <div
      class="absolute left-0 right-0 z-50 max-h-60 overflow-y-auto rounded-b-xl border border-t-0 border-slate-200 bg-white shadow-2xl backdrop-blur-xl dark:border-slate-600/60 dark:bg-slate-800"
      id={listboxId}
      role="listbox"
      transition:fly={{ y: -4, duration: 120, opacity: 0 }}
    >
      {#each filteredOrganizations as org, i (org.id)}
        <button
          type="button"
          class={[
            'flex w-full items-center gap-3 px-4 py-2.5 text-left text-sm transition-all duration-150',
            highlightIndex === i ? 'bg-blue-50 text-slate-900 dark:bg-blue-500/15 dark:text-white' : 'text-slate-600 dark:text-slate-300',
          ].join(' ')}
          on:mousedown={() => selectOrganization(org)}
          on:mouseenter={() => (highlightIndex = i)}
          role="option"
          aria-selected={highlightIndex === i}
        >
          <span class="flex-1">{org.name}</span>
        </button>
      {/each}

      {#if showAddNew}
        <button
          type="button"
          class="flex w-full items-center gap-3 border-t border-slate-200 px-4 py-2.5 text-left text-sm text-blue-600 transition-all duration-150 hover:bg-blue-50 dark:border-slate-700/60 dark:text-blue-400 dark:hover:bg-blue-500/15"
          on:mousedown={createOrganization}
          disabled={creating}
        >
          <svg class="h-4 w-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          <span>{creating ? 'Creating…' : `Add organization: `}<strong class="text-slate-900 dark:text-white">{!creating ? `"${searchText.trim()}"` : ''}</strong></span>
        </button>
      {/if}
    </div>
  {/if}
</div>
