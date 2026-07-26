<script lang="ts">
  import { marked } from 'marked';
  import DOMPurify from 'dompurify';

  export let content = '';
  export let compact = false;

  marked.setOptions({ breaks: true, gfm: true });

  $: html = content.trim() ? DOMPurify.sanitize(marked.parse(content, { async: false }) as string) : '';
</script>

<div class="prose prose-slate max-w-none dark:prose-invert {compact ? 'prose-sm' : ''} prose-headings:font-display prose-a:text-blue-600 dark:prose-a:text-blue-400 prose-code:before:content-none prose-code:after:content-none">
  {#if html}
    {@html html}
  {:else}
    <p class="italic text-slate-400 dark:text-slate-500">No description provided.</p>
  {/if}
</div>
