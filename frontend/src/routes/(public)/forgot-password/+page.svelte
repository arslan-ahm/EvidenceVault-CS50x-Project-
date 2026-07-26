<script lang="ts">
  import Alert from '$lib/components/Alert.svelte';
  import TextField from '$lib/components/TextField.svelte';
  import { apiPost } from '$lib/api';
  import type { ForgotPasswordRequest } from '$lib/types';
  import { validateEmail } from '$lib/validation';

  let email = '';
  let loading = false;
  let errorMessage = '';
  let successMessage = '';
  let submitted = false;
  let attemptedSubmit = false;

  $: emailError = validateEmail(email);

  async function submitForgotPassword() {
    errorMessage = '';
    successMessage = '';
    attemptedSubmit = true;
    if (emailError) {
      errorMessage = 'Please enter a valid email address';
      return;
    }
    loading = true;
    try {
      const payload: ForgotPasswordRequest = { email };
      await apiPost<void>('/auth/forgot-password', payload);
      successMessage = 'If an account with that email exists, a password reset link has been sent. Please check your inbox.';
      submitted = true;
    } catch (error) {
      // Don't reveal whether the email exists — show same success msg
      successMessage = 'If an account with that email exists, a password reset link has been sent. Please check your inbox.';
      submitted = true;
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
        Reset your<br>
        <span class="gradient-text">password</span>
      </h1>
      <p class="max-w-xl text-lg text-slate-600 dark:text-slate-400">
        Enter the email address associated with your account and we'll send you
        a link to reset your password.
      </p>
      <div class="hidden space-y-4 lg:block">
        {#each [
          { icon: '🔒', text: 'Secure password reset via email' },
          { icon: '⚡', text: 'Link expires after 1 hour' },
          { icon: '🛡️', text: 'Your account stays protected' },
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
      {#if submitted && successMessage}
        <div class="text-center">
          <div class="mx-auto mb-6 flex h-16 w-16 items-center justify-center rounded-full bg-green-100 dark:bg-green-500/10">
            <svg class="h-8 w-8 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
          </div>
          <h2 class="text-2xl font-bold text-slate-900 dark:text-white">Check your email</h2>
          <p class="mt-3 text-sm text-slate-500 dark:text-slate-400">{successMessage}</p>
          <a href="/login" class="mt-6 inline-flex items-center gap-2 text-sm font-medium text-blue-600 transition-colors hover:text-blue-500 dark:text-blue-400 dark:hover:text-blue-300">
            <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Back to login
          </a>
        </div>
      {:else}
        <h2 class="text-2xl font-bold text-slate-900 dark:text-white">Forgot password</h2>
        <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">We'll send you a recovery link</p>

        <form class="mt-6 space-y-4" on:submit|preventDefault={submitForgotPassword} novalidate>
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

          <button class="button-primary w-full py-3 text-base" type="submit" disabled={loading}>
            {loading ? 'Sending...' : 'Send reset link'}
          </button>

          <p class="text-center text-sm text-slate-500 dark:text-slate-400">
            Remember your password?
            <a class="font-semibold text-blue-600 transition-colors hover:text-blue-500 dark:text-blue-400 dark:hover:text-blue-300" href="/login">Log in</a>
          </p>

          {#if errorMessage}
            <Alert variant="error">{errorMessage}</Alert>
          {/if}
        </form>
      {/if}
    </section>
  </div>
</div>
