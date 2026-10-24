import { Component, computed, inject, signal } from '@angular/core';
import { toObservable, toSignal } from '@angular/core/rxjs-interop';
import { LucideAngularModule } from 'lucide-angular';
import { catchError, of, switchMap, tap } from 'rxjs';
import { EventItem } from '../../core/models/event.model';
import { PublicService } from '../../core/services/public.service';
import { EventCardComponent } from '../../shared/components/event-card/event-card.component';
import { PageHeaderComponent } from '../../shared/components/page-header/page-header.component';
import { Icons } from '../../shared/icons';

@Component({
  selector: 'app-events-list-page',
  imports: [LucideAngularModule, EventCardComponent, PageHeaderComponent],
  template: `
    <app-page-header overline="Agenda Giguiya" title="Eventi e" accent="incontri" image="images/mali-niger.jpg"
      lead="Laboratori, incontri, sport, gite e momenti di comunità aperti a tutta la cittadinanza. Scegli un evento e prenota il tuo posto in pochi secondi." />

    <section class="section-tight">
      <div class="container">
        <div class="row-between">
          <div class="row" role="tablist">
            <button class="chip" [class.active]="scope() === 'upcoming'" (click)="setScope('upcoming')" data-testid="events-scope-upcoming">Prossimi</button>
            <button class="chip" [class.active]="scope() === 'past'" (click)="setScope('past')" data-testid="events-scope-past">Passati</button>
          </div>
          @if (categories().length > 1) {
            <div class="row">
              <button class="chip" [class.active]="!category()" (click)="category.set('')" data-testid="events-category-all">Tutti</button>
              @for (c of categories(); track c) {
                <button class="chip" [class.active]="category() === c" (click)="category.set(c)" [attr.data-testid]="'events-category-' + c.toLowerCase()">{{ c }}</button>
              }
            </div>
          }
        </div>

        @if (loading()) {
          <div class="grid grid-3 mt-4">
            @for (n of [1, 2, 3]; track n) { <div class="skeleton" style="height: 440px"></div> }
          </div>
        } @else if (filtered().length) {
          <div class="grid grid-3 mt-4" data-testid="events-grid">
            @for (e of filtered(); track e.id) {
              <app-event-card [event]="e" class="fade-up" />
            }
          </div>
        } @else {
          <div class="empty mt-4" data-testid="events-empty">
            <lucide-icon [img]="i.CalendarDays" [size]="32" style="color: var(--gold)" />
            <p class="mt-2">{{ scope() === 'upcoming' ? 'Nessun evento in programma al momento. Torna presto!' : 'Nessun evento passato da mostrare.' }}</p>
          </div>
        }
      </div>
    </section>
  `,
})
export default class EventsListPage {
  private api = inject(PublicService);
  protected readonly i = Icons;
  protected scope = signal<'upcoming' | 'past'>('upcoming');
  protected category = signal('');
  protected loading = signal(true);
  private events = toSignal(
    toObservable(this.scope).pipe(
      tap(() => this.loading.set(true)),
      switchMap((s) => this.api.events(s).pipe(catchError(() => of([] as EventItem[])))),
      tap(() => this.loading.set(false)),
    ),
    { initialValue: [] as EventItem[] },
  );
  protected categories = computed(() => [...new Set(this.events().map((e) => e.category))]);
  protected filtered = computed(() => this.events().filter((e) => !this.category() || e.category === this.category()));

  setScope(s: 'upcoming' | 'past'): void {
    this.category.set('');
    this.scope.set(s);
  }
}
