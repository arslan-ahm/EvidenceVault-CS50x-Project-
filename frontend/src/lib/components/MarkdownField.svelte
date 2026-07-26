<script lang="ts">
  import Markdown from './Markdown.svelte';

  export let id: string;
  export let label = '';
  export let value = '';
  export let placeholder = '';
  export let error: string | null = null;
  export let helper = 'Supports Markdown — **bold**, _italic_, lists, links, and code blocks.';
  export let required = false;
  export let maxlength: number | undefined = undefined;
  export let forceShowError = false;
  export let rows = 10;
  export let minHeightClass = 'min-h-48';

  let mode: 'write' | 'preview' = 'write';
  let touched = false;

  $: showError = !!error && (touched || forceShowError);
  $: nearLimit = maxlength !== undefined && value.length >= maxlength * 0.9;
</script>

<div>
  <div class="field-label">
    <label for={id}>{label}{#if required}<span class="ml-0.5 text-red-400">*</span>{/if}</label>
    {#if maxlength !== undefined}
      <span class="field-counter" class:field-counter-warn={nearLimit}>{value.length}/{maxlength}</span>
    {/if}
  </div>

  <div class="mb-2 inline-flex rounded-lg border border-slate-200 bg-slate-100 p-0.5 dark:border-slate-700/60 dark:bg-slate-800/50">
    <button
      type="button"
      class="rounded-md px-3 py-1 text-xs font-semibold transition-colors"
      class:bg-white={mode === 'write'}
      class:dark:bg-slate-700={mode === 'write'}
      class:text-slate-900={mode === 'write'}
      class:dark:text-white={mode === 'write'}
      class:shadow-sm={mode === 'write'}
      class:text-slate-500={mode !== 'write'}
      class:dark:text-slate-400={mode !== 'write'}
      on:click={() => (mode = 'write')}
    >
      Write
    </button>
    <button
      type="button"
      class="rounded-md px-3 py-1 text-xs font-semibold transition-colors"
      class:bg-white={mode === 'preview'}
      class:dark:bg-slate-700={mode === 'preview'}
      class:text-slate-900={mode === 'preview'}
      class:dark:text-white={mode === 'preview'}
      class:shadow-sm={mode === 'preview'}
      class:text-slate-500={mode !== 'preview'}
      class:dark:text-slate-400={mode !== 'preview'}
      on:click={() => (mode = 'preview')}
    >
      Preview
    </button>
  </div>

  {#if mode === 'write'}
    <textarea
      {id}
      {placeholder}
      {maxlength}
      {required}
      {rows}
      class="field {minHeightClass}"
      class:field-invalid={showError}
      bind:value
      on:blur={() => (touched = true)}
      aria-invalid={showError}
    ></textarea>
  {:else}
    <div class="field {minHeightClass} overflow-auto">
      <Markdown content={value} compact />
    </div>
  {/if}

  {#if showError}
    <p class="field-error-text">
      <svg class="h-3.5 w-3.5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" /></svg>
      {error}
    </p>
  {:else if helper}
    <p class="field-help">{helper}</p>
  {/if}
</div>
