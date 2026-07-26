<script lang="ts">
  import Sidebar from '$lib/components/Sidebar.svelte';
</script>

<div class="min-h-screen bg-slate-50 dark:bg-slate-900">
  <Sidebar />
  <main class="min-h-screen pt-16 lg:ml-64 lg:pt-0">
    <div class="mx-auto max-w-6xl px-4 py-8 sm:px-6 lg:px-10 lg:py-10">
      <slot />
    </div>
  </main>
</div>
