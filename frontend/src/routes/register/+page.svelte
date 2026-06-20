<script lang="ts">
  import { goto } from '$app/navigation';

  import { apiPost } from '$lib/api';
  import { currentUser } from '$lib/stores/auth';
  import type { User } from '$lib/types';

  let email = '';
  let password = '';
  let errorMessage = '';

  async function submitRegister() {
    errorMessage = '';
    try {
      const user = await apiPost<User>('/auth/register', { email, password });
      currentUser.set(user);
      await goto('/');
    } catch (error) {
      errorMessage = error instanceof Error ? error.message : 'Unable to register';
    }
  }
</script>

<div class="min-h-screen bg-dashboard-grid px-4 py-12 text-ink">
  <div class="mx-auto grid min-h-[calc(100vh-6rem)] max-w-6xl items-center gap-8 lg:grid-cols-2">
    <section class="space-y-4">
      <p class="text-xs font-semibold uppercase tracking-[0.2em] text-blue-600">EvidenceVault AI</p>
      <h1 class="text-4xl font-semibold tracking-tight">Start a protected evidence workspace.</h1>
      <p class="max-w-xl text-slate-600">Create a secure account, then build cases with uploaded evidence, OCR text, and structured timelines.</p>
    </section>

    <section class="panel p-8">
      <h2 class="text-2xl font-semibold">Register</h2>
      <div class="mt-6 space-y-4">
        <input class="field" bind:value={email} type="email" placeholder="Email" />
        <input class="field" bind:value={password} type="password" placeholder="Password" />
        <button class="button-primary w-full" on:click={submitRegister}>Create account</button>
        <p class="text-sm text-slate-600">Already have an account? <a class="font-semibold text-blue-600" href="/login">Log in</a></p>
        {#if errorMessage}
          <p class="text-sm text-red-600">{errorMessage}</p>
        {/if}
      </div>
    </section>
  </div>
</div>
