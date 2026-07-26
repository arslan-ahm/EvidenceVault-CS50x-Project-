<script lang="ts">
  import { formatAbsoluteDateTime, formatRelativeTime } from '$lib/relativeTime';

  export let date: string | Date;
  export let className = '';

  $: relative = formatRelativeTime(date);
  $: absolute = formatAbsoluteDateTime(date);
</script>

<time datetime={typeof date === 'string' ? date : date.toISOString()} title={absolute} class={className}>{relative}</time>
