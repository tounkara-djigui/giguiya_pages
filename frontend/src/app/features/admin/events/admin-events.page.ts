import { Component, OnInit, inject, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { LucideAngularModule } from 'lucide-angular';
import { EventItem } from '../../../core/models/event.model';
import { AdminService } from '../../../core/services/admin.service';
import { ToastService } from '../../../core/services/toast.service';
import { apiError } from '../../../core/utils/api.utils';
import { Icons } from '../../../shared/icons';
import { ItDatePipe } from '../../../shared/pipes/it-date.pipe';
import { EventBookingsComponent } from './event-bookings.component';
import { EventFormComponent } from './event-form.component';

@Component({
  selector: 'app-admin-events-page',
  imports: [RouterLink, LucideAngularModule, ItDatePipe, EventFormComponent, EventBookingsComponent],
  template: `
    <div class="row-between">
      <div>
        <span class="overline">Contenuti</span>
        <h1 class="admin-title mt-2">Eventi</h1>
        <p class="muted mt-1">Crea e modifica gli eventi pubblicati sul sito e consulta le prenotazioni di ogni singolo evento.</p>
      </div>
      <button class="btn btn-gold btn-sm" (click)="openForm(null)" data-testid="admin-new-event-button"><lucide-icon [img]="i.Plus" [size]="16" /> Nuovo evento</button>
    </div>

    @if (events(); as list) {
      @if (list.length) {
        <div class="table-wrap mt-4">
          <table class="table" data-testid="admin-events-table">
            <thead><tr><th>Evento</th><th>Data</th><th>Prenotazioni</th><th>Stato</th><th></th></tr></thead>
            <tbody>
              @for (e of list; track e.id) {
                <tr [attr.data-testid]="'admin-event-row-' + e.slug">
                  <td>
                    <strong style="font-weight: 500">{{ e.title }}</strong>
                    <div class="dim" style="font-size: .8rem">{{ e.category }} · {{ e.location || '—' }}</div>
                  </td>
                  <td style="white-space: nowrap">{{ e.start_at | itDate: 'datetime' }}</td>
                  <td>
                    <button class="btn btn-ghost btn-sm" (click)="bookingsFor.set(e)" [attr.data-testid]="'admin-event-bookings-button-' + e.slug">
                      <lucide-icon [img]="i.Users" [size]="15" /> {{ e.bookings_count }}{{ e.capacity ? ' / ' + e.capacity : '' }}
                    </button>
                  </td>
                  <td>
                    @if (!e.is_published) { <span class="badge badge-muted">Bozza</span> }
                    @else if (e.is_past) { <span class="badge badge-muted">Concluso</span> }
                    @else { <span class="badge badge-green">Pubblicato</span> }
                  </td>
                  <td>
                    <div class="row" style="flex-wrap: nowrap">
                      @if (e.is_published) {
                        <a [routerLink]="['/eventi', e.slug]" target="_blank" class="btn btn-ghost btn-icon" title="Vedi sul sito"><lucide-icon [img]="i.ArrowUpRight" [size]="15" /></a>
                      }
                      <button class="btn btn-ghost btn-icon" (click)="openForm(e)" title="Modifica" [attr.data-testid]="'admin-event-edit-' + e.slug"><lucide-icon [img]="i.Pencil" [size]="15" /></button>
                      @if (confirmId() === e.id) {
                        <button class="btn btn-danger btn-sm" (click)="remove(e)" [attr.data-testid]="'admin-event-confirm-delete-' + e.slug">Conferma</button>
                      } @else {
                        <button class="btn btn-ghost btn-icon" (click)="confirmId.set(e.id)" title="Elimina" [attr.data-testid]="'admin-event-delete-' + e.slug"><lucide-icon [img]="i.Trash2" [size]="15" /></button>
                      }
                    </div>
                  </td>
                </tr>
              }
            </tbody>
          </table>
        </div>
      } @else {
        <div class="empty mt-4">Nessun evento. Crea il primo!</div>
      }
    } @else {
      <div class="skeleton mt-4" style="height: 300px"></div>
    }

    @if (formOpen()) {
      <app-event-form [event]="editing()" (closed)="formOpen.set(false)" (saved)="onSaved()" />
    }
    @if (bookingsFor(); as b) {
      <app-event-bookings [event]="b" (closed)="bookingsFor.set(null)" (changed)="load()" />
    }
  `,
})
export default class AdminEventsPage implements OnInit {
  private api = inject(AdminService);
  private toast = inject(ToastService);
  protected readonly i = Icons;
  protected events = signal<EventItem[] | null>(null);
  protected formOpen = signal(false);
  protected editing = signal<EventItem | null>(null);
  protected bookingsFor = signal<EventItem | null>(null);
  protected confirmId = signal<string | null>(null);

  ngOnInit(): void {
    this.load();
  }

  load(): void {
    this.api.events().subscribe({
      next: (e) => this.events.set(e),
      error: (e) => this.toast.error(apiError(e)),
    });
  }

  openForm(e: EventItem | null): void {
    this.editing.set(e);
    this.formOpen.set(true);
  }

  onSaved(): void {
    this.formOpen.set(false);
    this.load();
  }

  remove(e: EventItem): void {
    this.api.deleteEvent(e.id).subscribe({
      next: () => {
        this.toast.success('Evento eliminato');
        this.confirmId.set(null);
        this.load();
      },
      error: (err) => this.toast.error(apiError(err)),
    });
  }
}
