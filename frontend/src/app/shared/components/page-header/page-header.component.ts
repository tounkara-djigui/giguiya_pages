import { Component, input } from '@angular/core';

@Component({
  selector: 'app-page-header',
  template: `
    <section class="ph page-top" [class.has-bg]="image()">
      @if (image()) {
        <div class="ph-bg"><img [src]="image()" alt="" /></div>
      }
      <div class="halo"></div>
      <div class="container rel">
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
    .has-bg { padding-bottom: 80px; }
    .ph-bg { position: absolute; inset: 0; }
    .ph-bg img { width: 100%; height: 100%; object-fit: cover; opacity: .42; animation: heroZoomPh 16s ease-out both; }
    .ph-bg::after { content: ''; position: absolute; inset: 0; background: linear-gradient(90deg, rgba(12,13,16,.95) 0%, rgba(12,13,16,.7) 55%, rgba(12,13,16,.35) 100%), linear-gradient(0deg, var(--bg-root) 0%, transparent 45%); }
    .rel { position: relative; }
    @keyframes heroZoomPh { from { transform: scale(1.1); } to { transform: scale(1); } }
  `,
})
export class PageHeaderComponent {
  readonly overline = input('');
  readonly title = input.required<string>();
  readonly accent = input('');
  readonly lead = input('');
  readonly image = input('');
}
