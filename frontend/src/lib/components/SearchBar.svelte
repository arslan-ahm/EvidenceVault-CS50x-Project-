<script lang="ts">
  import { createEventDispatcher } from 'svelte';

  export let value = '';
  const dispatch = createEventDispatcher<{ search: string }>();
</script>

<div class="panel flex flex-col gap-3 p-5 sm:flex-row sm:items-center">
  <input class="field flex-1" bind:value placeholder="Search evidence text, case titles, metadata" />
  <button class="button-primary" on:click={() => dispatch('search', value)}>Search</button>
</div>
