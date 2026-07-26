<script lang="ts">
  import { createEventDispatcher } from 'svelte';

  export let value = '';
  const dispatch = createEventDispatcher<{ search: string }>();
</script>

<div class="card flex flex-col gap-3 p-5 sm:flex-row sm:items-center">
  <label class="sr-only" for="evidence-search">Search evidence text, case titles, metadata</label>
  <input
    id="evidence-search"
    class="field flex-1"
    bind:value
    maxlength={200}
    placeholder="Search evidence text, case titles, metadata"
    on:keydown={(e) => e.key === 'Enter' && dispatch('search', value)}
  />
  <button class="button-primary" on:click={() => dispatch('search', value)}>Search</button>
</div>
