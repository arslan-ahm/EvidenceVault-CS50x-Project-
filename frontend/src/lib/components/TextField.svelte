<script lang="ts">
  import type { HTMLInputAttributes } from 'svelte/elements';

  export let id: string;
  export let label = '';
  export let type: 'text' | 'email' | 'tel' | 'url' | 'number' = 'text';
  export let value = '';
  export let placeholder = '';
  export let error: string | null = null;
  export let helper = '';
  export let required = false;
  export let maxlength: number | undefined = undefined;
  export let autocomplete: HTMLInputAttributes['autocomplete'] = undefined;
  export let disabled = false;
  export let forceShowError = false;

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
  <input
    {id}
    {type}
    {placeholder}
    {maxlength}
    {required}
    {disabled}
    {autocomplete}
    class="field"
    class:field-invalid={showError}
    bind:value
    on:blur={() => (touched = true)}
    on:blur
    on:input
    aria-invalid={showError}
    aria-describedby={showError ? `${id}-error` : helper ? `${id}-help` : undefined}
  />
  {#if showError}
    <p id={`${id}-error`} class="field-error-text">
      <svg class="h-3.5 w-3.5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" /></svg>
      {error}
    </p>
  {:else if helper}
    <p id={`${id}-help`} class="field-help">{helper}</p>
  {/if}
</div>
