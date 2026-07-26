import { get, writable } from 'svelte/store';

export type ThemePreference = 'light' | 'dark' | 'system';
export type ResolvedTheme = 'light' | 'dark';

const STORAGE_KEY = 'ev-theme';

function getSystemTheme(): ResolvedTheme {
  if (typeof window === 'undefined') return 'dark';
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}

function getStoredPreference(): ThemePreference {
  if (typeof window === 'undefined') return 'system';
  const stored = localStorage.getItem(STORAGE_KEY);
  return stored === 'light' || stored === 'dark' ? stored : 'system';
}

export const themePreference = writable<ThemePreference>('system');
export const resolvedTheme = writable<ResolvedTheme>('dark');

function applyTheme(pref: ThemePreference) {
  const resolved = pref === 'system' ? getSystemTheme() : pref;
  resolvedTheme.set(resolved);
  if (typeof document !== 'undefined') {
    document.documentElement.setAttribute('data-theme', resolved);
  }
}

export function setTheme(pref: ThemePreference) {
  themePreference.set(pref);
  if (typeof window !== 'undefined') {
    if (pref === 'system') {
      localStorage.removeItem(STORAGE_KEY);
    } else {
      localStorage.setItem(STORAGE_KEY, pref);
    }
  }
  applyTheme(pref);
}

let mediaListenerAttached = false;

export function initTheme() {
  const pref = getStoredPreference();
  themePreference.set(pref);
  applyTheme(pref);

  if (!mediaListenerAttached && typeof window !== 'undefined') {
    mediaListenerAttached = true;
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
      if (get(themePreference) === 'system') {
        applyTheme('system');
      }
    });
  }
}
