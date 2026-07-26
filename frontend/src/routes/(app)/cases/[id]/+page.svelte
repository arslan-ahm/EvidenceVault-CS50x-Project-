<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/stores';

  import Alert from '$lib/components/Alert.svelte';
  import EvidencePreview from '$lib/components/EvidencePreview.svelte';
  import EvidenceUpload from '$lib/components/EvidenceUpload.svelte';
  import LoadingCard from '$lib/components/LoadingCard.svelte';
  import Markdown from '$lib/components/Markdown.svelte';
  import MarkdownField from '$lib/components/MarkdownField.svelte';
  import RelativeTime from '$lib/components/RelativeTime.svelte';
  import SearchableCategorySelect from '$lib/components/SearchableCategorySelect.svelte';
  import SearchableOrganizationSelect from '$lib/components/SearchableOrganizationSelect.svelte';
  import SearchBar from '$lib/components/SearchBar.svelte';
  import TextareaField from '$lib/components/TextareaField.svelte';
  import TextField from '$lib/components/TextField.svelte';
  import TimelineList from '$lib/components/TimelineList.svelte';
  import { apiDelete, apiGet, apiPost, apiPut, getApiBaseUrl } from '$lib/api';
  import { currentUser } from '$lib/stores/auth';
  import type { Case, Comment, Evidence, SearchResult, TimelineEvent } from '$lib/types';
  import { validateLength } from '$lib/validation';

  const COMMENT_MAX_LENGTH = 5000;

  const severities = [
    { value: 'critical', label: 'Critical' },
    { value: 'high', label: 'High' },
    { value: 'medium', label: 'Medium' },
    { value: 'low', label: 'Low' }
  ];

  const statuses = [
    { value: 'open', label: 'Open' },
    { value: 'in_progress', label: 'In Progress' },
    { value: 'resolved', label: 'Resolved' },
    { value: 'closed', label: 'Closed' }
  ];

  let caseItem: Case | null = null;
  let evidence: Evidence[] = [];
  let timeline: TimelineEvent[] = [];
  let comments: Comment[] = [];
  let upvoted = false;
  let searchResults: SearchResult[] = [];
  let loading = true;
  let message = '';
  let query = '';
  let caseId = '';
  let exportUrl = '';
  let newComment = '';
  let commentSubmitting = false;
  $: caseId = $page.params.id ?? '';
  $: exportUrl = `${getApiBaseUrl()}/cases/${caseId}/export`;

  // Preview / edit mode
  let mode: 'preview' | 'edit' = 'preview';
  let editTitle = '';
  let editDescription = '';
  let editCategory = 'other';
  let editSeverity = 'medium';
  let editStatus = 'open';
  let editOrganizationId = '';
  let editIsPublic = true;
  let editSaving = false;
  let editError = '';
  let editAttemptedSubmit = false;

  $: editTitleError = validateLength(editTitle, { min: 5, max: 200 }, 'Case title');
  $: editDescriptionError = validateLength(editDescription, { min: 20, max: 10000 }, 'Description');

  const severityStyles: Record<string, string> = {
    critical: 'text-red-600 bg-red-50 dark:text-red-400 dark:bg-red-500/10',
    high: 'text-orange-600 bg-orange-50 dark:text-orange-400 dark:bg-orange-500/10',
    medium: 'text-amber-600 bg-amber-50 dark:text-yellow-400 dark:bg-yellow-500/10',
    low: 'text-green-600 bg-green-50 dark:text-green-400 dark:bg-green-500/10'
  };

  function formatLabel(value?: string) {
    if (!value) return '';
    return value.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
  }

  async function loadCase() {
    loading = true;
    try {
      caseItem = await apiGet<Case>(`/cases/${caseId}`);
      evidence = await apiGet<Evidence[]>(`/cases/${caseId}/evidence`);
      timeline = await apiGet<TimelineEvent[]>(`/cases/${caseId}/timeline`);
      comments = await apiGet<Comment[]>(`/cases/${caseId}/comments`);
      if (caseItem.is_public) {
        try {
          const status = await apiGet<{ upvoted: boolean }>(`/cases/${caseId}/upvote/status`);
          upvoted = status.upvoted;
        } catch {
          upvoted = false;
        }
      }
    } catch (error) {
      message = error instanceof Error ? error.message : 'Unable to load case';
    } finally {
      loading = false;
    }
  }

  function enterEdit() {
    if (!caseItem) return;
    editTitle = caseItem.title;
    editDescription = caseItem.description ?? '';
    editCategory = caseItem.category ?? 'other';
    editSeverity = caseItem.severity ?? 'medium';
    editStatus = caseItem.status ?? 'open';
    editOrganizationId = caseItem.organization_id ?? '';
    editIsPublic = caseItem.is_public ?? true;
    editError = '';
    editAttemptedSubmit = false;
    mode = 'edit';
  }

  function cancelEdit() {
    mode = 'preview';
    editError = '';
  }

  async function saveEdit() {
    editAttemptedSubmit = true;
    if (editTitleError || editDescriptionError) {
      editError = 'Please fix the highlighted fields before continuing.';
      return;
    }
    editSaving = true;
    editError = '';
    try {
      caseItem = await apiPut<Case>(`/cases/${caseId}`, {
        title: editTitle.trim(),
        description: editDescription.trim(),
        category: editCategory,
        severity: editSeverity,
        status: editStatus,
        organization_id: editOrganizationId || null,
        is_public: editIsPublic
      });
      mode = 'preview';
      message = 'Case updated successfully';
    } catch (error) {
      editError = error instanceof Error ? error.message : 'Failed to update case';
    } finally {
      editSaving = false;
    }
  }

  async function searchCase(value: string) {
    query = value;
    searchResults = value.trim() ? await apiGet<SearchResult[]>(`/search?q=${encodeURIComponent(value)}`) : [];
  }

  async function toggleUpvote() {
    if (!caseItem) return;
    const result = await apiPost<{ upvoted: boolean; upvotes_count: number }>(`/cases/${caseId}/upvote`);
    upvoted = result.upvoted;
    caseItem = { ...caseItem, upvotes_count: result.upvotes_count };
  }

  async function submitComment() {
    if (!newComment.trim()) return;
    commentSubmitting = true;
    try {
      await apiPost(`/cases/${caseId}/comments`, { body: newComment.trim() });
      newComment = '';
      comments = await apiGet<Comment[]>(`/cases/${caseId}/comments`);
    } finally {
      commentSubmitting = false;
    }
  }

  async function deleteComment(commentId: string) {
    await apiDelete(`/cases/${caseId}/comments/${commentId}`);
    comments = comments.filter((c) => c.id !== commentId);
  }

  function canDeleteComment(comment: Comment): boolean {
    if (!$currentUser || !caseItem) return false;
    return comment.user_id === $currentUser.id || caseItem.user_id === $currentUser.id;
  }

  onMount(() => {
    void loadCase();
  });
</script>

<svelte:head>
  <title>{caseItem ? `${caseItem.title} | EvidenceVault AI` : 'Case | EvidenceVault AI'}</title>
</svelte:head>

{#if loading}
  <LoadingCard label="Loading case details..." />
{:else if caseItem}
  <!-- Breadcrumb + page actions -->
  <div class="mb-6 flex items-center justify-between gap-4">
    <a href="/dashboard" class="flex items-center gap-1.5 text-sm text-slate-500 transition-colors hover:text-slate-900 dark:text-slate-400 dark:hover:text-white">
      <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" /></svg>
      Dashboard
    </a>
    <div class="flex items-center gap-2">
      {#if mode === 'preview'}
        <button class="button-secondary gap-1.5 px-3 py-1.5 text-xs" on:click={enterEdit}>
          <svg class="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/></svg>
          Edit
        </button>
      {/if}
      <a class="button-secondary gap-1.5 px-3 py-1.5 text-xs" href={exportUrl} target="_blank" rel="noreferrer">
        <svg class="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v2a2 2 0 002 2h12a2 2 0 002-2v-2M7 10l5 5 5-5M12 15V3"/></svg>
        Export PDF
      </a>
    </div>
  </div>

  <div class="grid gap-10 lg:grid-cols-[1fr_320px]">
    <!-- Document column -->
    <div class="min-w-0 space-y-10">
      {#if mode === 'preview'}
        <!-- Header -->
        <header class="border-b border-slate-200 pb-8 dark:border-slate-800">
          <div class="flex flex-wrap items-center gap-2">
            <span class="rounded-full bg-slate-100 px-2.5 py-0.5 text-[11px] font-semibold uppercase tracking-wide text-slate-600 dark:bg-slate-800 dark:text-slate-300">{formatLabel(caseItem.category)}</span>
            <span class={`rounded-full px-2.5 py-0.5 text-[11px] font-semibold uppercase tracking-wide ${severityStyles[caseItem.severity || ''] || 'bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-300'}`}>{formatLabel(caseItem.severity)}</span>
            <span class="rounded-full bg-slate-100 px-2.5 py-0.5 text-[11px] font-semibold uppercase tracking-wide text-slate-600 dark:bg-slate-800 dark:text-slate-300">{formatLabel(caseItem.status)}</span>
            <span class="rounded-full bg-slate-100 px-2.5 py-0.5 text-[11px] font-semibold uppercase tracking-wide text-slate-600 dark:bg-slate-800 dark:text-slate-300">{caseItem.is_public ? 'Public' : 'Private'}</span>
          </div>

          <h1 class="mt-4 font-display text-4xl font-bold leading-tight tracking-tight text-slate-900 dark:text-white">{caseItem.title}</h1>

          {#if caseItem.organization_name}
            <p class="mt-2 text-sm text-slate-500 dark:text-slate-400">Affects <span class="font-medium text-slate-700 dark:text-slate-300">{caseItem.organization_name}</span></p>
          {/if}

          <div class="mt-5 flex items-center gap-5 text-sm text-slate-500 dark:text-slate-400">
            <span class="flex items-center gap-1.5">
              <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
              {caseItem.views_count ?? 0} views
            </span>
            {#if caseItem.is_public}
              <button
                class={`flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-semibold transition-colors ${upvoted ? 'border-blue-400 bg-blue-50 text-blue-600 dark:border-blue-500/40 dark:bg-blue-500/10 dark:text-blue-400' : 'border-slate-200 bg-white text-slate-600 hover:border-blue-300 hover:text-slate-900 dark:border-slate-700/60 dark:bg-slate-800/50 dark:text-slate-300 dark:hover:border-blue-500/30 dark:hover:text-white'}`}
                on:click={toggleUpvote}
              >
                <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7"/></svg>
                {caseItem.upvotes_count ?? 0} upvotes
              </button>
            {:else}
              <span>{caseItem.upvotes_count ?? 0} upvotes</span>
            {/if}
          </div>
        </header>

        <!-- Markdown body -->
        <Markdown content={caseItem.description ?? ''} />
      {:else}
        <div>
          <div class="flex items-center justify-between gap-4">
            <p class="text-xs font-semibold uppercase tracking-[0.2em] text-blue-600 dark:text-blue-400">Edit case</p>
          </div>

          {#if editError}
            <div class="mt-3"><Alert variant="error">{editError}</Alert></div>
          {/if}

          <div class="mt-4 space-y-4">
            <TextField
              id="edit-title"
              label="Case title"
              bind:value={editTitle}
              required
              maxlength={200}
              error={editTitleError}
              forceShowError={editAttemptedSubmit}
            />
            <MarkdownField
              id="edit-description"
              label="Description"
              bind:value={editDescription}
              required
              maxlength={10000}
              rows={9}
              minHeightClass="min-h-48"
              error={editDescriptionError}
              forceShowError={editAttemptedSubmit}
            />

            <div class="grid gap-4 sm:grid-cols-2">
              <div>
                <p class="field-label"><span>Category</span></p>
                <SearchableCategorySelect bind:value={editCategory} />
              </div>
              <div>
                <p class="field-label"><span>Affected organization</span></p>
                <SearchableOrganizationSelect bind:value={editOrganizationId} />
              </div>
            </div>

            <div>
              <span class="field-label"><span>Severity</span></span>
              <div class="grid grid-cols-2 gap-2 sm:grid-cols-4">
                {#each severities as sev}
                  <button
                    type="button"
                    class={[
                      'rounded-xl border px-3 py-2 text-center text-xs font-semibold uppercase tracking-wide transition-all duration-200',
                      editSeverity === sev.value
                        ? 'border-blue-400 bg-blue-50 text-blue-600 dark:border-blue-500/50 dark:bg-blue-500/10 dark:text-blue-400'
                        : 'border-slate-200 bg-white text-slate-500 hover:border-slate-300 hover:text-slate-900 dark:border-slate-700/60 dark:bg-slate-700/30 dark:text-slate-400 dark:hover:text-white'
                    ].join(' ')}
                    on:click={() => (editSeverity = sev.value)}
                  >
                    {sev.label}
                  </button>
                {/each}
              </div>
            </div>

            <div>
              <label class="field-label" for="edit-status"><span>Status</span></label>
              <div class="select-wrapper">
                <select id="edit-status" class="field" bind:value={editStatus}>
                  {#each statuses as st}
                    <option value={st.value}>{st.label}</option>
                  {/each}
                </select>
                <svg class="select-chevron h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
              </div>
            </div>

            <div class="flex items-center justify-between rounded-xl border border-slate-200 bg-slate-50 p-4 dark:border-slate-700/60 dark:bg-slate-900/50">
              <div>
                <p class="text-sm font-medium text-slate-900 dark:text-white">Public case</p>
                <p class="text-xs text-slate-500 dark:text-slate-400">Allow this case to appear in the public explore feed</p>
              </div>
              <button
                type="button"
                class="relative h-6 w-11 rounded-full transition-colors duration-300"
                class:bg-blue-600={editIsPublic}
                class:bg-slate-300={!editIsPublic}
                class:dark:bg-slate-600={!editIsPublic}
                on:click={() => (editIsPublic = !editIsPublic)}
                aria-label="Toggle public visibility"
              >
                <span
                  class="absolute left-0.5 top-0.5 h-5 w-5 rounded-full bg-white shadow transition-transform duration-300"
                  class:translate-x-5={editIsPublic}
                  class:translate-x-0={!editIsPublic}
                ></span>
              </button>
            </div>

            <div class="flex justify-end gap-3 border-t border-slate-200 pt-4 dark:border-slate-700/60">
              <button class="button-secondary" on:click={cancelEdit} disabled={editSaving}>Cancel</button>
              <button class="button-primary" on:click={saveEdit} disabled={editSaving}>
                {editSaving ? 'Saving...' : 'Save changes'}
              </button>
            </div>
          </div>
        </div>
      {/if}

      <!-- Evidence gallery -->
      <section>
        <div class="mb-4 flex items-center justify-between">
          <h2 class="font-display text-lg font-bold text-slate-900 dark:text-white">Evidence</h2>
          <span class="text-xs text-slate-400 dark:text-slate-500">{evidence.length} item{evidence.length === 1 ? '' : 's'}</span>
        </div>

        {#if mode === 'edit'}
          <EvidenceUpload {caseId} on:complete={loadCase} />
        {/if}

        {#if evidence.length === 0}
          <div class="mt-4 flex items-center gap-3 rounded-xl border border-dashed border-slate-300 p-4 dark:border-slate-700/60">
            <div class="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-slate-100 dark:bg-slate-700/50">
              <svg class="h-4 w-4 text-slate-400 dark:text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
            </div>
            <p class="text-sm text-slate-500 dark:text-slate-400">
              {mode === 'edit' ? 'No evidence uploaded yet — use the uploader above to attach files.' : 'No evidence has been uploaded for this case yet.'}
            </p>
          </div>
        {:else}
          <div class="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {#each evidence as item (item.id)}
              <EvidencePreview {item} deletable={mode === 'edit'} on:deleted={loadCase} />
            {/each}
          </div>
        {/if}
      </section>

      <!-- Discussion -->
      <section>
        <h2 class="mb-4 font-display text-lg font-bold text-slate-900 dark:text-white">Discussion</h2>
        <form class="space-y-2" on:submit|preventDefault={submitComment}>
          <TextareaField
            id="new-comment"
            label=""
            bind:value={newComment}
            placeholder="Add a note or comment..."
            maxlength={COMMENT_MAX_LENGTH}
            rows={3}
            minHeightClass="min-h-20"
          />
          <div class="flex justify-end">
            <button class="button-primary" type="submit" disabled={commentSubmitting || !newComment.trim()}>
              {commentSubmitting ? 'Posting...' : 'Post comment'}
            </button>
          </div>
        </form>

        {#if comments.length === 0}
          <div class="mt-4 flex items-center gap-3 rounded-xl border border-dashed border-slate-300 p-4 dark:border-slate-700/60">
            <div class="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-slate-100 dark:bg-slate-700/50">
              <svg class="h-4 w-4 text-slate-400 dark:text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.86 9.86 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"/></svg>
            </div>
            <p class="text-sm text-slate-500 dark:text-slate-400">No comments yet — be the first to add one.</p>
          </div>
        {:else}
          <ul class="mt-4 divide-y divide-slate-200 dark:divide-slate-800">
            {#each comments as comment}
              <li class="py-4 first:pt-0">
                <div class="flex items-center justify-between gap-3">
                  <span class="font-medium text-slate-900 dark:text-white">{comment.author_name}</span>
                  <div class="flex items-center gap-3">
                    <RelativeTime date={comment.created_at} className="text-xs text-slate-400 dark:text-slate-500" />
                    {#if canDeleteComment(comment)}
                      <button class="text-xs text-red-600 hover:text-red-500 dark:text-red-400 dark:hover:text-red-300" on:click={() => deleteComment(comment.id)}>Delete</button>
                    {/if}
                  </div>
                </div>
                <p class="mt-2 text-sm text-slate-500 dark:text-slate-400 whitespace-pre-wrap">{comment.body}</p>
              </li>
            {/each}
          </ul>
        {/if}
      </section>
    </div>

    <!-- Side rail -->
    <aside class="space-y-6 lg:sticky lg:top-10 lg:self-start">
      <SearchBar bind:value={query} on:search={(event) => searchCase(event.detail)} />
      {#if searchResults.length > 0}
        <div class="card p-5">
          <h3 class="text-sm font-semibold text-slate-900 dark:text-white">Search results</h3>
          <div class="mt-3 space-y-3">
            {#each searchResults as result}
              <div class="rounded-xl border border-slate-200 bg-slate-50 p-3 text-sm dark:border-slate-700/60 dark:bg-slate-800/30">
                <p class="font-medium text-slate-900 dark:text-white">{result.case_title}</p>
                <p class="mt-1 text-slate-500 dark:text-slate-400">{result.snippet}</p>
              </div>
            {/each}
          </div>
        </div>
      {/if}

      <TimelineList items={timeline} />
      {#if message}
        <Alert variant={message.toLowerCase().includes('unable') || message.toLowerCase().includes('fail') ? 'error' : 'success'}>{message}</Alert>
      {/if}
    </aside>
  </div>
{/if}
