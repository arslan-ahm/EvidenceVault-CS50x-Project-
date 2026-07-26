<script lang="ts">
  import { createEventDispatcher, onMount } from 'svelte';
  import { fly } from 'svelte/transition';

  import { apiGet } from '$lib/api';

  export let value = '';
  export let placeholder = 'Search or type a category…';

  const dispatch = createEventDispatcher();

  interface CategoryOption {
    id: string;
    value: string;
    label: string;
  }

  let categories: CategoryOption[] = [];
  let open = false;
  let searchText = '';
  let highlightIndex = -1;
  let inputElement: HTMLInputElement;
  let listElement: HTMLDivElement;
  let listboxId = '';

  function generateId(): string {
    return 'cat-list-' + Math.random().toString(36).substring(2, 10);
  }

  $: filteredCategories = searchText.trim()
    ? categories.filter(
        (c) =>
          c.label.toLowerCase().includes(searchText.toLowerCase()) ||
          c.value.toLowerCase().includes(searchText.toLowerCase()),
      )
    : categories;

  $: exactMatch = filteredCategories.some(
    (c) => c.value.toLowerCase() === searchText.toLowerCase().trim(),
  );

  $: showAddNew = searchText.trim().length > 0 && !exactMatch;

  onMount(async () => {
    listboxId = generateId();
    try {
      categories = await apiGet<CategoryOption[]>('/categories');
    } catch {
      // fallback: categories unavailable
    }
  });

  function selectCategory(cat: CategoryOption) {
    searchText = cat.label;
    value = cat.value;
    open = false;
    highlightIndex = -1;
    dispatch('change', { value: cat.value, label: cat.label });
  }

  function selectCustom() {
    const typed = searchText.trim();
    if (!typed) return;
    value = typed.toLowerCase().replace(/\s+/g, '_');
    open = false;
    highlightIndex = -1;
    dispatch('change', { value, label: typed, isNew: true });
  }

  function handleInput() {
    value = searchText;
    open = true;
    highlightIndex = -1;
    dispatch('change', { value: searchText, label: searchText, isNew: true });
  }

  function handleFocus() {
    open = true;
    // If value is set externally, populate searchText
    if (value && !searchText) {
      const match = categories.find((c) => c.value === value);
      searchText = match?.label || value;
    }
  }

  function handleBlur() {
    // Delay to allow click on dropdown item
    setTimeout(() => {
      open = false;
      highlightIndex = -1;
    }, 200);
  }

  function handleKeydown(event: KeyboardEvent) {
    const totalItems = filteredCategories.length + (showAddNew ? 1 : 0);

    if (event.key === 'ArrowDown') {
      event.preventDefault();
      highlightIndex = Math.min(highlightIndex + 1, totalItems - 1);
    } else if (event.key === 'ArrowUp') {
      event.preventDefault();
      highlightIndex = Math.max(highlightIndex - 1, -1);
    } else if (event.key === 'Enter') {
      event.preventDefault();
      if (highlightIndex >= 0 && highlightIndex < filteredCategories.length) {
        selectCategory(filteredCategories[highlightIndex]);
      } else if (showAddNew && highlightIndex === filteredCategories.length) {
        selectCustom();
      }
    } else if (event.key === 'Escape') {
      open = false;
      highlightIndex = -1;
    }
  }

  function handleMouseEnter(idx: number) {
    highlightIndex = idx;
  }
</script>

<div class="relative">
  <div class="relative">
    <input
      bind:this={inputElement}
      type="text"
      class="field w-full pr-10"
      class:rounded-b-none={open && (filteredCategories.length > 0 || showAddNew)}
      placeholder={placeholder}
      maxlength={80}
      bind:value={searchText}
      on:focus={handleFocus}
      on:blur={handleBlur}
      on:input={handleInput}
      on:keydown={handleKeydown}
      autocomplete="off"
      role="combobox"
      aria-expanded={open}
      aria-controls={listboxId}
      aria-haspopup="listbox"
    />
    <div class="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 dark:text-slate-500">
      <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
      </svg>
    </div>
  </div>

  {#if open && (filteredCategories.length > 0 || showAddNew)}
    <div
      bind:this={listElement}
      class="absolute left-0 right-0 z-50 max-h-60 overflow-y-auto rounded-b-xl border border-t-0 border-slate-200 bg-white shadow-2xl backdrop-blur-xl dark:border-slate-600/60 dark:bg-slate-800"
      id={listboxId}
      role="listbox"
      transition:fly={{ y: -4, duration: 120, opacity: 0 }}
    >
      {#each filteredCategories as cat, i (cat.id)}
        <button
          type="button"
          class={[
            'flex w-full items-center gap-3 px-4 py-2.5 text-left text-sm transition-all duration-150',
            highlightIndex === i ? 'bg-blue-50 text-slate-900 dark:bg-blue-500/15 dark:text-white' : 'text-slate-600 dark:text-slate-300',
          ].join(' ')}
          on:mousedown={() => selectCategory(cat)}
          on:mouseenter={() => handleMouseEnter(i)}
          role="option"
          aria-selected={highlightIndex === i}
        >
          <svg class="h-4 w-4 shrink-0 text-slate-400 dark:text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" />
          </svg>
          <span class="flex-1">{cat.label}</span>
          <span class="rounded-md bg-slate-100 px-2 py-0.5 text-xs text-slate-500 dark:bg-slate-700/50 dark:text-slate-500">{cat.value}</span>
        </button>
      {/each}

      {#if showAddNew}
        <button
          type="button"
          class={[
            'flex w-full items-center gap-3 border-t border-slate-200 px-4 py-2.5 text-left text-sm transition-all duration-150 dark:border-slate-700/60',
            highlightIndex === filteredCategories.length ? 'bg-blue-50 text-blue-600 dark:bg-blue-500/15 dark:text-blue-400' : 'text-slate-500 dark:text-slate-400',
          ].join(' ')}
          on:mousedown={selectCustom}
          on:mouseenter={() => handleMouseEnter(filteredCategories.length)}
          role="option"
          aria-selected={highlightIndex === filteredCategories.length}
        >
          <svg class="h-4 w-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          <span>Add category: <strong class="text-slate-900 dark:text-white">"{searchText.trim()}"</strong></span>
        </button>
      {/if}
    </div>
  {/if}
</div>
