import { Component, input } from '@angular/core';

@Component({
  selector: 'app-page-header',
  template: `
    <section class="ph page-top">
      <div class="halo"></div>
      <div class="container">
        <span class="overline fade-up">{{ overline() }}</span>
        <h1 class="display mt-2 fade-up delay-1" data-testid="page-title">
          {{ title() }} @if (accent()) { <span class="gold-text">{{ accent() }}</span> }
        </h1>
        @if (lead()) {
          <p class="lead mt-3 fade-up delay-2">{{ lead() }}</p>
        }
        <div class="mt-3 fade-up delay-3"><ng-content /></div>
      </div>
    </section>
  `,
  styles: `
    .ph { position: relative; padding-bottom: 56px; border-bottom: 1px solid var(--gold-border); overflow: hidden; }
    .ph::after { content: ''; position: absolute; right: -10%; top: -20%; width: 520px; height: 520px; border-radius: 50%; border: 1px solid var(--gold-border); pointer-events: none; }
  `,
})
export class PageHeaderComponent {
  readonly overline = input('');
  readonly title = input.required<string>();
  readonly accent = input('');
  readonly lead = input('');
}
