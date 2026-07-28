<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';

  import Alert from '$lib/components/Alert.svelte';
  import LoadingCard from '$lib/components/LoadingCard.svelte';
  import { apiDelete, apiGet, apiPatch, apiPut } from '$lib/api';
  import { authReady, currentUser } from '$lib/stores/auth';
  import type { AdminCase, AdminStats, AdminUser, PublicOrganization, User } from '$lib/types';
  import { validateLength } from '$lib/validation';

  type AdminComment = {
    id: string;
    case_id: string;
    case_title: string;
    author_email: string;
    body: string;
    created_at: string;
  };

  type Tab = 'reports' | 'users' | 'organizations' | 'comments';

  let ready = false;
  let allowed = false;
  let tab: Tab = 'reports';

  let stats: AdminStats | null = null;
  let cases: AdminCase[] = [];
  let users: AdminUser[] = [];
  let organizations: PublicOrganization[] = [];
  let comments: AdminComment[] = [];
  let editingOrgId = '';
  let editingOrgName = '';
  let message = '';

  async function loadAll() {
    const [statsData, casesData, usersData, orgsData, commentsData] = await Promise.all([
      apiGet<AdminStats>('/admin/stats'),
      apiGet<AdminCase[]>('/admin/cases'),
      apiGet<AdminUser[]>('/admin/users'),
      apiGet<PublicOrganization[]>('/public/organizations?limit=100'),
      apiGet<AdminComment[]>('/admin/comments'),
    ]);
    stats = statsData;
    cases = casesData;
    users = usersData;
    organizations = orgsData;
    comments = commentsData;
  }

  async function toggleCaseVisibility(item: AdminCase) {
    const updated = await apiPatch<AdminCase>(`/admin/cases/${item.id}`, { is_public: !item.is_public });
    cases = cases.map((c) => (c.id === item.id ? updated : c));
  }

  async function deleteCase(item: AdminCase) {
    if (!confirm(`Delete complaint "${item.title}"? This cannot be undone.`)) return;
    await apiDelete(`/admin/cases/${item.id}`);
    cases = cases.filter((c) => c.id !== item.id);
  }

  async function toggleBan(user: AdminUser) {
    const updated = await apiPatch<AdminUser>(`/admin/users/${user.id}`, { is_banned: !user.is_banned });
    users = users.map((u) => (u.id === user.id ? updated : u));
  }

  async function toggleAdmin(user: AdminUser) {
    const updated = await apiPatch<AdminUser>(`/admin/users/${user.id}`, { is_admin: !user.is_admin });
    users = users.map((u) => (u.id === user.id ? updated : u));
  }

  async function deleteUser(user: AdminUser) {
    if (!confirm(`Delete user ${user.email} and all their complaints? This cannot be undone.`)) return;
    try {
      await apiDelete(`/admin/users/${user.id}`);
      users = users.filter((u) => u.id !== user.id);
    } catch (error) {
      message = error instanceof Error ? error.message : 'Failed to delete user';
    }
  }

  function startEditOrg(org: PublicOrganization) {
    editingOrgId = org.id;
    editingOrgName = org.name;
  }

  $: editingOrgNameError = editingOrgId ? validateLength(editingOrgName, { min: 2, max: 120 }, 'Organization name') : null;

  async function saveOrgEdit() {
    if (!editingOrgId || editingOrgNameError) return;
    await apiPut(`/organizations/${editingOrgId}`, { name: editingOrgName.trim() });
    organizations = organizations.map((o) => (o.id === editingOrgId ? { ...o, name: editingOrgName.trim() } : o));
    editingOrgId = '';
  }

  async function deleteOrg(org: PublicOrganization) {
    if (!confirm(`Delete organization "${org.name}"? Complaints linked to it will become unaffiliated.`)) return;
    await apiDelete(`/organizations/${org.id}`);
    organizations = organizations.filter((o) => o.id !== org.id);
  }

  async function deleteComment(comment: AdminComment) {
    if (!confirm('Delete this comment?')) return;
    await apiDelete(`/admin/comments/${comment.id}`);
    comments = comments.filter((c) => c.id !== comment.id);
  }

  onMount(async () => {
    try {
      const me = await apiGet<User>('/auth/me');
      currentUser.set(me);
      authReady.set(true);
      if (!me.is_admin) {
        await goto('/dashboard');
        return;
      }
      allowed = true;
      await loadAll();
    } catch {
      authReady.set(true);
      await goto('/login');
      return;
    } finally {
      ready = true;
    }
  });
</script>

<svelte:head>
  <title>Admin | EvidenceVault</title>
</svelte:head>

{#if !ready}
    <LoadingCard label="Loading admin panel..." />
  {:else if allowed}
    <div class="mb-6">
      <p class="text-xs font-semibold uppercase tracking-[0.2em] text-blue-600 dark:text-blue-400">Moderation</p>
      <h2 class="mt-1 text-3xl font-semibold tracking-tight text-slate-900 dark:text-white">Admin panel</h2>
    </div>

    {#if stats}
      <div class="mb-6 grid gap-4 sm:grid-cols-3 lg:grid-cols-7">
        {#each [
          ['Users', stats.total_users],
          ['Admins', stats.admin_users],
          ['Banned', stats.banned_users],
          ['Complaints', stats.total_cases],
          ['Public complaints', stats.public_cases],
          ['Organizations', stats.total_organizations],
          ['Comments', stats.total_comments],
        ] as [label, value]}
          <div class="card p-4">
            <p class="text-xs uppercase tracking-wide text-slate-400 dark:text-slate-500">{label}</p>
            <p class="mt-1 text-2xl font-semibold text-slate-900 dark:text-white">{value}</p>
          </div>
        {/each}
      </div>
    {/if}

    {#if message}
      <div class="mb-4"><Alert variant="error">{message}</Alert></div>
    {/if}

    <div class="mb-6 flex gap-2 border-b border-slate-200 dark:border-slate-700/60">
      {#each [['reports', 'Reports'], ['users', 'Users'], ['organizations', 'Organizations'], ['comments', 'Comments']] as [key, label]}
        <button
          class="border-b-2 px-4 py-2 text-sm font-medium transition-colors"
          class:border-blue-500={tab === key}
          class:text-slate-900={tab === key}
          class:dark:text-white={tab === key}
          class:border-transparent={tab !== key}
          class:text-slate-400={tab !== key}
          class:dark:text-slate-400={tab !== key}
          on:click={() => (tab = key as Tab)}
        >
          {label}
        </button>
      {/each}
    </div>

    {#if tab === 'reports'}
      <div class="card overflow-x-auto">
        <table class="w-full text-left text-sm">
          <thead class="border-b border-slate-200 text-xs uppercase tracking-wide text-slate-400 dark:border-slate-700/60 dark:text-slate-500">
            <tr>
              <th class="px-4 py-3">Title</th>
              <th class="px-4 py-3">Owner</th>
              <th class="px-4 py-3">Org</th>
              <th class="px-4 py-3">Status</th>
              <th class="px-4 py-3">Visibility</th>
              <th class="px-4 py-3">Votes / Views</th>
              <th class="px-4 py-3">Actions</th>
            </tr>
          </thead>
          <tbody>
            {#each cases as item}
              <tr class="border-b border-slate-100 text-slate-600 dark:border-slate-700/40 dark:text-slate-300">
                <td class="px-4 py-3"><a class="text-blue-600 hover:underline dark:text-blue-400" href={`/cases/${item.id}`}>{item.title}</a></td>
                <td class="px-4 py-3">{item.owner_email}</td>
                <td class="px-4 py-3">{item.organization_name || '—'}</td>
                <td class="px-4 py-3">{item.status}</td>
                <td class="px-4 py-3">{item.is_public ? 'Public' : 'Private'}</td>
                <td class="px-4 py-3">{item.upvotes_count} / {item.views_count}</td>
                <td class="px-4 py-3">
                  <div class="flex gap-2">
                    <button class="button-secondary px-3 py-1.5 text-xs" on:click={() => toggleCaseVisibility(item)}>
                      {item.is_public ? 'Hide' : 'Unhide'}
                    </button>
                    <button class="button-danger px-3 py-1.5 text-xs" on:click={() => deleteCase(item)}>
                      Delete
                    </button>
                  </div>
                </td>
              </tr>
            {:else}
              <tr><td class="px-4 py-6 text-slate-500 dark:text-slate-400" colspan="7">No complaints yet.</td></tr>
            {/each}
          </tbody>
        </table>
      </div>
    {:else if tab === 'users'}
      <div class="card overflow-x-auto">
        <table class="w-full text-left text-sm">
          <thead class="border-b border-slate-200 text-xs uppercase tracking-wide text-slate-400 dark:border-slate-700/60 dark:text-slate-500">
            <tr>
              <th class="px-4 py-3">Email</th>
              <th class="px-4 py-3">Name</th>
              <th class="px-4 py-3">Complaints</th>
              <th class="px-4 py-3">Role</th>
              <th class="px-4 py-3">Status</th>
              <th class="px-4 py-3">Actions</th>
            </tr>
          </thead>
          <tbody>
            {#each users as user}
              <tr class="border-b border-slate-100 text-slate-600 dark:border-slate-700/40 dark:text-slate-300">
                <td class="px-4 py-3">{user.email}</td>
                <td class="px-4 py-3">{user.name || '—'}</td>
                <td class="px-4 py-3">{user.case_count}</td>
                <td class="px-4 py-3">{user.is_admin ? 'Admin' : 'Member'}</td>
                <td class="px-4 py-3">{user.is_banned ? 'Banned' : 'Active'}</td>
                <td class="px-4 py-3">
                  <div class="flex flex-wrap gap-2">
                    <button class="button-secondary px-3 py-1.5 text-xs disabled:opacity-40 disabled:cursor-not-allowed" on:click={() => toggleAdmin(user)} disabled={user.id === $currentUser?.id}>
                      {user.is_admin ? 'Revoke admin' : 'Make admin'}
                    </button>
                    <button class="button-secondary px-3 py-1.5 text-xs disabled:opacity-40 disabled:cursor-not-allowed" on:click={() => toggleBan(user)} disabled={user.id === $currentUser?.id}>
                      {user.is_banned ? 'Unban' : 'Ban'}
                    </button>
                    <button
                      class="button-danger px-3 py-1.5 text-xs disabled:opacity-40 disabled:cursor-not-allowed"
                      on:click={() => deleteUser(user)}
                      disabled={user.id === $currentUser?.id}
                    >
                      Delete
                    </button>
                  </div>
                </td>
              </tr>
            {:else}
              <tr><td class="px-4 py-6 text-slate-500 dark:text-slate-400" colspan="6">No users yet.</td></tr>
            {/each}
          </tbody>
        </table>
      </div>
    {:else if tab === 'organizations'}
      <div class="card overflow-x-auto">
        <table class="w-full text-left text-sm">
          <thead class="border-b border-slate-200 text-xs uppercase tracking-wide text-slate-400 dark:border-slate-700/60 dark:text-slate-500">
            <tr>
              <th class="px-4 py-3">Name</th>
              <th class="px-4 py-3">Reports</th>
              <th class="px-4 py-3">Actions</th>
            </tr>
          </thead>
          <tbody>
            {#each organizations as org}
              <tr class="border-b border-slate-100 text-slate-600 dark:border-slate-700/40 dark:text-slate-300">
                <td class="px-4 py-3">
                  {#if editingOrgId === org.id}
                    <input class="field" class:field-invalid={!!editingOrgNameError} bind:value={editingOrgName} maxlength={120} />
                    {#if editingOrgNameError}
                      <p class="field-error-text">{editingOrgNameError}</p>
                    {/if}
                  {:else}
                    {org.name}
                  {/if}
                </td>
                <td class="px-4 py-3">{org.total_reports}</td>
                <td class="px-4 py-3">
                  <div class="flex gap-2">
                    {#if editingOrgId === org.id}
                      <button class="button-primary px-3 py-1.5 text-xs" on:click={saveOrgEdit} disabled={!!editingOrgNameError}>Save</button>
                      <button class="button-secondary px-3 py-1.5 text-xs" on:click={() => (editingOrgId = '')}>Cancel</button>
                    {:else}
                      <button class="button-secondary px-3 py-1.5 text-xs" on:click={() => startEditOrg(org)}>Rename</button>
                      <button class="button-danger px-3 py-1.5 text-xs" on:click={() => deleteOrg(org)}>
                        Delete
                      </button>
                    {/if}
                  </div>
                </td>
              </tr>
            {:else}
              <tr><td class="px-4 py-6 text-slate-500 dark:text-slate-400" colspan="3">No organizations yet.</td></tr>
            {/each}
          </tbody>
        </table>
      </div>
    {:else if tab === 'comments'}
      <div class="space-y-3">
        {#each comments as comment}
          <div class="card p-4">
            <div class="flex items-start justify-between gap-3">
              <div>
                <p class="text-sm font-medium text-slate-900 dark:text-white">{comment.author_email}</p>
                <a class="text-xs text-blue-600 hover:underline dark:text-blue-400" href={`/cases/${comment.case_id}`}>{comment.case_title}</a>
              </div>
              <button class="button-danger px-3 py-1.5 text-xs" on:click={() => deleteComment(comment)}>
                Delete
              </button>
            </div>
            <p class="mt-2 text-sm text-slate-500 whitespace-pre-wrap dark:text-slate-400">{comment.body}</p>
          </div>
        {:else}
          <div class="card p-8 text-sm text-slate-500 dark:text-slate-400">No comments yet.</div>
        {/each}
      </div>
    {/if}
{/if}
