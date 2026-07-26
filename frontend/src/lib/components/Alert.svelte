<script lang="ts">
  export let variant: 'success' | 'error' | 'info' = 'info';

  const styles: Record<string, string> = {
    success: 'border-green-200 bg-green-50 text-green-700 dark:border-green-500/20 dark:bg-green-500/10 dark:text-green-400',
    error: 'border-red-200 bg-red-50 text-red-700 dark:border-red-500/20 dark:bg-red-500/10 dark:text-red-400',
    info: 'border-slate-200 bg-slate-50 text-slate-600 dark:border-slate-700/60 dark:bg-slate-800/50 dark:text-slate-400'
  };
</script>

<div class={`rounded-lg border px-4 py-3 text-sm ${styles[variant]}`} role={variant === 'error' ? 'alert' : 'status'}>
  <slot />
</div>
