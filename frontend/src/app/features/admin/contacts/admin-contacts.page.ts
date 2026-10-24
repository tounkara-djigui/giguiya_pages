import { Component, OnInit, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { LucideAngularModule } from 'lucide-angular';
import { Subject, debounceTime } from 'rxjs';
import { Contact } from '../../../core/models/admin.model';
import { AdminService } from '../../../core/services/admin.service';
import { ToastService } from '../../../core/services/toast.service';
import { apiError, downloadCsv } from '../../../core/utils/api.utils';
import { Icons } from '../../../shared/icons';
import { ItDatePipe } from '../../../shared/pipes/it-date.pipe';

@Component({
  selector: 'app-admin-contacts-page',
  imports: [FormsModule, LucideAngularModule, ItDatePipe],
  template: `
    <div class="row-between">
      <div>
        <span class="overline">Persone interessate</span>
        <h1 class="admin-title mt-2">Interessati agli eventi</h1>
        <p class="muted mt-1">Tutte le persone che hanno prenotato almeno un evento, con lo storico delle loro iscrizioni.</p>
      </div>
      <button class="btn btn-ghost btn-sm" (click)="exportCsv()" data-testid="admin-contacts-export-button"><lucide-icon [img]="i.Download" [size]="16" /> Esporta CSV</button>
    </div>
    <div class="toolbar">
      <div class="search">
        <lucide-icon [img]="i.Search" [size]="16" />
        <input class="input" placeholder="Cerca per nome o email" [(ngModel)]="q" (ngModelChange)="search$.next()" data-testid="admin-contacts-search-input" />
      </div>
    </div>
    @if (contacts(); as list) {
      @if (list.length) {
        <div class="table-wrap">
          <table class="table" data-testid="admin-contacts-table">
            <thead><tr><th>Nome</th><th>Contatti</th><th>Prenotazioni</th><th>Eventi</th><th>Ultima</th><th>Socio</th></tr></thead>
            <tbody>
              @for (c of list; track c.email) {
                <tr [attr.data-testid]="'admin-contact-row-' + c.email">
                  <td><strong style="font-weight: 500">{{ c.last_name }} {{ c.first_name }}</strong></td>
                  <td><div>{{ c.email }}</div><div class="dim" style="font-size: .8rem">{{ c.phone || '—' }}</div></td>
                  <td class="mono">{{ c.bookings_count }}</td>
                  <td style="max-width: 280px; font-size: .85rem" class="muted">{{ c.events.join(', ') }}</td>
                  <td class="dim" style="white-space: nowrap">{{ c.last_booking_at | itDate: 'date' }}</td>
                  <td>@if (c.is_member) { <span class="badge badge-green">Socio</span> } @else { <span class="badge badge-muted">No</span> }</td>
                </tr>
              }
            </tbody>
          </table>
        </div>
      } @else {
        <div class="empty" data-testid="admin-contacts-empty">Nessuna persona ha ancora prenotato un evento.</div>
      }
    } @else {
      <div class="skeleton" style="height: 300px"></div>
    }
  `,
})
export default class AdminContactsPage implements OnInit {
  private api = inject(AdminService);
  private toast = inject(ToastService);
  protected readonly i = Icons;
  protected contacts = signal<Contact[] | null>(null);
  protected q = '';
  protected search$ = new Subject<void>();

  ngOnInit(): void {
    this.search$.pipe(debounceTime(300)).subscribe(() => this.load());
    this.load();
  }

  load(): void {
    this.api.contacts(this.q).subscribe({
      next: (c) => this.contacts.set(c),
      error: (e) => this.toast.error(apiError(e)),
    });
  }

  exportCsv(): void {
    downloadCsv('interessati-giguiya.csv', [
      ['Cognome', 'Nome', 'Email', 'Telefono', 'Prenotazioni', 'Eventi', 'Socio'],
      ...(this.contacts() ?? []).map((c) => [c.last_name, c.first_name, c.email, c.phone, c.bookings_count, c.events.join(' | '), c.is_member ? 'Sì' : 'No']),
    ]);
  }
}
