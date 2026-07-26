<script lang="ts">
  import { onMount, onDestroy, createEventDispatcher } from 'svelte';
  import { env } from '$env/dynamic/public';
  import { resolvedTheme } from '$lib/stores/theme';

  const dispatch = createEventDispatcher<{ verify: string; expire: void }>();
  const siteKey = env.PUBLIC_TURNSTILE_SITE_KEY || '';

  let container: HTMLDivElement;
  let widgetId: string | undefined;

  const SCRIPT_SRC = 'https://challenges.cloudflare.com/turnstile/v0/api.js';

  function loadScript(): Promise<void> {
    return new Promise((resolve, reject) => {
      if ((window as any).turnstile) {
        resolve();
        return;
      }
      const existing = document.querySelector(`script[src="${SCRIPT_SRC}"]`);
      if (existing) {
        existing.addEventListener('load', () => resolve());
        return;
      }
      const script = document.createElement('script');
      script.src = SCRIPT_SRC;
      script.async = true;
      script.defer = true;
      script.onload = () => resolve();
      script.onerror = () => reject(new Error('Failed to load Turnstile script'));
      document.head.appendChild(script);
    });
  }

  onMount(() => {
    if (!siteKey) return;
    let cancelled = false;
    loadScript().then(() => {
      if (cancelled || !container) return;
      widgetId = (window as any).turnstile.render(container, {
        sitekey: siteKey,
        theme: $resolvedTheme,
        callback: (token: string) => dispatch('verify', token),
        'expired-callback': () => dispatch('expire')
      });
    });
    return () => {
      cancelled = true;
    };
  });

  onDestroy(() => {
    if (widgetId && (window as any).turnstile) {
      (window as any).turnstile.remove(widgetId);
    }
  });
</script>

{#if siteKey}
  <div bind:this={container}></div>
{/if}
