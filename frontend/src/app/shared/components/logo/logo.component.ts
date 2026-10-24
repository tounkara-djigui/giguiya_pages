import { Component } from '@angular/core';

@Component({
  selector: 'app-logo',
  template: `
    <span class="logo" data-testid="brand-logo">
      <svg viewBox="0 0 40 40" width="38" height="38" aria-hidden="true">
        <defs>
          <linearGradient id="lg" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0" stop-color="#F3E5AB" /><stop offset=".5" stop-color="#D4A03C" /><stop offset="1" stop-color="#9A6B1F" />
          </linearGradient>
        </defs>
        <circle cx="20" cy="20" r="18.5" fill="none" stroke="url(#lg)" stroke-width="1.2" />
        <path d="M20 7 L31 27 H9 Z" fill="none" stroke="url(#lg)" stroke-width="1.4" />
        <circle cx="20" cy="21" r="3.2" fill="url(#lg)" />
      </svg>
      <span class="word">Giguiya<small>Associazione · Torino</small></span>
    </span>
  `,
  styles: `
    .logo { display: inline-flex; align-items: center; gap: 12px; }
    .word { font-family: var(--font-display); font-size: 1.55rem; line-height: 1; letter-spacing: 0.01em; display: flex; flex-direction: column; }
    small { font-family: var(--font-mono); font-size: 0.56rem; letter-spacing: 0.24em; text-transform: uppercase; color: var(--gold); margin-top: 5px; }
  `,
})
export class LogoComponent {}
