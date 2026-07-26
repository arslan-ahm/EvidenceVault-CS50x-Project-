<script lang="ts">
  import { createEventDispatcher } from 'svelte';

  import { apiPost } from '$lib/api';

  export let caseId: string;

  const MAX_UPLOAD_MB = 25;
  const ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg', 'pdf', 'tif', 'tiff', 'txt'];

  const dispatch = createEventDispatcher<{ complete: void }>();

  type QueueStatus = 'pending' | 'uploading' | 'done' | 'error';
  type QueueItem = {
    id: string;
    file: File;
    status: QueueStatus;
    error?: string;
    previewUrl?: string;
  };

  let queue: QueueItem[] = [];
  let uploading = false;
  let dragActive = false;
  let inputEl: HTMLInputElement;

  function fileExtension(name: string): string {
    return name.includes('.') ? name.split('.').pop()!.toLowerCase() : '';
  }

  function validateFile(file: File): string | null {
    const ext = fileExtension(file.name);
    if (!ALLOWED_EXTENSIONS.includes(ext)) {
      return `Unsupported type ".${ext || '?'}"`;
    }
    if (file.size > MAX_UPLOAD_MB * 1024 * 1024) {
      return `Too large (${(file.size / (1024 * 1024)).toFixed(1)} MB, max ${MAX_UPLOAD_MB} MB)`;
    }
    return null;
  }

  function addFiles(fileList: FileList | File[]) {
    const files = Array.from(fileList);
    const additions: QueueItem[] = files.map((file) => {
      const error = validateFile(file);
      return {
        id: `${file.name}-${file.size}-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
        file,
        status: error ? 'error' : 'pending',
        error: error ?? undefined,
        previewUrl: file.type.startsWith('image/') ? URL.createObjectURL(file) : undefined
      };
    });
    queue = [...queue, ...additions];
    void processQueue();
  }

  async function processQueue() {
    if (uploading) return;
    uploading = true;
    try {
      let uploadedAny = false;
      for (const item of queue) {
        if (item.status !== 'pending') continue;
        queue = queue.map((q) => (q.id === item.id ? { ...q, status: 'uploading' } : q));
        try {
          const formData = new FormData();
          formData.append('case_id', caseId);
          formData.append('file', item.file);
          await apiPost('/evidence/upload', formData);
          queue = queue.map((q) => (q.id === item.id ? { ...q, status: 'done' } : q));
          uploadedAny = true;
        } catch (error) {
          const message = error instanceof Error ? error.message : 'Upload failed';
          queue = queue.map((q) => (q.id === item.id ? { ...q, status: 'error', error: message } : q));
        }
      }
      if (uploadedAny) {
        dispatch('complete');
      }
    } finally {
      uploading = false;
    }
  }

  function dismiss(id: string) {
    const item = queue.find((q) => q.id === id);
    if (item?.previewUrl) URL.revokeObjectURL(item.previewUrl);
    queue = queue.filter((q) => q.id !== id);
  }

  function handleFileInput(event: Event) {
    const input = event.currentTarget as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      addFiles(input.files);
    }
    input.value = '';
  }

  function handleDrop(event: DragEvent) {
    event.preventDefault();
    dragActive = false;
    if (uploading) return;
    if (event.dataTransfer?.files && event.dataTransfer.files.length > 0) {
      addFiles(event.dataTransfer.files);
    }
  }

  function statusLabel(status: QueueStatus): string {
    switch (status) {
      case 'pending':
        return 'Queued';
      case 'uploading':
        return 'Uploading…';
      case 'done':
        return 'Uploaded';
      case 'error':
        return 'Failed';
    }
  }
</script>

<div class="card p-5">
  <div class="flex items-center justify-between gap-4">
    <div>
      <h3 class="text-lg font-semibold text-slate-900 dark:text-white">Upload evidence</h3>
      <p class="text-sm text-slate-500 dark:text-slate-400">Images, PDFs, screenshots, text documents. Max {MAX_UPLOAD_MB} MB each, multiple files supported.</p>
    </div>
  </div>

  <label class="sr-only" for="evidence-file-input">Choose evidence files to upload</label>
  <div
    class="mt-4 flex flex-col items-center justify-center gap-2 rounded-xl border-2 border-dashed px-4 py-8 text-center transition-colors duration-200 {dragActive ? 'border-blue-400 bg-blue-50 dark:bg-blue-500/10' : 'border-slate-300 dark:border-slate-600/60'} {uploading ? 'pointer-events-none opacity-50' : ''}"
    role="presentation"
    on:dragover|preventDefault={() => (dragActive = true)}
    on:dragleave={() => (dragActive = false)}
    on:drop={handleDrop}
  >
    <svg class="h-8 w-8 text-slate-400 dark:text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M12 12v9m0-9l-3 3m3-3l3 3"/></svg>
    <p class="text-sm text-slate-500 dark:text-slate-400">
      Drag and drop files here, or
      <button type="button" class="font-semibold text-blue-600 hover:text-blue-500 dark:text-blue-400 dark:hover:text-blue-300" on:click={() => inputEl.click()} disabled={uploading}>
        browse
      </button>
    </p>
    <input
      id="evidence-file-input"
      bind:this={inputEl}
      class="hidden"
      type="file"
      multiple
      accept=".png,.jpg,.jpeg,.pdf,.tif,.tiff,.txt"
      disabled={uploading}
      on:change={handleFileInput}
    />
  </div>

  {#if queue.length > 0}
    <ul class="mt-4 space-y-2">
      {#each queue as item (item.id)}
        <li class="flex items-center gap-3 rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 dark:border-slate-700/60 dark:bg-slate-900/40">
          {#if item.previewUrl}
            <img src={item.previewUrl} alt="" class="h-9 w-9 shrink-0 rounded-lg object-cover" />
          {:else}
            <div class="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-slate-200 text-slate-500 dark:bg-slate-700/60 dark:text-slate-400">
              <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
            </div>
          {/if}
          <div class="min-w-0 flex-1">
            <p class="truncate text-sm font-medium text-slate-700 dark:text-slate-200">{item.file.name}</p>
            <p
              class="text-xs"
              class:text-slate-400={item.status === 'pending' || item.status === 'uploading'}
              class:dark:text-slate-500={item.status === 'pending' || item.status === 'uploading'}
              class:text-emerald-600={item.status === 'done'}
              class:dark:text-emerald-400={item.status === 'done'}
              class:text-red-600={item.status === 'error'}
              class:dark:text-red-400={item.status === 'error'}
            >
              {item.error ?? statusLabel(item.status)}
            </p>
          </div>
          {#if item.status === 'uploading'}
            <svg class="h-4 w-4 shrink-0 animate-spin text-blue-500" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path></svg>
          {:else if item.status === 'done'}
            <svg class="h-4 w-4 shrink-0 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
          {:else}
            <button type="button" class="shrink-0 rounded-lg p-1 text-slate-400 hover:bg-slate-200 hover:text-slate-700 dark:hover:bg-slate-700/60 dark:hover:text-white" on:click={() => dismiss(item.id)} aria-label={`Remove ${item.file.name}`}>
              <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
            </button>
          {/if}
        </li>
      {/each}
    </ul>
  {/if}
</div>
