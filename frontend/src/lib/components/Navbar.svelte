<script lang="ts">
  import { fly } from 'svelte/transition';
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import { gsap } from 'gsap';

  import ThemeToggle from './ThemeToggle.svelte';
  import { apiPost } from '$lib/api';
  import { currentUser } from '$lib/stores/auth';

  let navRef: HTMLElement;
  let mobileMenuOpen = false;
  let profileDropdownOpen = false;
  let profileDropdownEl: HTMLDivElement;

  const navLinks = [
    { label: 'Explore', href: '/explore' },
  ];

  function handleLogout() {
    profileDropdownOpen = false;
    apiPost('/auth/logout').then(() => {
      currentUser.set(null);
      goto('/');
    });
  }

  function isActive(href: string): boolean {
    return $page.url.pathname.startsWith(href) && href !== '/';
  }

  function navLinkEnter(el: Element) {
    gsap.fromTo(el, { opacity: 0, y: -8 }, { opacity: 1, y: 0, duration: 0.3, ease: 'power2.out' });
    return {};
  }

  function toggleDropdown() {
    profileDropdownOpen = !profileDropdownOpen;
  }

  function handleClickOutside(event: MouseEvent) {
    if (profileDropdownEl && !profileDropdownEl.contains(event.target as Node)) {
      profileDropdownOpen = false;
    }
  }

  function handleKeydown(event: KeyboardEvent) {
    if (event.key === 'Escape') {
      profileDropdownOpen = false;
    }
  }
</script>

<svelte:window on:click={handleClickOutside} on:keydown={handleKeydown} />

<header class="fixed left-0 right-0 top-0 z-50 border-b border-slate-200 bg-white/80 backdrop-blur-xl dark:border-slate-800/60 dark:bg-slate-900/80">
  <div class="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 sm:px-6 lg:px-8">
    <!-- Logo -->
    <a href="/" class="group flex items-center gap-3">
      <div class="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 text-sm font-bold text-white shadow-lg shadow-blue-500/20 transition-all duration-300 group-hover:shadow-blue-500/30 group-hover:scale-105">
        EV
      </div>
      <div class="hidden sm:block">
        <p class="text-sm font-bold tracking-tight text-slate-900 dark:text-white">EvidenceVault</p>
        <p class="-mt-0.5 text-[10px] font-medium uppercase tracking-[0.2em] text-blue-600 dark:text-blue-400">Disclosure Intelligence</p>
      </div>
    </a>

    <!-- Desktop Navigation -->
    <nav class="hidden items-center gap-1 md:flex" bind:this={navRef}>
      {#each navLinks as link}
        <a
          href={link.href}
          class="relative rounded-lg px-3 py-2 text-sm font-medium text-slate-600 transition-all duration-300 hover:text-slate-900 dark:text-slate-300 dark:hover:text-white"
          class:nav-active={isActive(link.href)}
          in:navLinkEnter
        >
          {link.label}
          {#if isActive(link.href)}
            <span class="absolute inset-0 rounded-lg bg-slate-900/5 dark:bg-white/5"></span>
          {/if}
        </a>
      {/each}

      <!-- Dashboard link - only visible when logged in -->
      {#if $currentUser && $page.url.pathname !== '/dashboard'}
        <a
          href="/dashboard"
          class="relative rounded-lg px-3 py-2 text-sm font-medium text-slate-600 transition-all duration-300 hover:text-slate-900 dark:text-slate-300 dark:hover:text-white"
        >
          <span class="relative z-10 flex items-center gap-1.5">
            <svg class="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/></svg>
            Dashboard
          </span>
        </a>
      {/if}

      {#if $currentUser?.is_admin && $page.url.pathname !== '/admin'}
        <a
          href="/admin"
          class="relative rounded-lg px-3 py-2 text-sm font-medium text-slate-600 transition-all duration-300 hover:text-slate-900 dark:text-slate-300 dark:hover:text-white"
        >
          <span class="relative z-10 flex items-center gap-1.5">
            <svg class="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/></svg>
            Admin
          </span>
        </a>
      {/if}

      <!-- Auth area -->
      <div class="ml-4 flex items-center gap-2">
        <ThemeToggle />
        {#if $currentUser}
          <!-- Profile avatar dropdown -->
          <div class="relative" bind:this={profileDropdownEl}>
            <button
              class="flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-sm font-medium text-slate-600 transition-all duration-300 hover:border-blue-400 hover:text-slate-900 dark:border-slate-700/60 dark:bg-slate-800/50 dark:text-slate-300 dark:hover:border-blue-500/30 dark:hover:text-white"
              on:click={toggleDropdown}
              aria-haspopup="true"
              aria-expanded={profileDropdownOpen}
            >
              <div class="flex h-7 w-7 items-center justify-center rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 text-[11px] font-bold text-white shadow-lg shadow-blue-500/20">
                {$currentUser.name ? $currentUser.name.charAt(0).toUpperCase() : $currentUser.email.charAt(0).toUpperCase()}
              </div>
              <span class="hidden lg:inline">{$currentUser.name || $currentUser.email}</span>
              <svg class="h-3.5 w-3.5 text-slate-400 transition-transform duration-200 dark:text-slate-500" class:rotate-180={profileDropdownOpen} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              </svg>
            </button>

            <!-- Dropdown menu -->
            {#if profileDropdownOpen}
              <div
                class="absolute right-0 top-full mt-2 w-56 origin-top-right rounded-xl border border-slate-200 bg-white/95 p-1.5 shadow-2xl shadow-slate-900/10 backdrop-blur-xl dark:border-slate-700/60 dark:bg-slate-800/90 dark:shadow-black/40"
                transition:fly={{ y: -8, duration: 150, opacity: 0 }}
              >
                <div class="border-b border-slate-200 px-3 py-2.5 dark:border-slate-700/60">
                  <p class="text-sm font-semibold text-slate-900 truncate dark:text-white">{$currentUser.name || 'User'}</p>
                  <p class="truncate text-xs text-slate-500 dark:text-slate-400">{$currentUser.email}</p>
                </div>
                <div class="mt-1 space-y-0.5">
                  <a
                    href="/profile"
                    class="flex items-center gap-2.5 rounded-lg px-3 py-2 text-sm font-medium text-slate-600 transition-colors hover:bg-slate-100 hover:text-slate-900 dark:text-slate-300 dark:hover:bg-slate-700/50 dark:hover:text-white"
                    on:click={() => (profileDropdownOpen = false)}
                  >
                    <svg class="h-4 w-4 text-slate-400 dark:text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/></svg>
                    Profile
                  </a>
                </div>
                <div class="mt-1 border-t border-slate-200 pt-1 dark:border-slate-700/60">
                  <button
                    class="flex w-full items-center gap-2.5 rounded-lg px-3 py-2 text-sm font-medium text-red-600 transition-colors hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-500/10"
                    on:click={handleLogout}
                  >
                    <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/></svg>
                    Log out
                  </button>
                </div>
              </div>
            {/if}
          </div>
        {:else}
          <a href="/login" class="button-secondary px-4 py-2 text-xs sm:text-sm">
            Log in
          </a>
          <a href="/register" class="button-primary px-4 py-2 text-xs sm:text-sm">
            Register
          </a>
        {/if}
      </div>
    </nav>

    <!-- Mobile menu button -->
    <div class="flex items-center gap-2 md:hidden">
      <ThemeToggle />
      <button
        class="flex h-9 w-9 items-center justify-center rounded-lg border border-slate-200 bg-white text-slate-500 transition-colors hover:text-slate-900 dark:border-slate-700/60 dark:bg-slate-800/50 dark:text-slate-400 dark:hover:text-white"
        on:click={() => (mobileMenuOpen = !mobileMenuOpen)}
        aria-label="Toggle menu"
      >
        <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          {#if mobileMenuOpen}
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
          {:else}
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
          {/if}
        </svg>
      </button>
    </div>
  </div>

  <!-- Mobile menu -->
  {#if mobileMenuOpen}
    <div class="border-t border-slate-200 bg-white/95 backdrop-blur-xl dark:border-slate-800/60 dark:bg-slate-900/95 md:hidden">
      <div class="space-y-1 px-4 pb-4 pt-2">
        {#each navLinks as link}
          <a
            href={link.href}
            class="block rounded-lg px-3 py-2 text-sm font-medium text-slate-600 transition-colors hover:bg-slate-100 hover:text-slate-900 dark:text-slate-300 dark:hover:bg-slate-800/50 dark:hover:text-white"
            on:click={() => (mobileMenuOpen = false)}
          >
            {link.label}
          </a>
        {/each}

        {#if $currentUser && $page.url.pathname !== '/dashboard'}
          <a
            href="/dashboard"
            class="block rounded-lg px-3 py-2 text-sm font-medium text-slate-600 transition-colors hover:bg-slate-100 hover:text-slate-900 dark:text-slate-300 dark:hover:bg-slate-800/50 dark:hover:text-white"
            on:click={() => (mobileMenuOpen = false)}
          >
            Dashboard
          </a>
        {/if}

        {#if $currentUser?.is_admin && $page.url.pathname !== '/admin'}
          <a
            href="/admin"
            class="block rounded-lg px-3 py-2 text-sm font-medium text-slate-600 transition-colors hover:bg-slate-100 hover:text-slate-900 dark:text-slate-300 dark:hover:bg-slate-800/50 dark:hover:text-white"
            on:click={() => (mobileMenuOpen = false)}
          >
            Admin
          </a>
        {/if}

        {#if $currentUser}
          <a
            href="/profile"
            class="block rounded-lg px-3 py-2 text-sm font-medium text-slate-600 transition-colors hover:bg-slate-100 hover:text-slate-900 dark:text-slate-300 dark:hover:bg-slate-800/50 dark:hover:text-white"
            on:click={() => (mobileMenuOpen = false)}
          >
            Profile
          </a>
          <button
            class="mt-2 w-full rounded-lg px-3 py-2 text-left text-sm font-medium text-red-600 transition-colors hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-500/10"
            on:click={() => { mobileMenuOpen = false; handleLogout(); }}
          >
            Log out
          </button>
        {:else}
          <a
            href="/login"
            class="mt-2 block rounded-lg px-3 py-2 text-sm font-medium text-slate-600 transition-colors hover:bg-slate-100 hover:text-slate-900 dark:text-slate-300 dark:hover:bg-slate-800/50 dark:hover:text-white"
            on:click={() => (mobileMenuOpen = false)}
          >
            Log in
          </a>
          <a
            href="/register"
            class="mt-1 block rounded-lg bg-gradient-to-r from-blue-600 to-indigo-600 px-3 py-2 text-center text-sm font-medium text-white transition-colors hover:from-blue-500 hover:to-indigo-500"
            on:click={() => (mobileMenuOpen = false)}
          >
            Register
          </a>
        {/if}
      </div>
    </div>
  {/if}
</header>

<style>
  :global([data-theme='dark'] .nav-active) {
    color: white;
  }

  :global([data-theme='light'] .nav-active),
  :global(:root:not([data-theme]) .nav-active) {
    color: #0f172a;
  }
</style>
