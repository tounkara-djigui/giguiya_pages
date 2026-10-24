import { Component, input } from '@angular/core';
import { LogoComponent } from '../logo/logo.component';

@Component({
  selector: 'app-auth-shell',
  imports: [LogoComponent],
  template: `
    <section class="shell page-top">
      <div class="halo"></div>
      <div class="container wrap">
        <div class="side hide-mobile">
          <img src="images/mali-timbuktu.jpg" alt="" />
          <div class="side-copy">
            <app-logo />
            <p class="mt-3">"Una comunità forte è fatta di mani che si intrecciano."</p>
          </div>
        </div>
        <div class="card panel fade-up">
          <span class="overline">{{ overline() }}</span>
          <h1 class="h2 mt-2" data-testid="auth-title">{{ title() }}</h1>
          @if (subtitle()) { <p class="muted mt-2">{{ subtitle() }}</p> }
          <div class="mt-4"><ng-content /></div>
        </div>
      </div>
    </section>
  `,
  styles: `
    .shell { position: relative; min-height: 100vh; padding-bottom: 96px; }
    .wrap { display: grid; gap: 40px; align-items: stretch; position: relative; }
    @media (min-width: 1024px) { .wrap { grid-template-columns: 1fr 1fr; } }
    .side { position: relative; border-radius: var(--radius); overflow: hidden; border: 1px solid var(--gold-border); min-height: 560px; }
    .side img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }
    .side::after { content: ''; position: absolute; inset: 0; background: linear-gradient(180deg, rgba(12,13,16,.2), rgba(12,13,16,.92)); }
    .side-copy { position: absolute; z-index: 1; left: 40px; right: 40px; bottom: 40px; }
    .side-copy p { font-family: var(--font-display); font-style: italic; font-size: 1.7rem; line-height: 1.3; }
    .panel { max-width: 560px; width: 100%; margin: 0 auto; align-self: center; }
  `,
})
export class AuthShellComponent {
  readonly overline = input('Accesso');
  readonly title = input.required<string>();
  readonly subtitle = input('');
}
