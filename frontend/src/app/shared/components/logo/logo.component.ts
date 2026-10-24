import { Component } from '@angular/core';

@Component({
  selector: 'app-logo',
  template: `
    <span class="logo" data-testid="brand-logo">
      <span class="emblem"><img src="/images/logo-emblem.png" alt="Logo ASPCMT Giguiya" width="46" height="46" /></span>
      <span class="word">Giguiya<small>ASPCMT · Torino</small></span>
    </span>
  `,
  styles: `
    .logo { display: inline-flex; align-items: center; gap: 12px; }
    .emblem { width: 50px; height: 50px; border-radius: 50%; background: #fff; display: grid; place-items: center; flex-shrink: 0;
      box-shadow: 0 0 0 1px var(--gold-border-strong), 0 8px 24px -10px rgba(212,160,60,.5); overflow: hidden; }
    .emblem img { width: 44px; height: 44px; object-fit: contain; }
    .word { font-family: var(--font-display); font-size: 1.55rem; line-height: 1; letter-spacing: 0.01em; display: flex; flex-direction: column; }
    small { font-family: var(--font-mono); font-size: 0.56rem; letter-spacing: 0.22em; text-transform: uppercase; color: var(--gold); margin-top: 5px; white-space: nowrap; }
    @media (max-width: 420px) { small { display: none; } .word { font-size: 1.4rem; } }
  `,
})
export class LogoComponent {}
