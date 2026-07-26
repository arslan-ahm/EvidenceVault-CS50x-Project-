<script lang="ts">
  import { setTheme, themePreference, type ThemePreference } from '$lib/stores/theme';

  const options: { value: ThemePreference; label: string }[] = [
    { value: 'light', label: 'Light theme' },
    { value: 'system', label: 'System theme' },
    { value: 'dark', label: 'Dark theme' }
  ];
</script>

<div
  class="inline-flex items-center gap-0.5 rounded-lg border border-slate-200 bg-slate-100 p-0.5 dark:border-slate-700/60 dark:bg-slate-800/50"
  role="radiogroup"
  aria-label="Theme"
>
  {#each options as option}
    <button
      type="button"
      class="flex h-7 w-7 items-center justify-center rounded-md text-slate-500 transition-all duration-200 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white"
      class:bg-white={$themePreference === option.value}
      class:dark:bg-slate-700={$themePreference === option.value}
      class:text-slate-900={$themePreference === option.value}
      class:dark:text-white={$themePreference === option.value}
      class:shadow-sm={$themePreference === option.value}
      role="radio"
      aria-checked={$themePreference === option.value}
      aria-label={option.label}
      title={option.label}
      on:click={() => setTheme(option.value)}
    >
      {#if option.value === 'light'}
        <svg class="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"/></svg>
      {:else if option.value === 'dark'}
        <svg class="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 1020.354 15.354z"/></svg>
      {:else}
        <svg class="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/></svg>
      {/if}
    </button>
  {/each}
</div>
