import { Component, effect, inject, input, signal } from '@angular/core';
import { Title } from '@angular/platform-browser';
import { RouterLink } from '@angular/router';
import { LucideAngularModule } from 'lucide-angular';
import { Project } from '../../core/models/project.model';
import { PublicService } from '../../core/services/public.service';
import { Icons } from '../../shared/icons';
import { MediaUrlPipe } from '../../shared/pipes/media-url.pipe';

@Component({
  selector: 'app-project-detail-page',
  imports: [RouterLink, LucideAngularModule, MediaUrlPipe],
  template: `
    @if (project(); as p) {
      <section class="ph page-top">
        <div class="container">
          <a routerLink="/progetti" class="link-gold" data-testid="project-back-link"><lucide-icon [img]="i.ArrowLeft" [size]="16" /> Tutti i progetti</a>
          <div class="row mt-3 fade-up"><span class="badge">{{ p.category }}</span>@if (p.year_label) { <span class="badge badge-muted">{{ p.year_label }}</span> }</div>
          <h1 class="display mt-2 fade-up delay-1" data-testid="project-title">{{ p.title }}</h1>
          <p class="sub mt-2 fade-up delay-2">{{ p.subtitle }}</p>
        </div>
      </section>
      <div class="container">
        <div class="img-frame cover fade-up delay-3"><img [src]="p.image_url | mediaUrl" [alt]="p.title" /></div>
      </div>
      <section class="section-tight">
        <div class="container split">
          <div>
            <p class="lead">{{ p.summary }}</p>
            <div class="desc mt-3" data-testid="project-description">{{ p.description }}</div>
          </div>
          <aside class="stack">
            @if (p.partners) {
              <div class="card">
                <span class="label">In collaborazione con</span>
                <p class="partners mt-2" data-testid="project-partners">{{ p.partners }}</p>
              </div>
            }
            @if (p.highlights.length) {
              <div class="card">
                <span class="label">Attività</span>
                <ul class="hl mt-2">
                  @for (h of p.highlights; track h) { <li><lucide-icon [img]="i.CircleCheck" [size]="16" /> {{ h }}</li> }
                </ul>
              </div>
            }
            <a routerLink="/eventi" class="btn btn-gold" data-testid="project-events-button">Vedi gli eventi <lucide-icon [img]="i.ArrowRight" [size]="16" /></a>
          </aside>
        </div>
      </section>
      @if (p.gallery.length) {
        <section class="section-tight" data-testid="project-gallery">
          <div class="container">
            <span class="overline">Galleria</span>
            <div class="pgal mt-3">
              @for (g of p.gallery; track g; let idx = $index) {
                <button type="button" class="pgal-item" (click)="open.set(idx)" [attr.data-testid]="'project-gallery-item-' + idx">
                  <img [src]="g | mediaUrl" [alt]="p.title + ' – foto ' + (idx + 1)" loading="lazy" />
                </button>
              }
            </div>
          </div>
        </section>
        @if (open() !== null) {
          <div class="lb" (click)="open.set(null)" data-testid="project-lightbox">
            <button class="lb-btn lb-close" (click)="open.set(null)" aria-label="Chiudi" data-testid="project-lightbox-close"><lucide-icon [img]="i.X" [size]="22" /></button>
            <button class="lb-btn lb-prev" (click)="step(-1, p.gallery.length); $event.stopPropagation()" aria-label="Precedente" data-testid="project-lightbox-prev"><lucide-icon [img]="i.ChevronLeft" [size]="26" /></button>
            <img [src]="p.gallery[open()!] | mediaUrl" alt="" (click)="$event.stopPropagation()" data-testid="project-lightbox-image" />
            <button class="lb-btn lb-next" (click)="step(1, p.gallery.length); $event.stopPropagation()" aria-label="Successiva" data-testid="project-lightbox-next"><lucide-icon [img]="i.ChevronRight" [size]="26" /></button>
            <span class="lb-count">{{ open()! + 1 }} / {{ p.gallery.length }}</span>
          </div>
        }
      }
    } @else if (notFound()) {
      <section class="section page-top"><div class="container center">
        <h1 class="h2">Progetto non trovato</h1>
        <a routerLink="/progetti" class="btn btn-gold mt-4">Torna ai progetti</a>
      </div></section>
    } @else {
      <section class="section page-top"><div class="container"><div class="skeleton" style="height: 420px"></div></div></section>
    }
  `,
  styles: `
    .ph { padding-bottom: 48px; }
    .sub { font-family: var(--font-display); font-style: italic; font-size: 1.5rem; color: var(--gold-light); }
    .cover { aspect-ratio: 21/9; min-height: 260px; }
    .desc { white-space: pre-line; color: var(--text-2); font-size: 1.05rem; line-height: 1.8; }
    .partners { font-family: var(--font-display); font-size: 1.8rem; color: var(--gold-light); }
    .hl { list-style: none; padding: 0; margin: 0; display: grid; gap: 12px; }
    .hl li { display: flex; gap: 10px; align-items: center; color: var(--text-2); }
    .hl lucide-icon { color: var(--gold); flex-shrink: 0; }
    .pgal { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 14px; }
    .pgal-item { padding: 0; border: 1px solid var(--gold-border); border-radius: var(--radius-sm); overflow: hidden; aspect-ratio: 4/3; cursor: zoom-in; background: var(--bg-card); }
    .pgal-item img { width: 100%; height: 100%; object-fit: cover; transition: transform .5s var(--ease); }
    .pgal-item:hover img { transform: scale(1.05); }
    .lb { position: fixed; inset: 0; z-index: 200; background: rgba(5,6,8,.92); display: grid; place-items: center; padding: 56px 16px; animation: fadeUp .25s var(--ease) both; }
    .lb img { max-width: min(1100px, 100%); max-height: 82vh; object-fit: contain; border-radius: 10px; }
    .lb-btn { position: absolute; width: 46px; height: 46px; border-radius: 50%; border: 1px solid rgba(212,160,60,.4); background: rgba(20,22,28,.8); color: #f4f4f6; display: grid; place-items: center; cursor: pointer; transition: background-color .2s ease; }
    .lb-btn:hover { background: #d4a03c; color: #14110a; }
    .lb-close { top: 16px; right: 16px; }
    .lb-prev { left: 16px; top: 50%; transform: translateY(-50%); }
    .lb-next { right: 16px; top: 50%; transform: translateY(-50%); }
    .lb-count { position: absolute; bottom: 18px; left: 50%; transform: translateX(-50%); color: #a1a1aa; font-size: .85rem; }
  `,
})
export default class ProjectDetailPage {
  private api = inject(PublicService);
  private title = inject(Title);
  readonly slug = input.required<string>();
  protected readonly i = Icons;
  protected project = signal<Project | null>(null);
  protected notFound = signal(false);
  protected open = signal<number | null>(null);

  step(dir: number, total: number): void {
    this.open.update((i) => ((i ?? 0) + dir + total) % total);
  }

  constructor() {
    effect(() => {
      this.api.project(this.slug()).subscribe({
        next: (p) => {
          this.project.set(p);
          this.title.setTitle(`${p.title} · Giguiya`);
        },
        error: () => this.notFound.set(true),
      });
    });
  }
}
