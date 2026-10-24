import { Component, effect, inject, input, signal } from '@angular/core';
import { Title } from '@angular/platform-browser';
import { RouterLink } from '@angular/router';
import { LucideAngularModule } from 'lucide-angular';
import { EventItem } from '../../core/models/event.model';
import { PublicService } from '../../core/services/public.service';
import { Icons } from '../../shared/icons';
import { ItDatePipe } from '../../shared/pipes/it-date.pipe';
import { BookingFormComponent } from './booking-form.component';

@Component({
  selector: 'app-event-detail-page',
  imports: [RouterLink, LucideAngularModule, ItDatePipe, BookingFormComponent],
  template: `
    @if (event(); as e) {
      <section class="hero-ev page-top">
        <div class="bg"><img [src]="e.image_url || '/images/community.jpg'" [alt]="e.title" /></div>
        <div class="container rel">
          <a routerLink="/eventi" class="link-gold back" data-testid="event-back-link"><lucide-icon [img]="i.ArrowLeft" [size]="16" /> Tutti gli eventi</a>
          <div class="row mt-3 fade-up"><span class="badge">{{ e.category }}</span>
            @if (e.is_past) { <span class="badge badge-muted">Concluso</span> }
          </div>
          <h1 class="display mt-2 fade-up delay-1" data-testid="event-title">{{ e.title }}</h1>
          <p class="lead mt-2 fade-up delay-2">{{ e.summary }}</p>
        </div>
      </section>

      <section class="section-tight">
        <div class="container split">
          <div class="stack" style="gap: 32px">
            <div class="facts">
              <div class="fact"><lucide-icon [img]="i.Calendar" [size]="20" /><div><span class="label">Data</span><p data-testid="event-date" class="cap">{{ e.start_at | itDate: 'full' }}</p></div></div>
              <div class="fact"><lucide-icon [img]="i.Clock" [size]="20" /><div><span class="label">Orario</span><p>{{ e.start_at | itDate: 'time' }}@if (e.end_at) { – {{ e.end_at | itDate: 'time' }} }</p></div></div>
              <div class="fact"><lucide-icon [img]="i.MapPin" [size]="20" /><div><span class="label">Luogo</span><p data-testid="event-location">{{ e.location || 'Torino' }}</p></div></div>
              <div class="fact"><lucide-icon [img]="i.Ticket" [size]="20" /><div><span class="label">Partecipazione</span><p>{{ e.price_label || 'Aperto a tutti' }}</p></div></div>
            </div>
            <div class="desc" data-testid="event-description">{{ e.description }}</div>
          </div>
          <aside class="sticky">
            @if (e.is_past) {
              <div class="card center"><p class="muted">Questo evento si è concluso. Scopri i prossimi appuntamenti!</p>
                <a routerLink="/eventi" class="btn btn-gold mt-3">Prossimi eventi</a></div>
            } @else if (e.spots_left === 0) {
              <div class="card center" data-testid="event-full-message"><h3 class="h3">Evento al completo</h3><p class="muted mt-2">Tutti i posti sono stati prenotati.</p></div>
            } @else {
              <app-booking-form [event]="e" (booked)="reload()" />
            }
          </aside>
        </div>
      </section>
    } @else if (notFound()) {
      <section class="section page-top"><div class="container center">
        <h1 class="h2">Evento non trovato</h1>
        <a routerLink="/eventi" class="btn btn-gold mt-4">Torna agli eventi</a>
      </div></section>
    } @else {
      <section class="section page-top"><div class="container"><div class="skeleton" style="height: 420px"></div></div></section>
    }
  `,
  styles: `
    .hero-ev { position: relative; padding-bottom: 72px; overflow: hidden; border-bottom: 1px solid var(--gold-border); }
    .bg { position: absolute; inset: 0; }
    .bg img { width: 100%; height: 100%; object-fit: cover; opacity: .35; }
    .bg::after { content: ''; position: absolute; inset: 0; background: linear-gradient(180deg, rgba(12,13,16,.6), var(--bg-root)); }
    .rel { position: relative; }
    .facts { display: grid; grid-template-columns: 1fr; gap: 1px; background: var(--gold-border); border: 1px solid var(--gold-border); border-radius: var(--radius); overflow: hidden; }
    @media (min-width: 640px) { .facts { grid-template-columns: 1fr 1fr; } }
    .fact { display: flex; gap: 16px; padding: 22px 24px; background: var(--bg-card); }
    .fact lucide-icon { color: var(--gold); margin-top: 4px; }
    .fact p { margin-top: 4px; }
    .cap { text-transform: capitalize; }
    .desc { white-space: pre-line; color: var(--text-2); font-size: 1.05rem; line-height: 1.8; }
    @media (min-width: 1024px) { .sticky { position: sticky; top: calc(var(--nav-h) + 24px); } }
  `,
})
export default class EventDetailPage {
  private api = inject(PublicService);
  private title = inject(Title);
  readonly slug = input.required<string>();
  protected readonly i = Icons;
  protected event = signal<EventItem | null>(null);
  protected notFound = signal(false);

  constructor() {
    effect(() => {
      this.load(this.slug());
    });
  }

  reload(): void {
    this.load(this.slug());
  }

  private load(slug: string): void {
    this.api.event(slug).subscribe({
      next: (e) => {
        this.event.set(e);
        this.title.setTitle(`${e.title} · Giguiya`);
      },
      error: () => this.notFound.set(true),
    });
  }
}
