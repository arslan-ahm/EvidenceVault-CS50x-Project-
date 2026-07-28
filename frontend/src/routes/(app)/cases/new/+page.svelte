<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { fly } from 'svelte/transition';

  import Alert from '$lib/components/Alert.svelte';
  import Markdown from '$lib/components/Markdown.svelte';
  import MarkdownField from '$lib/components/MarkdownField.svelte';
  import SearchableCategorySelect from '$lib/components/SearchableCategorySelect.svelte';
  import SearchableOrganizationSelect from '$lib/components/SearchableOrganizationSelect.svelte';
  import TextField from '$lib/components/TextField.svelte';
  import { apiGet, apiPost } from '$lib/api';
  import type { Case } from '$lib/types';
  import { validateLength } from '$lib/validation';

  let step = 1;
  let submitting = false;
  let errorMessage = '';
  let step1AttemptedSubmit = false;

  const severities = [
    { value: 'critical', label: 'Critical', color: 'text-red-400 bg-red-500/10' },
    { value: 'high', label: 'High', color: 'text-orange-400 bg-orange-500/10' },
    { value: 'medium', label: 'Medium', color: 'text-yellow-400 bg-yellow-500/10' },
    { value: 'low', label: 'Low', color: 'text-green-400 bg-green-500/10' },
  ];

  const statuses = [
    { value: 'open', label: 'Open' },
    { value: 'in_progress', label: 'In Progress' },
    { value: 'resolved', label: 'Resolved' },
    { value: 'closed', label: 'Closed' },
  ];

  let categoryOptions: { value: string; label: string }[] = [
    { value: 'social_media_scam', label: 'Social Media Scam (Facebook, Telegram, Instagram, WhatsApp)' },
    { value: 'marketplace_fraud', label: 'Online Marketplace Fraud (Daraz, Alibaba, OLX, eBay)' },
    { value: 'phishing', label: 'Phishing / Account Takeover' },
    { value: 'fake_job', label: 'Fake Job / Employment Scam' },
    { value: 'investment_scam', label: 'Investment / Crypto Scam' },
    { value: 'software_service_complaint', label: 'Software & App Service Complaint' },
    { value: 'billing_dispute', label: 'Billing & Subscription Dispute' },
    { value: 'poor_service', label: 'Poor Service / Breach of Contract' },
    { value: 'rental_property_scam', label: 'Rental & Property Scam' },
    { value: 'identity_theft', label: 'Identity Theft / Impersonation' },
    { value: 'delivery_courier_scam', label: 'Delivery / Courier Scam' },
    { value: 'other', label: 'Other / General Complaint' },
  ];

  // Form data
  let formTitle = '';
  let formDescription = '';
  let formCategory = 'other';
  let formSeverity = 'medium';
  let formStatus = 'open';
  let formOrganizationId = '';
  let formOrganizationName = '';
  let formIsPublic = true;

  const steps = ['Complaint Details', 'Classification', 'Organization', 'Review & Submit'];

  $: titleError = validateLength(formTitle, { min: 5, max: 200 }, 'Complaint title');
  $: descriptionError = validateLength(formDescription, { min: 20, max: 10000 }, 'Description');

  onMount(async () => {
    try {
      const fetchedCategories = await apiGet<{ id: string; value: string; label: string }[]>('/categories').catch(() => []);
      if (fetchedCategories.length > 0) {
        categoryOptions = fetchedCategories;
      }
    } catch {
      // optional data; silently ignore
    }
  });

  function getSeverityLabel(value: string): string {
    return severities.find(s => s.value === value)?.label || value;
  }

  function getCategoryLabel(value: string): string {
    return categoryOptions.find((c) => c.value === value)?.label || value;
  }

  function nextStep() {
    if (step === 1) {
      step1AttemptedSubmit = true;
      if (titleError || descriptionError) return;
    }
    if (step < steps.length) {
      step += 1;
    }
  }

  function prevStep() {
    if (step > 1) {
      step -= 1;
    }
  }

  async function handleSubmit() {
    submitting = true;
    errorMessage = '';
    try {
      const payload: Record<string, unknown> = {
        title: formTitle.trim(),
        description: formDescription.trim(),
        category: formCategory,
        severity: formSeverity,
        status: formStatus,
        is_public: formIsPublic,
      };
      if (formOrganizationId) {
        payload.organization_id = formOrganizationId;
      }
      const created = await apiPost<Case>('/cases', payload);
      await goto(`/cases/${created.id}`);
    } catch (error) {
      errorMessage = error instanceof Error ? error.message : 'Failed to file complaint. Please try again.';
      submitting = false;
    }
  }

  function goToStep(targetStep: number) {
    if (targetStep < step) {
      step = targetStep;
    }
  }

  function isStepActive(idx: number): boolean {
    return idx === step;
  }

  function isStepCompleted(idx: number): boolean {
    return idx < step;
  }

  function isStepPending(idx: number): boolean {
    return idx > step;
  }
</script>

<svelte:head>
  <title>File a Complaint | EvidenceVault</title>
</svelte:head>

<div class="mx-auto max-w-2xl">
    <!-- Step indicator -->
    <nav class="mb-10 flex items-center justify-center gap-0">
      {#each steps as label, i}
        {@const idx = i + 1}
        <button
          class="flex items-center gap-2 text-sm font-medium transition-all duration-300"
          disabled={isStepPending(idx)}
          on:click={() => goToStep(idx)}
        >
          <span
            class={[
              'flex h-8 w-8 items-center aspect-square justify-center rounded-full text-xs font-bold transition-all duration-300',
              isStepActive(idx) && 'bg-blue-600',
              isStepCompleted(idx) && 'bg-blue-100 dark:bg-blue-500/20',
              isStepPending(idx) && 'bg-slate-100 dark:bg-slate-700/50',
              isStepActive(idx) && 'text-white',
              isStepCompleted(idx) && 'text-blue-600 dark:text-blue-400',
              isStepPending(idx) && 'text-slate-400 dark:text-slate-500',
              isStepActive(idx) && 'shadow-lg',
              isStepActive(idx) && 'shadow-blue-500/20',
            ].filter(Boolean).join(' ')}
          >
            {#if isStepCompleted(idx)}
              <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"/></svg>
            {:else}
              {idx}
            {/if}
          </span>
          <span
            class="hidden sm:inline whitespace-nowrap"
            class:text-blue-600={!isStepPending(idx)}
            class:dark:text-blue-400={!isStepPending(idx)}
            class:text-slate-400={isStepPending(idx)}
            class:dark:text-slate-500={isStepPending(idx)}
          >
            {label}
          </span>
        </button>
        {#if idx < steps.length}
          <div
            class={[
              'mx-3 h-px w-12 sm:w-20',
              isStepCompleted(idx) && 'bg-blue-400 dark:bg-blue-500/40',
              !isStepCompleted(idx) && 'bg-slate-200 dark:bg-slate-700',
            ].filter(Boolean).join(' ')}
          ></div>
        {/if}
      {/each}
    </nav>

    <!-- Step content -->
    <div class="card p-8">
      {#key step}
        <div transition:fly={{ y: 12, duration: 250, opacity: 0 }}>
          {#if step === 1}
            <!-- Step 1: Basic Info -->
            <div>
              <h3 class="text-xl font-semibold text-slate-900 dark:text-white">Complaint details</h3>
              <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">Give your complaint a clear title and describe what happened.</p>

              <div class="mt-6 space-y-5">
                <TextField
                  id="title"
                  label="Complaint title"
                  bind:value={formTitle}
                  placeholder="e.g. Fake Daraz seller took payment and never shipped item"
                  required
                  maxlength={200}
                  error={titleError}
                  forceShowError={step1AttemptedSubmit}
                />

                <MarkdownField
                  id="desc"
                  label="Description"
                  bind:value={formDescription}
                  placeholder="Describe what happened, how you discovered it, and any platforms, accounts, or orders involved... (Markdown supported)"
                  required
                  maxlength={10000}
                  rows={9}
                  minHeightClass="min-h-48"
                  error={descriptionError}
                  forceShowError={step1AttemptedSubmit}
                />
              </div>
            </div>
          {:else if step === 2}
            <!-- Step 2: Classification -->
            <div>
              <h3 class="text-xl font-semibold text-slate-900 dark:text-white">Classification</h3>
              <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">Categorise the complaint and set severity to help prioritise it.</p>

              <div class="mt-6 space-y-5">
                <div>
                  <label for="category" class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">Category / Scam type</label>
                  <SearchableCategorySelect
                    placeholder="Search or type a new scam type…"
                    bind:value={formCategory}
                  />
                  <p class="mt-1 text-xs text-slate-400 dark:text-slate-500">Start typing to search existing categories, or type a new one to add it.</p>
                </div>

                <div>
                  <span class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">Severity</span>
                  <div class="grid grid-cols-2 gap-3 sm:grid-cols-4">
                    {#each severities as sev}
                      <button
                        class={[
                          'rounded-xl border px-4 py-3 text-center text-sm font-medium transition-all duration-200 hover:border-slate-300 hover:text-slate-900 dark:hover:border-slate-600/60 dark:hover:text-white',
                          formSeverity === sev.value && 'border-blue-400 dark:border-blue-500/50',
                          formSeverity === sev.value && 'bg-blue-50 dark:bg-blue-500/10',
                          formSeverity === sev.value && 'text-blue-600 dark:text-blue-400',
                          formSeverity !== sev.value && 'border-slate-200 dark:border-slate-700/60',
                          formSeverity !== sev.value && 'bg-white dark:bg-slate-700/30',
                          formSeverity !== sev.value && 'text-slate-500 dark:text-slate-400',
                        ].filter(Boolean).join(' ')}
                        on:click={() => (formSeverity = sev.value)}
                      >
                        <span class="block text-xs font-semibold uppercase tracking-wider">{sev.label}</span>
                      </button>
                    {/each}
                  </div>
                </div>

                <div>
                  <label for="status" class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">Status</label>
                  <div class="select-wrapper">
                    <select id="status" class="field" bind:value={formStatus}>
                      {#each statuses as st}
                        <option value={st.value}>{st.label}</option>
                      {/each}
                    </select>
                    <svg class="select-chevron h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
                  </div>
                </div>
              </div>
            </div>

          {:else if step === 3}
            <!-- Step 3: Organization & Visibility -->
            <div>
              <h3 class="text-xl font-semibold text-slate-900 dark:text-white">Organization & visibility</h3>
              <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">Link the complaint to an organisation and control its visibility.</p>

              <div class="mt-6 space-y-5">
                <div>
                  <label for="org" class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">Affected organization <span class="text-slate-400 dark:text-slate-500">(optional)</span></label>
                  <SearchableOrganizationSelect
                    placeholder="Search or add an organization…"
                    bind:value={formOrganizationId}
                    on:change={(e) => (formOrganizationName = e.detail.name)}
                  />
                  <p class="mt-1 text-xs text-slate-400 dark:text-slate-500">Search for an existing organisation, or type a new name to add it. Leave blank for a general complaint.</p>
                </div>

                <div class="rounded-xl border border-slate-200 bg-slate-50 p-5 dark:border-slate-700/60 dark:bg-slate-900/50">
                  <div class="flex items-center justify-between">
                    <div>
                      <p class="text-sm font-medium text-slate-900 dark:text-white">Public complaint</p>
                      <p class="text-xs text-slate-500 dark:text-slate-400">Allow this complaint to appear in the public explore feed</p>
                    </div>
                    <button
                      class="relative h-6 w-11 rounded-full transition-colors duration-300"
                      class:bg-blue-600={formIsPublic}
                      class:bg-slate-300={!formIsPublic}
                      class:dark:bg-slate-600={!formIsPublic}
                      on:click={() => (formIsPublic = !formIsPublic)}
                      aria-label="Toggle public visibility"
                    >
                      <span
                        class="absolute left-0.5 top-0.5 h-5 w-5 rounded-full bg-white shadow transition-transform duration-300"
                        class:translate-x-5={formIsPublic}
                        class:translate-x-0={!formIsPublic}
                      ></span>
                    </button>
                  </div>
                </div>
              </div>
            </div>

          {:else if step === 4}
            <!-- Step 4: Review & Submit -->
            <div>
              <h3 class="text-xl font-semibold text-slate-900 dark:text-white">Review & submit</h3>
              <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">Check everything looks correct before submitting.</p>

              <div class="mt-6 space-y-4 rounded-xl border border-slate-200 bg-slate-50 p-5 dark:border-slate-700/60 dark:bg-slate-900/50">
                <div class="grid gap-4 sm:grid-cols-2">
                  <div>
                    <p class="text-xs font-semibold uppercase tracking-wider text-slate-400 dark:text-slate-500">Title</p>
                    <p class="mt-1 text-sm font-medium text-slate-900 dark:text-white">{formTitle}</p>
                  </div>
                  <div>
                    <p class="text-xs font-semibold uppercase tracking-wider text-slate-400 dark:text-slate-500">Category</p>
                    <p class="mt-1 text-sm font-medium text-slate-900 dark:text-white">{getCategoryLabel(formCategory)}</p>
                  </div>
                  <div>
                    <p class="text-xs font-semibold uppercase tracking-wider text-slate-400 dark:text-slate-500">Severity</p>
                    <span
                      class={[
                        'mt-1 inline-block rounded-md px-2 py-0.5 text-xs font-semibold',
                        formSeverity === 'critical' && 'text-red-600 bg-red-50 dark:text-red-400 dark:bg-red-500/10',
                        formSeverity === 'high' && 'text-orange-600 bg-orange-50 dark:text-orange-400 dark:bg-orange-500/10',
                        formSeverity === 'medium' && 'text-amber-600 bg-amber-50 dark:text-yellow-400 dark:bg-yellow-500/10',
                        formSeverity === 'low' && 'text-green-600 bg-green-50 dark:text-green-400 dark:bg-green-500/10',
                      ].filter(Boolean).join(' ')}
                    >
                      {getSeverityLabel(formSeverity)}
                    </span>
                  </div>
                  <div>
                    <p class="text-xs font-semibold uppercase tracking-wider text-slate-400 dark:text-slate-500">Status</p>
                    <p class="mt-1 text-sm font-medium text-slate-900 dark:text-white">{statuses.find(s => s.value === formStatus)?.label || formStatus}</p>
                  </div>
                  <div>
                    <p class="text-xs font-semibold uppercase tracking-wider text-slate-400 dark:text-slate-500">Organization</p>
                    <p class="mt-1 text-sm font-medium text-slate-900 dark:text-white">{formOrganizationName || 'None'}</p>
                  </div>
                  <div>
                    <p class="text-xs font-semibold uppercase tracking-wider text-slate-400 dark:text-slate-500">Visibility</p>
                    <p class="mt-1 text-sm font-medium text-slate-900 dark:text-white">{formIsPublic ? 'Public' : 'Private'}</p>
                  </div>
                </div>
                <div>
                  <p class="text-xs font-semibold uppercase tracking-wider text-slate-400 dark:text-slate-500">Description</p>
                  <div class="relative mt-1 max-h-40 overflow-hidden">
                    <Markdown content={formDescription} compact />
                    <div class="absolute bottom-0 left-0 right-0 h-8 bg-gradient-to-t from-slate-50 to-transparent dark:from-slate-900/50"></div>
                  </div>
                </div>
              </div>

              <!-- Error message -->
              {#if errorMessage}
                <div class="mt-4"><Alert variant="error">{errorMessage}</Alert></div>
              {/if}
            </div>
          {/if}
        </div>
      {/key}

      <!-- Navigation buttons -->
      <div class="mt-8 flex items-center justify-between border-t border-slate-200 pt-6 dark:border-slate-700/60">
        {#if step > 1}
          <button class="button-secondary" on:click={prevStep}>
            <svg class="mr-1.5 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/></svg>
            Back
          </button>
        {:else}
          <div></div>
        {/if}

        {#if step < steps.length}
          <button
            class="button-primary gap-1.5"
            on:click={nextStep}
            disabled={step === 1 && step1AttemptedSubmit && (!!titleError || !!descriptionError)}
          >
            Continue
            <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>
          </button>
        {:else}
          <button class="button-primary gap-1.5" on:click={handleSubmit} disabled={submitting}>
            {#if submitting}
              <svg class="h-4 w-4 animate-spin" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path></svg>
              Creating...
            {:else}
              <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
              File complaint
            {/if}
          </button>
        {/if}
      </div>
    </div>
  </div>