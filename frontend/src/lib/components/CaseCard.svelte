<script lang="ts">
  import type { Case } from '$lib/types';

  export let item: Case;
</script>

<article class="panel p-5 transition hover:-translate-y-0.5 hover:shadow-xl">
  <div class="flex items-start justify-between gap-4">
    <div>
      <h3 class="text-lg font-semibold text-ink">{item.title}</h3>
      <p class="mt-1 line-clamp-2 text-sm text-slate-600">{item.description || 'No description yet.'}</p>
    </div>
    <span class="rounded-full bg-blue-50 px-3 py-1 text-xs font-semibold text-blue-700">Case</span>
  </div>
  <div class="mt-5 text-xs text-slate-500">Created {new Date(item.created_at).toLocaleString()}</div>
</article>
