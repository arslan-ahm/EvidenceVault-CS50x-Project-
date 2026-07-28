<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/stores';

  import EvidencePreview from '$lib/components/EvidencePreview.svelte';
  import LoadingCard from '$lib/components/LoadingCard.svelte';
  import Markdown from '$lib/components/Markdown.svelte';
  import RelativeTime from '$lib/components/RelativeTime.svelte';
  import TimelineList from '$lib/components/TimelineList.svelte';
  import { apiGet, apiPost } from '$lib/api';
  import { currentUser } from '$lib/stores/auth';
  import type { Comment, PublicReportDetail } from '$lib/types';

  let reportId = '';
  $: reportId = $page.params.id ?? '';

  let detail: PublicReportDetail | null = null;
  let comments: Comment[] = [];
  let upvoted = false;
  let newComment = '';
  let commentSubmitting = false;
  let loading = true;
  let error = '';

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

  async function load() {
    loading = true;
    error = '';
    try {
      detail = await apiGet<PublicReportDetail>(`/public/reports/${reportId}`);
      comments = await apiGet<Comment[]>(`/public/reports/${reportId}/comments`);
      if ($currentUser) {
        try {
          const voteStatus = await apiGet<{ upvoted: boolean }>(`/cases/${reportId}/upvote/status`);
          upvoted = voteStatus.upvoted;
        } catch {
          upvoted = false;
        }
      }
      try {
        const viewResult = await apiPost<{ views_count: number }>(`/public/reports/${reportId}/view`);
        if (detail) detail = { ...detail, report: { ...detail.report, views_count: viewResult.views_count } };
      } catch {
        // best-effort
      }
    } catch (err) {
      error = err instanceof Error ? err.message : 'Unable to load this report';
    } finally {
      loading = false;
    }
  }

  async function toggleUpvote() {
    if (!detail) return;
    const result = await apiPost<{ upvoted: boolean; upvotes_count: number }>(`/cases/${reportId}/upvote`);
    upvoted = result.upvoted;
    detail = { ...detail, report: { ...detail.report, upvotes_count: result.upvotes_count } };
  }

  async function submitComment() {
    if (!newComment.trim()) return;
    commentSubmitting = true;
    try {
      await apiPost(`/cases/${reportId}/comments`, { body: newComment.trim() });
      newComment = '';
      comments = await apiGet<Comment[]>(`/public/reports/${reportId}/comments`);
    } finally {
      commentSubmitting = false;
    }
  }

  onMount(() => {
    void load();
  });
</script>

<svelte:head>
  <title>{detail ? `${detail.report.title} | EvidenceVault` : 'Complaint | EvidenceVault'}</title>
</svelte:head>

<div class="min-h-screen bg-slate-50 px-4 pb-16 pt-24 text-slate-900 dark:bg-slate-900 dark:text-white sm:px-6 lg:px-8">
  <div class="mx-auto max-w-3xl">
    <a href="/explore" class="mb-6 flex items-center gap-1.5 text-sm text-slate-500 transition-colors hover:text-slate-900 dark:text-slate-400 dark:hover:text-white">
      <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" /></svg>
      Explore
    </a>

    {#if loading}
      <LoadingCard label="Loading report..." />
    {:else if error}
      <div class="card p-8 text-center text-sm text-slate-500 dark:text-slate-400">{error}</div>
    {:else if detail}
      <header class="border-b border-slate-200 pb-8 dark:border-slate-800">
        <div class="flex flex-wrap items-center gap-2">
          <span class="rounded-full bg-slate-100 px-2.5 py-0.5 text-[11px] font-semibold uppercase tracking-wide text-slate-600 dark:bg-slate-800 dark:text-slate-300">{formatLabel(detail.report.category)}</span>
          <span class={`rounded-full px-2.5 py-0.5 text-[11px] font-semibold uppercase tracking-wide ${severityStyles[detail.report.severity] || 'bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-300'}`}>{formatLabel(detail.report.severity)}</span>
          <span class="rounded-full bg-slate-100 px-2.5 py-0.5 text-[11px] font-semibold uppercase tracking-wide text-slate-600 dark:bg-slate-800 dark:text-slate-300">{formatLabel(detail.report.status)}</span>
        </div>

        <h1 class="mt-4 font-display text-4xl font-bold leading-tight tracking-tight text-slate-900 dark:text-white">{detail.report.title}</h1>

        <p class="mt-2 text-sm text-slate-500 dark:text-slate-400">
          {detail.report.organization_name || 'Community report'}
          <span class="mx-1.5">·</span>
          <RelativeTime date={detail.report.created_at} />
        </p>

        <div class="mt-5 flex items-center gap-5 text-sm text-slate-500 dark:text-slate-400">
          <span class="flex items-center gap-1.5">
            <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
            {detail.report.views_count} views
          </span>
          {#if $currentUser}
            <button
              class={`flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-semibold transition-colors ${upvoted ? 'border-blue-400 bg-blue-50 text-blue-600 dark:border-blue-500/40 dark:bg-blue-500/10 dark:text-blue-400' : 'border-slate-200 bg-white text-slate-600 hover:border-blue-300 hover:text-slate-900 dark:border-slate-700/60 dark:bg-slate-800/50 dark:text-slate-300 dark:hover:border-blue-500/30 dark:hover:text-white'}`}
              on:click={toggleUpvote}
            >
              <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7"/></svg>
              {detail.report.upvotes_count} upvotes
            </button>
          {:else}
            <span>{detail.report.upvotes_count} upvotes</span>
          {/if}
        </div>
      </header>

      <div class="mt-8">
        <Markdown content={detail.report.description ?? ''} />
      </div>

      <section class="mt-10">
        <div class="mb-4 flex items-center justify-between">
          <h2 class="font-display text-lg font-bold text-slate-900 dark:text-white">Evidence</h2>
          <span class="text-xs text-slate-400 dark:text-slate-500">{detail.evidence.length} item{detail.evidence.length === 1 ? '' : 's'}</span>
        </div>
        {#if detail.evidence.length === 0}
          <div class="flex items-center gap-3 rounded-xl border border-dashed border-slate-300 p-4 dark:border-slate-700/60">
            <div class="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-slate-100 dark:bg-slate-700/50">
              <svg class="h-4 w-4 text-slate-400 dark:text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
            </div>
            <p class="text-sm text-slate-500 dark:text-slate-400">No evidence uploaded publicly for this report.</p>
          </div>
        {:else}
          <div class="grid gap-3 sm:grid-cols-2">
            {#each detail.evidence as item (item.id)}
              <EvidencePreview {item} />
            {/each}
          </div>
        {/if}
      </section>

      {#if detail.timeline.length > 0}
        <section class="mt-10">
          <TimelineList items={detail.timeline} />
        </section>
      {/if}

      <section class="mt-10">
        <h2 class="mb-4 font-display text-lg font-bold text-slate-900 dark:text-white">Discussion</h2>
        {#if $currentUser}
          <form class="space-y-2" on:submit|preventDefault={submitComment}>
            <textarea class="field min-h-20 w-full" placeholder="Add a comment..." maxlength={5000} bind:value={newComment}></textarea>
            <div class="flex justify-end">
              <button class="button-primary" type="submit" disabled={commentSubmitting || !newComment.trim()}>
                {commentSubmitting ? 'Posting...' : 'Post comment'}
              </button>
            </div>
          </form>
        {:else}
          <p class="text-sm text-slate-500 dark:text-slate-400"><a class="text-blue-600 hover:text-blue-500 dark:text-blue-400 dark:hover:text-blue-300" href="/login">Log in</a> to join the discussion.</p>
        {/if}

        {#if comments.length === 0}
          <p class="mt-4 text-sm text-slate-500 dark:text-slate-400">No comments yet.</p>
        {:else}
          <ul class="mt-4 divide-y divide-slate-200 dark:divide-slate-800">
            {#each comments as comment}
              <li class="py-4 first:pt-0">
                <div class="flex items-center justify-between gap-3">
                  <span class="font-medium text-slate-900 dark:text-white">{comment.author_name}</span>
                  <RelativeTime date={comment.created_at} className="text-xs text-slate-400 dark:text-slate-500" />
                </div>
                <p class="mt-2 text-sm text-slate-500 dark:text-slate-400 whitespace-pre-wrap">{comment.body}</p>
              </li>
            {/each}
          </ul>
        {/if}
      </section>
    {/if}
  </div>
</div>
