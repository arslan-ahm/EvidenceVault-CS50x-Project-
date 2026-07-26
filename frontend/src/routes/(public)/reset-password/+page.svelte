<script lang="ts">
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import Alert from '$lib/components/Alert.svelte';
  import PasswordField from '$lib/components/PasswordField.svelte';
  import { apiPost } from '$lib/api';
  import type { ResetPasswordRequest } from '$lib/types';
  import { validateMatch, validatePasswordStrength } from '$lib/validation';

  let password = '';
  let confirmPassword = '';
  let loading = false;
  let errorMessage = '';
  let successMessage = '';
  let submitted = false;
  let attemptedSubmit = false;

  $: token = $page.url.searchParams.get('token');
  $: passwordError = validatePasswordStrength(password);
  $: confirmPasswordError = !confirmPassword ? 'Please confirm your password' : validateMatch(confirmPassword, password, 'Passwords');

  async function submitResetPassword() {
    errorMessage = '';
    attemptedSubmit = true;
    if (!token) {
      errorMessage = 'Invalid or missing reset token. Please request a new password reset link.';
      return;
    }
    if (passwordError || confirmPasswordError) {
      errorMessage = 'Please fix the highlighted fields before continuing.';
      return;
    }
    loading = true;
    try {
      const payload: ResetPasswordRequest = { token, password };
      await apiPost<void>('/auth/reset-password', payload);
      successMessage = 'Your password has been successfully reset.';
      submitted = true;
    } catch (error) {
      errorMessage = error instanceof Error ? error.message : 'Unable to reset password. The link may have expired.';
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
        Set a new<br>
        <span class="gradient-text">password</span>
      </h1>
      <p class="max-w-xl text-lg text-slate-600 dark:text-slate-400">
        Choose a strong, unique password for your EvidenceVault account.
        Make sure it's at least 8 characters.
      </p>
      <div class="hidden space-y-4 lg:block">
        {#each [
          { icon: '🔒', text: 'Encrypted and securely stored' },
          { icon: '⚡', text: 'Instant activation after reset' },
          { icon: '🛡️', text: 'Session tokens remain valid' },
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
      {#if !token && !submitted}
        <div class="text-center">
          <div class="mx-auto mb-6 flex h-16 w-16 items-center justify-center rounded-full bg-red-100 dark:bg-red-500/10">
            <svg class="h-8 w-8 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          </div>
          <h2 class="text-2xl font-bold text-slate-900 dark:text-white">Invalid link</h2>
          <p class="mt-3 text-sm text-slate-500 dark:text-slate-400">This password reset link is invalid or has expired. Please request a new one.</p>
          <a href="/forgot-password" class="mt-6 inline-flex items-center gap-2 text-sm font-medium text-blue-600 transition-colors hover:text-blue-500 dark:text-blue-400 dark:hover:text-blue-300">
            Request new reset link
          </a>
        </div>
      {:else if submitted && successMessage}
        <div class="text-center">
          <div class="mx-auto mb-6 flex h-16 w-16 items-center justify-center rounded-full bg-green-100 dark:bg-green-500/10">
            <svg class="h-8 w-8 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h2 class="text-2xl font-bold text-slate-900 dark:text-white">Password reset!</h2>
          <p class="mt-3 text-sm text-slate-500 dark:text-slate-400">{successMessage}</p>
          <a href="/login" class="mt-6 inline-flex items-center gap-2 text-sm font-medium text-blue-600 transition-colors hover:text-blue-500 dark:text-blue-400 dark:hover:text-blue-300">
            <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Go to login
          </a>
        </div>
      {:else}
        <h2 class="text-2xl font-bold text-slate-900 dark:text-white">Reset password</h2>
        <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">Enter your new password below</p>

        <form class="mt-6 space-y-4" on:submit|preventDefault={submitResetPassword} novalidate>
          <PasswordField
            id="pwd"
            label="New password"
            bind:value={password}
            placeholder="Min. 8 characters"
            required
            autocomplete="new-password"
            error={passwordError}
            forceShowError={attemptedSubmit}
            showStrength
          />
          <PasswordField
            id="cpwd"
            label="Confirm new password"
            bind:value={confirmPassword}
            placeholder="Repeat new password"
            required
            autocomplete="new-password"
            error={confirmPasswordError}
            forceShowError={attemptedSubmit}
          />

          <button class="button-primary w-full py-3 text-base" type="submit" disabled={loading}>
            {loading ? 'Resetting...' : 'Reset password'}
          </button>

          <p class="text-center text-sm text-slate-500 dark:text-slate-400">
            <a class="font-semibold text-blue-600 transition-colors hover:text-blue-500 dark:text-blue-400 dark:hover:text-blue-300" href="/login">Back to login</a>
          </p>

          {#if errorMessage}
            <Alert variant="error">{errorMessage}</Alert>
          {/if}
        </form>
      {/if}
    </section>
  </div>
</div>
