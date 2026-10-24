import { Component, OnInit, inject, input, output, signal } from '@angular/core';
import { LucideAngularModule } from 'lucide-angular';
import { Booking, EventItem } from '../../../core/models/event.model';
import { AdminService } from '../../../core/services/admin.service';
import { ToastService } from '../../../core/services/toast.service';
import { apiError, downloadCsv } from '../../../core/utils/api.utils';
import { Icons } from '../../../shared/icons';
import { ItDatePipe } from '../../../shared/pipes/it-date.pipe';

@Component({
  selector: 'app-event-bookings',
  imports: [LucideAngularModule, ItDatePipe],
  template: `
    <div class="modal-backdrop" (click)="closed.emit()">
      <div class="modal wide" (click)="$event.stopPropagation()" data-testid="admin-event-bookings-modal">
        <div class="modal-head">
          <div>
            <span class="overline">Prenotazioni</span>
            <h2 class="h2 mt-1">{{ event().title }}</h2>
            <p class="dim mt-1">{{ event().start_at | itDate: 'datetime' }} · {{ bookings()?.length ?? 0 }} iscritti{{ event().capacity ? ' su ' + event().capacity : '' }}</p>
          </div>
          <div class="row">
            <button class="btn btn-ghost btn-sm" (click)="exportCsv()" data-testid="admin-bookings-export-button"><lucide-icon [img]="i.Download" [size]="15" /> CSV</button>
            <button class="btn btn-ghost btn-icon" (click)="closed.emit()" data-testid="admin-bookings-close"><lucide-icon [img]="i.X" [size]="18" /></button>
          </div>
        </div>
        @if (bookings(); as list) {
          @if (list.length) {
            <div class="table-wrap">
              <table class="table" data-testid="admin-bookings-table">
                <thead><tr><th>Nome</th><th>Email</th><th>Telefono</th><th>Prenotato il</th><th></th></tr></thead>
                <tbody>
                  @for (b of list; track b.id) {
                    <tr [attr.data-testid]="'admin-booking-row-' + b.id">
                      <td>{{ b.last_name }} {{ b.first_name }}</td>
                      <td>{{ b.email }}</td>
                      <td>{{ b.phone || '—' }}</td>
                      <td class="dim" style="white-space: nowrap">{{ b.created_at | itDate: 'datetime' }}</td>
                      <td><button class="btn btn-ghost btn-icon" (click)="remove(b)" title="Elimina" [attr.data-testid]="'admin-booking-delete-' + b.id"><lucide-icon [img]="i.Trash2" [size]="15" /></button></td>
                    </tr>
                  }
                </tbody>
              </table>
            </div>
          } @else {
            <div class="empty">Nessuna prenotazione per questo evento.</div>
          }
        } @else {
          <div class="skeleton" style="height: 200px"></div>
        }
      </div>
    </div>
  `,
  styles: `.wide { max-width: 960px; }`,
})
export class EventBookingsComponent implements OnInit {
  private api = inject(AdminService);
  private toast = inject(ToastService);
  readonly event = input.required<EventItem>();
  readonly closed = output<void>();
  readonly changed = output<void>();
  protected readonly i = Icons;
  protected bookings = signal<Booking[] | null>(null);

  ngOnInit(): void {
    this.api.eventBookings(this.event().id).subscribe({
      next: (b) => this.bookings.set(b),
      error: (e) => this.toast.error(apiError(e)),
    });
  }

  remove(b: Booking): void {
    this.api.deleteBooking(b.id).subscribe({
      next: () => {
        this.bookings.update((l) => l?.filter((x) => x.id !== b.id) ?? null);
        this.toast.success('Prenotazione eliminata');
        this.changed.emit();
      },
      error: (e) => this.toast.error(apiError(e)),
    });
  }

  exportCsv(): void {
    downloadCsv(`prenotazioni-${this.event().slug}.csv`, [
      ['Cognome', 'Nome', 'Email', 'Telefono', 'Data prenotazione'],
      ...(this.bookings() ?? []).map((b) => [b.last_name, b.first_name, b.email, b.phone, b.created_at]),
    ]);
  }
}
