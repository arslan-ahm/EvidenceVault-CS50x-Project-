<script lang="ts">
  export let label = 'Loading...';
</script>

<div class="card p-8">
  <div class="flex items-center gap-3">
    <span class="h-5 w-5 shrink-0 animate-spin rounded-full border-2 border-slate-300 border-t-blue-500 dark:border-slate-600 dark:border-t-blue-500" aria-hidden="true"></span>
    <span class="text-sm text-slate-500 dark:text-slate-400">{label}</span>
  </div>
</div>
