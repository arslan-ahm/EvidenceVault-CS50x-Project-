<script lang="ts">
  import { goto } from '$app/navigation';
  import Alert from '$lib/components/Alert.svelte';
  import PasswordField from '$lib/components/PasswordField.svelte';
  import TextField from '$lib/components/TextField.svelte';
  import { apiDelete, apiGet, apiPost, apiPut } from '$lib/api';
  import { formatAbsoluteDate } from '$lib/relativeTime';
  import { currentUser } from '$lib/stores/auth';
  import type { User, UserUpdate, ChangePasswordRequest } from '$lib/types';
  import { validateLength, validateMatch, validatePasswordStrength, validateRequired } from '$lib/validation';

  $: user = $currentUser;

  // Profile edit state
  let editName = '';
  let editOccupation = '';
  let editLoading = false;
  let editMessage = '';
  let editError = '';
  let editAttemptedSubmit = false;

  $: editNameError = validateLength(editName, { min: 2, max: 80 }, 'Full name');
  $: editOccupationError = editOccupation ? validateLength(editOccupation, { max: 100 }, 'Occupation') : null;

  // Change password state
  let currentPassword = '';
  let newPassword = '';
  let confirmNewPassword = '';
  let pwdLoading = false;
  let pwdMessage = '';
  let pwdError = '';
  let pwdAttemptedSubmit = false;

  $: currentPasswordError = validateRequired(currentPassword, 'Current password');
  $: newPasswordError = validatePasswordStrength(newPassword);
  $: confirmNewPasswordError = !confirmNewPassword
    ? 'Please confirm your new password'
    : validateMatch(confirmNewPassword, newPassword, 'Passwords');

  // Image upload
  let uploadLoading = false;

  function initEditFields() {
    if (user) {
      editName = user.name || '';
      editOccupation = user.occupation || '';
    }
  }

  $: if (user) {
    initEditFields();
  }

  async function saveProfile() {
    editError = '';
    editMessage = '';
    editAttemptedSubmit = true;
    if (editNameError || editOccupationError) {
      editError = 'Please fix the highlighted fields before continuing.';
      return;
    }
    editLoading = true;
    try {
      const payload: UserUpdate = {
        name: editName.trim(),
        occupation: editOccupation.trim() || null,
      };
      const updated = await apiPut<User>('/auth/profile', payload);
      currentUser.set(updated);
      editMessage = 'Profile updated successfully.';
    } catch (error) {
      editError = error instanceof Error ? error.message : 'Failed to update profile';
    } finally {
      editLoading = false;
    }
  }

  async function changePassword() {
    pwdError = '';
    pwdMessage = '';
    pwdAttemptedSubmit = true;
    if (currentPasswordError || newPasswordError || confirmNewPasswordError) {
      pwdError = 'Please fix the highlighted fields before continuing.';
      return;
    }
    pwdLoading = true;
    try {
      const payload: ChangePasswordRequest = {
        current_password: currentPassword,
        new_password: newPassword,
      };
      await apiPost('/auth/change-password', payload);
      pwdMessage = 'Password changed successfully.';
      currentPassword = '';
      newPassword = '';
      confirmNewPassword = '';
      pwdAttemptedSubmit = false;
    } catch (error) {
      pwdError = error instanceof Error ? error.message : 'Failed to change password';
    } finally {
      pwdLoading = false;
    }
  }

  async function handleImageUpload(event: Event) {
    const input = event.target as HTMLInputElement;
    if (!input.files || !input.files[0]) return;
    const file = input.files[0];
    if (file.size > 5 * 1024 * 1024) {
      editError = 'Image must be under 5 MB';
      return;
    }
    uploadLoading = true;
    editError = '';
    editMessage = '';
    try {
      const formData = new FormData();
      formData.append('file', file);
      const result = await apiPost<{ url: string }>('/auth/profile-image', formData);
      const updated = await apiPut<User>('/auth/profile', { profile_image_url: result.url });
      currentUser.set(updated);
      editMessage = 'Profile image updated.';
    } catch (error) {
      editError = error instanceof Error ? error.message : 'Failed to upload image';
    } finally {
      uploadLoading = false;
    }
  }

  let deleteConfirmOpen = false;
  let deleteLoading = false;
  let deleteError = '';

  async function confirmDeleteAccount() {
    deleteLoading = true;
    deleteError = '';
    try {
      await apiDelete('/auth/me');
      currentUser.set(null);
      await goto('/');
    } catch (error) {
      deleteError = error instanceof Error ? error.message : 'Failed to delete account';
      deleteLoading = false;
    }
  }

</script>

<svelte:head>
  <title>Profile | EvidenceVault</title>
</svelte:head>

<div class="mb-6 flex items-center gap-3">
  <a href="/dashboard" class="flex items-center gap-1.5 text-sm text-slate-500 transition-colors hover:text-slate-900 dark:text-slate-400 dark:hover:text-white">
    <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
    </svg>
    Dashboard
  </a>
  <span class="text-slate-300 dark:text-slate-700">/</span>
  <span class="text-sm text-slate-900 dark:text-white">Profile</span>
</div>

{#if !user}
  <div class="flex min-h-[40vh] items-center justify-center">
    <div class="text-center">
      <div class="skeleton mx-auto mb-4 h-12 w-12 !rounded-full"></div>
      <div class="skeleton mx-auto mb-2 h-4 w-48 !rounded-md"></div>
      <div class="skeleton mx-auto h-3 w-32 !rounded-md"></div>
    </div>
  </div>
{:else}
  <div class="grid gap-8 lg:grid-cols-3">
        <!-- Left column: Profile card -->
        <div class="lg:col-span-1">
          <div class="card p-6 text-center">
            <!-- Avatar -->
            <div class="relative mx-auto mb-4 h-28 w-28">
              {#if user.profile_image_url}
                <img
                  src={user.profile_image_url}
                  alt="Profile"
                  class="h-full w-full rounded-full object-cover ring-4 ring-slate-200 dark:ring-slate-700/60"
                />
              {:else}
                <div class="flex h-full w-full items-center justify-center rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 text-4xl font-bold text-white ring-4 ring-slate-200 dark:ring-slate-700/60">
                  {user.name ? user.name.charAt(0).toUpperCase() : user.email.charAt(0).toUpperCase()}
                </div>
              {/if}
              <label
                for="avatar-upload"
                class="absolute -bottom-1 -right-1 flex h-8 w-8 cursor-pointer items-center justify-center rounded-full border border-slate-200 bg-white text-slate-500 shadow-lg transition-all duration-300 hover:bg-blue-600 hover:text-white dark:border-slate-600/60 dark:bg-slate-700 dark:text-slate-300 {uploadLoading ? 'pointer-events-none opacity-50' : ''}"
              >
                <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              </label>
              <input id="avatar-upload" type="file" accept="image/*" class="hidden" on:change={handleImageUpload} />
            </div>

            <h2 class="text-xl font-bold text-slate-900 dark:text-white">{user.name || 'User'}</h2>
            {#if user.occupation}
              <p class="mt-0.5 text-sm text-slate-500 dark:text-slate-400">{user.occupation}</p>
            {/if}
            <p class="mt-3 text-xs text-slate-400 dark:text-slate-500">
              Member since {formatAbsoluteDate(user.created_at)}
            </p>
          </div>
        </div>

        <!-- Right column: Edit forms -->
        <div class="space-y-6 lg:col-span-2">
          <!-- Edit Profile -->
          <div class="card p-6">
            <h3 class="text-lg font-bold text-slate-900 dark:text-white">Edit Profile</h3>
            <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">Update your personal information</p>

            {#if editMessage}
              <div class="mt-4"><Alert variant="success">{editMessage}</Alert></div>
            {/if}
            {#if editError}
              <div class="mt-4"><Alert variant="error">{editError}</Alert></div>
            {/if}

            <form class="mt-5 space-y-4" on:submit|preventDefault={saveProfile} novalidate>
              <TextField
                id="pname"
                label="Full name"
                bind:value={editName}
                required
                maxlength={80}
                autocomplete="name"
                error={editNameError}
                forceShowError={editAttemptedSubmit}
              />
              <TextField
                id="pocc"
                label="Occupation (optional)"
                bind:value={editOccupation}
                placeholder="Student, Freelancer, Shop Owner..."
                maxlength={100}
                autocomplete="organization-title"
                error={editOccupationError}
                forceShowError={editAttemptedSubmit}
              />
              <div class="flex justify-end">
                <button class="button-primary px-6 py-2" type="submit" disabled={editLoading}>
                  {editLoading ? 'Saving...' : 'Save changes'}
                </button>
              </div>
            </form>
          </div>

          <!-- Change Password -->
          <div class="card p-6">
            <h3 class="text-lg font-bold text-slate-900 dark:text-white">Change Password</h3>
            <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">Update your account password</p>

            {#if pwdMessage}
              <div class="mt-4"><Alert variant="success">{pwdMessage}</Alert></div>
            {/if}
            {#if pwdError}
              <div class="mt-4"><Alert variant="error">{pwdError}</Alert></div>
            {/if}

            <form class="mt-5 space-y-4" on:submit|preventDefault={changePassword} novalidate>
              <PasswordField
                id="cpwd-current"
                label="Current password"
                bind:value={currentPassword}
                placeholder="Enter current password"
                required
                autocomplete="current-password"
                error={currentPasswordError}
                forceShowError={pwdAttemptedSubmit}
              />
              <div class="grid gap-4 sm:grid-cols-2">
                <PasswordField
                  id="cpwd-new"
                  label="New password"
                  bind:value={newPassword}
                  placeholder="Min. 8 characters"
                  required
                  autocomplete="new-password"
                  error={newPasswordError}
                  forceShowError={pwdAttemptedSubmit}
                  showStrength
                />
                <PasswordField
                  id="cpwd-confirm"
                  label="Confirm new password"
                  bind:value={confirmNewPassword}
                  placeholder="Repeat new password"
                  required
                  autocomplete="new-password"
                  error={confirmNewPasswordError}
                  forceShowError={pwdAttemptedSubmit}
                />
              </div>
              <div class="flex justify-end">
                <button class="button-primary px-6 py-2" type="submit" disabled={pwdLoading}>
                  {pwdLoading ? 'Changing...' : 'Change password'}
                </button>
              </div>
            </form>
          </div>

          <!-- Danger Zone -->
          <div class="rounded-2xl border border-red-200 bg-red-50 p-6 shadow-sm dark:border-red-500/20 dark:bg-red-500/5 dark:shadow-xl">
            <h3 class="text-lg font-bold text-red-600 dark:text-red-400">Danger Zone</h3>
            <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">Irreversible account actions</p>

            {#if deleteError}
              <div class="mt-4"><Alert variant="error">{deleteError}</Alert></div>
            {/if}

            <div class="mt-4">
              {#if !deleteConfirmOpen}
                <button
                  class="button-danger"
                  on:click={() => (deleteConfirmOpen = true)}
                >
                  Delete account
                </button>
                <p class="mt-2 text-xs text-slate-400 dark:text-slate-500">Permanently deletes your account, cases, evidence, and comments.</p>
              {:else}
                <p class="text-sm font-medium text-slate-900 dark:text-white">Are you sure? This cannot be undone.</p>
                <div class="mt-3 flex gap-3">
                  <button
                    class="inline-flex items-center justify-center rounded-xl bg-red-600 px-4 py-2 text-sm font-semibold text-white transition-all duration-300 hover:bg-red-500 active:scale-[0.97] disabled:pointer-events-none disabled:opacity-40"
                    disabled={deleteLoading}
                    on:click={confirmDeleteAccount}
                  >
                    {deleteLoading ? 'Deleting...' : 'Yes, delete my account'}
                  </button>
                  <button
                    class="button-secondary"
                    disabled={deleteLoading}
                    on:click={() => (deleteConfirmOpen = false)}
                  >
                    Cancel
                  </button>
                </div>
              {/if}
            </div>
          </div>
        </div>
      </div>
  {/if}
