<script lang="ts">
  import { createEventDispatcher } from 'svelte';

  const dispatch = createEventDispatcher<{ upload: { file: File } }>();
  let selectedFile: File | null = null;

  function submitUpload() {
    if (!selectedFile) return;
    dispatch('upload', { file: selectedFile });
  }

  function handleFileChange(event: Event) {
    const input = event.currentTarget as HTMLInputElement | null;
    selectedFile = input?.files?.[0] ?? null;
  }
</script>

<div class="panel p-5">
  <div class="flex items-center justify-between gap-4">
    <div>
      <h3 class="text-lg font-semibold">Upload evidence</h3>
      <p class="text-sm text-slate-600">Images, PDFs, screenshots, text documents.</p>
    </div>
    <button class="button-primary" on:click={submitUpload} disabled={!selectedFile}>Upload</button>
  </div>
  <input
    class="field mt-4"
    type="file"
    accept=".png,.jpg,.jpeg,.pdf,.tif,.tiff,.txt"
    on:change={handleFileChange}
  />
  {#if selectedFile}
    <p class="mt-3 text-sm text-slate-600">Selected: {selectedFile.name}</p>
  {/if}
</div>
