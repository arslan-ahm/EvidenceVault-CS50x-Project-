<script lang="ts">
  import { goto } from '$app/navigation';

  import Alert from '$lib/components/Alert.svelte';
  import PasswordField from '$lib/components/PasswordField.svelte';
  import TextField from '$lib/components/TextField.svelte';
  import Turnstile from '$lib/components/Turnstile.svelte';
  import { apiPost } from '$lib/api';
  import { currentUser } from '$lib/stores/auth';
  import type { User } from '$lib/types';
  import { validateEmail, validateRequired } from '$lib/validation';

  let email = '';
  let password = '';
  let turnstileToken = '';
  let errorMessage = '';
  let loading = false;
  let attemptedSubmit = false;

  $: emailError = validateEmail(email);
  $: passwordError = validateRequired(password, 'Password');
  $: formValid = !emailError && !passwordError;

  async function submitLogin() {
    errorMessage = '';
    attemptedSubmit = true;
    if (!formValid) {
      errorMessage = 'Please fix the highlighted fields before continuing.';
      return;
    }
    loading = true;
    try {
      const user = await apiPost<User>('/auth/login', {
        email,
        password,
        cf_turnstile_response: turnstileToken || undefined
      });
      currentUser.set(user);
      await goto('/dashboard');
    } catch (error) {
      errorMessage = error instanceof Error ? error.message : 'Unable to log in';
    } finally {
      loading = false;
    }
  }
</script>

<div class="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-50 px-4 pb-12 pt-28 dark:from-slate-900 dark:via-slate-800 dark:to-slate-900">
  <div class="mx-auto grid min-h-[calc(100vh-9rem)] max-w-6xl items-center gap-8 lg:grid-cols-2">
    <!-- Left side: branding -->
    <section class="space-y-6 text-center lg:text-left">
      <h1 class="text-4xl font-bold tracking-tight text-slate-900 sm:text-5xl dark:text-white">
        Welcome back to<br>
        <span class="gradient-text">EvidenceVault</span>
      </h1>
      <p class="max-w-xl text-lg text-slate-600 dark:text-slate-400">
        Access your dashboard, manage cases, and collaborate with the security community.
      </p>
      <div class="hidden space-y-4 lg:block">
        {#each [
          { icon: '🔐', text: 'Secured with JWT authentication' },
          { icon: '📁', text: 'Manage your submitted cases' },
          { icon: '👤', text: 'Personalized researcher profile' },
        ] as item}
          <div class="flex items-center gap-3 text-sm text-slate-600 dark:text-slate-300">
            <span>{item.icon}</span>
            <span>{item.text}</span>
          </div>
        {/each}
      </div>
    </section>

    <!-- Right side: form -->
    <section class="card p-8">
      <h2 class="text-2xl font-bold text-slate-900 dark:text-white">Welcome back</h2>
      <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">Log in to your account</p>

      <form class="mt-6 space-y-4" on:submit|preventDefault={submitLogin} novalidate>
        <TextField
          id="email"
          label="Email address"
          type="email"
          bind:value={email}
          placeholder="you@example.com"
          required
          autocomplete="email"
          error={emailError}
          forceShowError={attemptedSubmit}
        />
        <PasswordField
          id="pwd"
          label="Password"
          bind:value={password}
          placeholder="Your password"
          required
          autocomplete="current-password"
          error={passwordError}
          forceShowError={attemptedSubmit}
        />

        <div class="flex items-center justify-end text-sm">
          <a href="/forgot-password" class="font-medium text-blue-600 transition-colors hover:text-blue-500 dark:text-blue-400 dark:hover:text-blue-300">Forgot password?</a>
        </div>

        <Turnstile on:verify={(e) => (turnstileToken = e.detail)} on:expire={() => (turnstileToken = '')} />

        <button class="button-primary w-full py-3 text-base" type="submit" disabled={loading}>
          {loading ? 'Logging in...' : 'Log in'}
        </button>

        <p class="text-center text-sm text-slate-500 dark:text-slate-400">
          Need an account?
          <a class="font-semibold text-blue-600 transition-colors hover:text-blue-500 dark:text-blue-400 dark:hover:text-blue-300" href="/register">Register</a>
        </p>

        {#if errorMessage}
          <Alert variant="error">{errorMessage}</Alert>
        {/if}
      </form>
    </section>
  </div>
</div>
