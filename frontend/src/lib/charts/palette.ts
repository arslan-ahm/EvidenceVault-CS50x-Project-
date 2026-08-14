// Validated categorical + status palette (see dataviz skill: references/palette.md).
// Each slot/role has a light and dark step; components pick the active one
// reactively off the app's resolvedTheme store so charts follow the site's
// existing light/dark/system toggle.

export type ThemeMode = 'light' | 'dark';

export const categorical = [
  { light: '#2a78d6', dark: '#3987e5' }, // 1 blue
  { light: '#eb6834', dark: '#d95926' }, // 2 orange
  { light: '#1baf7a', dark: '#199e70' }, // 3 aqua
  { light: '#eda100', dark: '#c98500' }, // 4 yellow
  { light: '#e87ba4', dark: '#d55181' }, // 5 magenta
  { light: '#008300', dark: '#008300' }, // 6 green
  { light: '#4a3aa7', dark: '#9085e9' }, // 7 violet
  { light: '#e34948', dark: '#e66767' } // 8 red
];

export const status = {
  good: { light: '#0ca30c', dark: '#0ca30c' },
  warning: { light: '#fab219', dark: '#fab219' },
  serious: { light: '#ec835a', dark: '#ec835a' },
  critical: { light: '#d03b3b', dark: '#d03b3b' }
};

export const sequentialBlue = categorical[0];

export function pick(pair: { light: string; dark: string }, mode: ThemeMode): string {
  return mode === 'dark' ? pair.dark : pair.light;
}

export const chrome = {
  gridline: { light: '#e1e0d9', dark: '#2c2c2a' },
  axis: { light: '#c3c2b7', dark: '#383835' },
  muted: { light: '#898781', dark: '#898781' },
  surface: { light: '#fcfcfb', dark: '#1a1a19' }
};
