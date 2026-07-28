<script lang="ts">
  import { goto } from '$app/navigation';

  import Alert from '$lib/components/Alert.svelte';
  import PasswordField from '$lib/components/PasswordField.svelte';
  import TextField from '$lib/components/TextField.svelte';
  import Turnstile from '$lib/components/Turnstile.svelte';
  import { apiPost } from '$lib/api';
  import { currentUser } from '$lib/stores/auth';
  import type { User } from '$lib/types';
  import { validateEmail, validateLength, validateMatch, validatePasswordStrength } from '$lib/validation';

  let name = '';
  let occupation = '';
  let email = '';
  let password = '';
  let confirmPassword = '';
  let turnstileToken = '';
  let errorMessage = '';
  let loading = false;
  let attemptedSubmit = false;

  $: nameError = validateLength(name, { min: 2, max: 80 }, 'Full name');
  $: occupationError = occupation ? validateLength(occupation, { max: 100 }, 'Occupation') : null;
  $: emailError = validateEmail(email);
  $: passwordError = validatePasswordStrength(password);
  $: confirmPasswordError = !confirmPassword
    ? 'Please confirm your password'
    : validateMatch(confirmPassword, password, 'Passwords');
  $: formValid = !nameError && !occupationError && !emailError && !passwordError && !confirmPasswordError;

  async function submitRegister() {
    errorMessage = '';
    attemptedSubmit = true;
    if (!formValid) {
      errorMessage = 'Please fix the highlighted fields before continuing.';
      return;
    }
    loading = true;
    try {
      const user = await apiPost<User>('/auth/register', {
        email,
        password,
        name,
        occupation: occupation || null,
        cf_turnstile_response: turnstileToken || undefined
      });
      currentUser.set(user);
      await goto('/dashboard');
    } catch (error) {
      errorMessage = error instanceof Error ? error.message : 'Unable to register';
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
        Join the<br>
        <span class="gradient-text">consumer protection</span> community
      </h1>
      <p class="max-w-xl text-lg text-slate-600 dark:text-slate-400">
        Create a free account to file scam reports and complaints, track their progress,
        and help protect others in the community.
      </p>
      <div class="hidden space-y-4 lg:block">
        {#each [
          { icon: '🛡️', text: 'File detailed scam & complaint reports' },
          { icon: '📊', text: 'Track complaint progress with timelines' },
          { icon: '🔍', text: 'Browse community-verified complaints' },
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
      <h2 class="text-2xl font-bold text-slate-900 dark:text-white">Create account</h2>
      <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">Start reporting scams and complaints</p>

      <form class="mt-6 space-y-4" on:submit|preventDefault={submitRegister} novalidate>
        <div class="grid gap-4 sm:grid-cols-2">
          <TextField
            id="name"
            label="Full name"
            bind:value={name}
            placeholder="Jane Doe"
            required
            maxlength={80}
            autocomplete="name"
            error={nameError}
            forceShowError={attemptedSubmit}
          />
          <TextField
            id="occ"
            label="Occupation (optional)"
            bind:value={occupation}
            placeholder="Student, Freelancer, Shop Owner..."
            maxlength={100}
            autocomplete="organization-title"
            error={occupationError}
            forceShowError={attemptedSubmit}
          />
        </div>
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
        <div class="grid gap-4 sm:grid-cols-2">
          <PasswordField
            id="pwd"
            label="Password"
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
            label="Confirm password"
            bind:value={confirmPassword}
            placeholder="Repeat password"
            required
            autocomplete="new-password"
            error={confirmPasswordError}
            forceShowError={attemptedSubmit}
          />
        </div>

        <Turnstile on:verify={(e) => (turnstileToken = e.detail)} on:expire={() => (turnstileToken = '')} />

        <button class="button-primary w-full py-3 text-base" type="submit" disabled={loading}>
          {loading ? 'Creating account...' : 'Create account'}
        </button>

        <p class="text-center text-sm text-slate-500 dark:text-slate-400">
          Already have an account?
          <a class="font-semibold text-blue-600 transition-colors hover:text-blue-500 dark:text-blue-400 dark:hover:text-blue-300" href="/login">Log in</a>
        </p>

        {#if errorMessage}
          <Alert variant="error">{errorMessage}</Alert>
        {/if}
      </form>
    </section>
  </div>
</div>
