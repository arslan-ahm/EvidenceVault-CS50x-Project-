<script lang="ts">
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';

  import ThemeToggle from './ThemeToggle.svelte';
  import { apiPost } from '$lib/api';
  import { currentUser } from '$lib/stores/auth';

  let mobileOpen = false;

  const navItems = [
    {
      href: '/dashboard',
      label: 'Dashboard',
      icon: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6'
    },
    {
      href: '/cases/new',
      label: 'New case',
      icon: 'M12 4v16m8-8H4'
    },
    {
      href: '/explore',
      label: 'Explore',
      icon: 'M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z'
    }
  ];

  $: adminItem = $currentUser?.is_admin
    ? { href: '/admin', label: 'Admin', icon: 'M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z' }
    : null;

  function isActive(href: string): boolean {
    return $page.url.pathname === href || (href !== '/dashboard' && $page.url.pathname.startsWith(href));
  }

  function navLinkClass(href: string): string {
    const base = 'flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors';
    return isActive(href)
      ? `${base} bg-blue-50 text-blue-700 dark:bg-blue-500/10 dark:text-blue-400`
      : `${base} text-slate-600 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800`;
  }

  async function handleLogout() {
    try {
      await apiPost('/auth/logout');
    } catch {
      // ignore
    }
    currentUser.set(null);
    await goto('/');
  }
</script>

<!-- Mobile top bar -->
<div class="fixed inset-x-0 top-0 z-40 flex items-center justify-between border-b border-slate-200 bg-white px-4 py-3 dark:border-slate-800 dark:bg-slate-950 lg:hidden">
  <a href="/dashboard" class="flex items-center gap-2.5">
    <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-blue-500 to-indigo-600 text-xs font-bold text-white">EV</div>
    <span class="text-sm font-bold text-slate-900 dark:text-white">EvidenceVault</span>
  </a>
  <button
    class="flex h-9 w-9 items-center justify-center rounded-lg text-slate-500 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800"
    on:click={() => (mobileOpen = !mobileOpen)}
    aria-label="Toggle navigation"
  >
    <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      {#if mobileOpen}
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
      {:else}
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
      {/if}
    </svg>
  </button>
</div>

<!-- Sidebar -->
<aside
  class="fixed inset-y-0 left-0 z-50 flex w-64 flex-col border-r border-slate-200 bg-white transition-transform duration-200 dark:border-slate-800 dark:bg-slate-950 lg:translate-x-0 {mobileOpen ? 'translate-x-0' : '-translate-x-full'}"
>
  <a href="/dashboard" class="hidden items-center gap-2.5 border-b border-slate-200 px-5 py-5 dark:border-slate-800 lg:flex">
    <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-blue-500 to-indigo-600 text-xs font-bold text-white">EV</div>
    <div>
      <p class="text-sm font-bold leading-none text-slate-900 dark:text-white">EvidenceVault</p>
      <p class="mt-1 text-[10px] font-medium uppercase tracking-[0.15em] text-slate-400 dark:text-slate-500">Workspace</p>
    </div>
  </a>

  <nav class="flex-1 space-y-1 overflow-y-auto px-3 py-4 pt-20 lg:pt-4">
    {#each navItems as item}
      <a
        href={item.href}
        class={navLinkClass(item.href)}
        on:click={() => (mobileOpen = false)}
      >
        <svg class="h-4 w-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d={item.icon}/></svg>
        {item.label}
      </a>
    {/each}

    {#if adminItem}
      <div class="my-3 border-t border-slate-200 dark:border-slate-800"></div>
      <a
        href={adminItem.href}
        class={navLinkClass(adminItem.href)}
        on:click={() => (mobileOpen = false)}
      >
        <svg class="h-4 w-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d={adminItem.icon}/></svg>
        {adminItem.label}
      </a>
    {/if}
  </nav>

  <div class="border-t border-slate-200 p-3 dark:border-slate-800">
    <div class="mb-2 flex items-center justify-between px-1">
      <ThemeToggle />
    </div>
    {#if $currentUser}
      <a
        href="/profile"
        class="flex items-center gap-2.5 rounded-lg px-2 py-2 transition-colors hover:bg-slate-100 dark:hover:bg-slate-800"
        on:click={() => (mobileOpen = false)}
      >
        <div class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 text-xs font-bold text-white">
          {$currentUser.name ? $currentUser.name.charAt(0).toUpperCase() : $currentUser.email.charAt(0).toUpperCase()}
        </div>
        <div class="min-w-0 flex-1">
          <p class="truncate text-xs font-semibold text-slate-900 dark:text-white">{$currentUser.name || 'User'}</p>
          <p class="truncate text-[11px] text-slate-400 dark:text-slate-500">{$currentUser.email}</p>
        </div>
        <button
          type="button"
          class="shrink-0 rounded-md p-1.5 text-slate-400 hover:bg-slate-200 hover:text-slate-700 dark:text-slate-500 dark:hover:bg-slate-700 dark:hover:text-white"
          on:click|preventDefault|stopPropagation={handleLogout}
          aria-label="Log out"
          title="Log out"
        >
          <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/></svg>
        </button>
      </a>
    {/if}
  </div>
</aside>

{#if mobileOpen}
  <button
    type="button"
    class="fixed inset-0 z-40 bg-slate-900/50 lg:hidden"
    on:click={() => (mobileOpen = false)}
    aria-label="Close navigation"
  ></button>
{/if}
