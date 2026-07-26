<script lang="ts">
  import { fade, scale } from 'svelte/transition';

  export let open = false;
  export let title = '';

  function close() {
    open = false;
  }

  function handleKeydown(event: KeyboardEvent) {
    if (event.key === 'Escape') close();
  }

  function handleBackdropClick(event: MouseEvent) {
    if (event.target === event.currentTarget) close();
  }
</script>

<svelte:window on:keydown={open ? handleKeydown : undefined} />

{#if open}
  <div
    class="fixed inset-0 z-[100] flex items-center justify-center bg-slate-900/70 p-4 backdrop-blur-sm dark:bg-black/80"
    on:click={handleBackdropClick}
    role="presentation"
    transition:fade={{ duration: 150 }}
  >
    <div
      class="relative flex max-h-[90vh] w-full max-w-4xl flex-col overflow-hidden rounded-2xl bg-white shadow-2xl outline-none dark:bg-slate-800"
      role="dialog"
      aria-modal="true"
      aria-label={title || 'Preview'}
      tabindex="-1"
      transition:scale={{ duration: 150, start: 0.96 }}
    >
      <div class="flex items-center justify-between border-b border-slate-200 px-4 py-3 dark:border-slate-700/60">
        <p class="truncate text-sm font-medium text-slate-700 dark:text-slate-200">{title}</p>
        <button
          type="button"
          class="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg text-slate-400 transition-colors hover:bg-slate-100 hover:text-slate-700 dark:text-slate-500 dark:hover:bg-slate-700/60 dark:hover:text-white"
          on:click={close}
          aria-label="Close preview"
        >
          <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
        </button>
      </div>
      <div class="min-h-0 flex-1 overflow-auto">
        <slot />
      </div>
    </div>
  </div>
{/if}
