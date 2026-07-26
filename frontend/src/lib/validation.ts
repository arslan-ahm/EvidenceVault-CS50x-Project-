// Shared, dependency-free form validators. Each returns an error message
// string when invalid, or null when the value passes.

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
// Loose E.164-ish phone matcher: optional leading +, 7-15 digits, spaces/dashes/parens allowed.
const PHONE_RE = /^\+?[0-9()\-\s]{7,20}$/;
const URL_RE = /^https?:\/\/[^\s]+\.[^\s]{2,}$/i;

export function validateRequired(value: string, label = 'This field'): string | null {
  if (!value || !value.trim()) return `${label} is required`;
  return null;
}

export function validateEmail(value: string, opts: { required?: boolean } = {}): string | null {
  const required = opts.required ?? true;
  if (!value || !value.trim()) return required ? 'Email address is required' : null;
  if (!EMAIL_RE.test(value.trim())) return 'Enter a valid email address';
  return null;
}

export function validatePhone(value: string, opts: { required?: boolean } = {}): string | null {
  const required = opts.required ?? false;
  if (!value || !value.trim()) return required ? 'Phone number is required' : null;
  const digits = value.replace(/[^0-9]/g, '');
  if (!PHONE_RE.test(value.trim()) || digits.length < 7 || digits.length > 15) {
    return 'Enter a valid phone number';
  }
  return null;
}

export function validateUrl(value: string, opts: { required?: boolean } = {}): string | null {
  const required = opts.required ?? false;
  if (!value || !value.trim()) return required ? 'URL is required' : null;
  if (!URL_RE.test(value.trim())) return 'Enter a valid URL (starting with http:// or https://)';
  return null;
}

export function validateLength(
  value: string,
  bounds: { min?: number; max?: number },
  label = 'This field'
): string | null {
  const len = value.trim().length;
  if (bounds.min !== undefined && len < bounds.min) {
    return `${label} must be at least ${bounds.min} characters`;
  }
  if (bounds.max !== undefined && len > bounds.max) {
    return `${label} must be ${bounds.max} characters or fewer`;
  }
  return null;
}

export function validateMatch(value: string, other: string, label = 'Fields'): string | null {
  if (value !== other) return `${label} do not match`;
  return null;
}

export function validatePasswordStrength(value: string, opts: { minLength?: number } = {}): string | null {
  const minLength = opts.minLength ?? 8;
  if (!value) return 'Password is required';
  if (value.length < minLength) return `Password must be at least ${minLength} characters`;
  if (!/[a-zA-Z]/.test(value) || !/[0-9]/.test(value)) {
    return 'Password must include at least one letter and one number';
  }
  return null;
}

export type PasswordStrength = {
  score: 0 | 1 | 2 | 3 | 4;
  label: string;
  colorClass: string;
};

export function getPasswordStrength(value: string): PasswordStrength {
  if (!value) return { score: 0, label: '', colorClass: 'bg-slate-700' };

  let score = 0;
  if (value.length >= 8) score += 1;
  if (value.length >= 12) score += 1;
  if (/[a-z]/.test(value) && /[A-Z]/.test(value)) score += 1;
  if (/[0-9]/.test(value)) score += 1;
  if (/[^a-zA-Z0-9]/.test(value)) score += 1;

  const clamped = Math.min(4, score) as 0 | 1 | 2 | 3 | 4;
  const levels: PasswordStrength[] = [
    { score: 0, label: 'Very weak', colorClass: 'bg-red-500' },
    { score: 1, label: 'Weak', colorClass: 'bg-red-500' },
    { score: 2, label: 'Fair', colorClass: 'bg-amber-500' },
    { score: 3, label: 'Good', colorClass: 'bg-blue-500' },
    { score: 4, label: 'Strong', colorClass: 'bg-emerald-500' },
  ];
  return levels[clamped];
}
