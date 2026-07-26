<script lang="ts">
  import { createEventDispatcher } from 'svelte';

  import Lightbox from './Lightbox.svelte';
  import { apiDelete, getApiBaseUrl } from '$lib/api';
  import type { Evidence } from '$lib/types';

  export let item: Evidence;
  export let deletable = false;

  const dispatch = createEventDispatcher<{ deleted: { id: string } }>();

  let lightboxOpen = false;
  let confirmingDelete = false;
  let deleting = false;
  let deleteError = '';

  $: baseUrl = `${getApiBaseUrl()}/evidence/${item.id}/download`;
  $: inlineUrl = `${baseUrl}?disposition=inline`;
  $: downloadUrl = baseUrl;

  $: isImage = item.file_type?.startsWith('image/') ?? false;
  $: isPdf = item.file_type === 'application/pdf';
  $: isText = item.file_type === 'text/plain';

  async function confirmDelete() {
    deleting = true;
    deleteError = '';
    try {
      await apiDelete(`/evidence/${item.id}`);
      dispatch('deleted', { id: item.id });
    } catch (error) {
      deleteError = error instanceof Error ? error.message : 'Failed to delete evidence';
      deleting = false;
      confirmingDelete = false;
    }
  }
</script>

<div class="card overflow-hidden">
  <div class="relative h-40 w-full overflow-hidden bg-slate-100 dark:bg-slate-900/40">
    {#if isImage}
      <img src={inlineUrl} alt={item.file_name} loading="lazy" class="h-full w-full object-cover" />
    {:else if isPdf}
      <iframe src={inlineUrl} class="h-full w-full pointer-events-none" title={item.file_name}></iframe>
    {:else if isText}
      <pre class="h-full w-full overflow-hidden whitespace-pre-wrap p-3 text-[11px] leading-snug text-slate-600 dark:text-slate-400">{item.extracted_text || 'No text extracted yet.'}</pre>
    {:else}
      <div class="flex h-full w-full flex-col items-center justify-center gap-1.5 text-slate-400 dark:text-slate-500">
        <svg class="h-8 w-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
        <span class="text-[11px] font-medium uppercase tracking-wide">{item.file_type || 'File'}</span>
      </div>
    {/if}
    <button
      type="button"
      class="group absolute inset-0 flex items-center justify-center bg-slate-900/0 transition-colors duration-200 hover:bg-slate-900/20 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-blue-500"
      on:click={() => (lightboxOpen = true)}
      aria-label={`Preview ${item.file_name}`}
    >
      <span class="rounded-full bg-white/90 p-2 opacity-0 shadow transition-opacity duration-200 group-hover:opacity-100 dark:bg-slate-800/90">
        <svg class="h-4 w-4 text-slate-700 dark:text-slate-200" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"/></svg>
      </span>
    </button>

    {#if deletable}
      <button
        type="button"
        class="absolute right-2 top-2 flex h-7 w-7 items-center justify-center rounded-full bg-white/90 text-slate-500 shadow transition-colors hover:bg-red-50 hover:text-red-600 dark:bg-slate-800/90 dark:text-slate-300 dark:hover:bg-red-500/20 dark:hover:text-red-400"
        on:click={() => (confirmingDelete = true)}
        aria-label={`Delete ${item.file_name}`}
        title="Delete"
      >
        <svg class="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
      </button>
    {/if}
  </div>
  <div class="flex items-center justify-between gap-2 p-3">
    <p class="truncate text-xs font-medium text-slate-700 dark:text-slate-300" title={item.file_name}>{item.file_name}</p>
    <a
      href={downloadUrl}
      class="shrink-0 rounded-lg p-1.5 text-slate-400 transition-colors hover:bg-slate-100 hover:text-slate-700 dark:text-slate-500 dark:hover:bg-slate-700/60 dark:hover:text-white"
      title="Download"
      aria-label={`Download ${item.file_name}`}
    >
      <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v2a2 2 0 002 2h12a2 2 0 002-2v-2M7 10l5 5 5-5M12 15V3"/></svg>
    </a>
  </div>
  {#if deleteError}
    <p class="field-error-text px-3 pb-3">{deleteError}</p>
  {/if}
</div>

<Lightbox bind:open={lightboxOpen} title={item.file_name}>
  {#if isImage}
    <img src={inlineUrl} alt={item.file_name} class="mx-auto max-h-[80vh] w-auto object-contain" />
  {:else if isPdf}
    <iframe src={inlineUrl} class="h-[80vh] w-full border-0" title={item.file_name}></iframe>
  {:else if isText}
    <pre class="max-h-[80vh] overflow-auto whitespace-pre-wrap p-6 text-sm text-slate-700 dark:text-slate-300">{item.extracted_text || 'No text extracted yet.'}</pre>
  {:else}
    <div class="flex flex-col items-center gap-3 p-10 text-center">
      <svg class="h-10 w-10 text-slate-400 dark:text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
      <p class="text-sm text-slate-500 dark:text-slate-400">No inline preview available for this file type.</p>
      <a href={downloadUrl} class="button-primary">Download {item.file_name}</a>
    </div>
  {/if}
</Lightbox>

<Lightbox bind:open={confirmingDelete} title="Delete evidence">
  <div class="p-6 text-center">
    <div class="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-red-50 dark:bg-red-500/10">
      <svg class="h-6 w-6 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" /></svg>
    </div>
    <p class="text-sm font-medium text-slate-900 dark:text-white">Delete "{item.file_name}"?</p>
    <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">This permanently removes the file and its extracted data. This cannot be undone.</p>
    <div class="mt-5 flex justify-center gap-3">
      <button class="button-secondary" on:click={() => (confirmingDelete = false)} disabled={deleting}>Cancel</button>
      <button class="inline-flex items-center justify-center rounded-xl bg-red-600 px-4 py-2 text-sm font-semibold text-white transition-all duration-300 hover:bg-red-500 active:scale-[0.97] disabled:pointer-events-none disabled:opacity-40" on:click={confirmDelete} disabled={deleting}>
        {deleting ? 'Deleting...' : 'Delete'}
      </button>
    </div>
  </div>
</Lightbox>
