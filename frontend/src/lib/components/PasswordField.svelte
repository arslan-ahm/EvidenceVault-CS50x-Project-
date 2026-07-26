<script lang="ts">
  import type { HTMLInputAttributes } from 'svelte/elements';
  import { getPasswordStrength } from '$lib/validation';

  export let id: string;
  export let label = '';
  export let value = '';
  export let placeholder = '';
  export let error: string | null = null;
  export let helper = '';
  export let required = false;
  export let autocomplete: HTMLInputAttributes['autocomplete'] = undefined;
  export let disabled = false;
  export let forceShowError = false;
  export let showStrength = false;

  let touched = false;
  let visible = false;

  $: showError = !!error && (touched || forceShowError);
  $: strength = showStrength ? getPasswordStrength(value) : null;
</script>

<div>
  <div class="field-label">
    <label for={id}>{label}{#if required}<span class="ml-0.5 text-red-400">*</span>{/if}</label>
  </div>
  <div class="relative">
    <input
      {id}
      type={visible ? 'text' : 'password'}
      {placeholder}
      {required}
      {disabled}
      {autocomplete}
      class="field pr-11"
      class:field-invalid={showError}
      bind:value
      on:blur={() => (touched = true)}
      on:blur
      on:input
      aria-invalid={showError}
      aria-describedby={showError ? `${id}-error` : helper ? `${id}-help` : undefined}
    />
    <button
      type="button"
      class="password-toggle"
      on:click={() => (visible = !visible)}
      aria-label={visible ? 'Hide password' : 'Show password'}
      aria-pressed={visible}
      tabindex="-1"
    >
      {#if visible}
        <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.542-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21" /></svg>
      {:else}
        <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
      {/if}
    </button>
  </div>

  {#if showStrength && value}
    <div class="mt-2 flex items-center gap-2">
      <div class="flex flex-1 gap-1">
        {#each [1, 2, 3, 4] as segment}
          <div class="strength-track">
            <div class="strength-fill {segment <= Math.max(1, strength?.score ?? 0) ? strength?.colorClass : 'bg-slate-200 dark:bg-slate-700'}" style="width: 100%"></div>
          </div>
        {/each}
      </div>
      <span class="w-16 shrink-0 text-right text-xs font-medium text-slate-500 dark:text-slate-400">{strength?.label}</span>
    </div>
  {/if}

  {#if showError}
    <p id={`${id}-error`} class="field-error-text">
      <svg class="h-3.5 w-3.5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" /></svg>
      {error}
    </p>
  {:else if helper}
    <p id={`${id}-help`} class="field-help">{helper}</p>
  {/if}
</div>
