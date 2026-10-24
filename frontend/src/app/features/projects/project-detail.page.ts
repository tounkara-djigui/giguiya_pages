import { Component, effect, inject, input, signal } from '@angular/core';
import { Title } from '@angular/platform-browser';
import { RouterLink } from '@angular/router';
import { LucideAngularModule } from 'lucide-angular';
import { Project } from '../../core/models/project.model';
import { PublicService } from '../../core/services/public.service';
import { Icons } from '../../shared/icons';

@Component({
  selector: 'app-project-detail-page',
  imports: [RouterLink, LucideAngularModule],
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
        <div class="img-frame cover fade-up delay-3"><img [src]="p.image_url || '/images/community.jpg'" [alt]="p.title" /></div>
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
  `,
})
export default class ProjectDetailPage {
  private api = inject(PublicService);
  private title = inject(Title);
  readonly slug = input.required<string>();
  protected readonly i = Icons;
  protected project = signal<Project | null>(null);
  protected notFound = signal(false);

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
