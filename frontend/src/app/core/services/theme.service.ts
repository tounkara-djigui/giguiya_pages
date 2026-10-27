import { Injectable, signal } from '@angular/core';

export type Theme = 'dark' | 'light';
const KEY = 'giguiya-theme';

@Injectable({ providedIn: 'root' })
export class ThemeService {
  readonly theme = signal<Theme>(document.documentElement.dataset['theme'] === 'light' ? 'light' : 'dark');

  toggle(): void {
    const next: Theme = this.theme() === 'dark' ? 'light' : 'dark';
    this.theme.set(next);
    document.documentElement.dataset['theme'] = next;
    document.querySelector('meta[name="theme-color"]')?.setAttribute('content', next === 'light' ? '#F6F2EA' : '#0C0D10');
    try {
      localStorage.setItem(KEY, next);
    } catch {
      /* storage unavailable */
    }
  }
}
