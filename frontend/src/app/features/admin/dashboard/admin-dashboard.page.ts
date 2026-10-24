import { Component, inject } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { RouterLink } from '@angular/router';
import { LucideAngularModule } from 'lucide-angular';
import { AdminStats } from '../../../core/models/admin.model';
import { AdminService } from '../../../core/services/admin.service';
import { AuthService } from '../../../core/services/auth.service';
import { Icons } from '../../../shared/icons';

@Component({
  selector: 'app-admin-dashboard-page',
  imports: [RouterLink, LucideAngularModule],
  template: `
    <span class="overline">Dashboard</span>
    <h1 class="admin-title mt-2">Benvenuto, <span class="gold-text">{{ auth.user()?.first_name }}</span></h1>
    <p class="muted mt-1">Panoramica dell'associazione e accesso rapido alla gestione dei contenuti.</p>

    @if (stats(); as s) {
      <div class="grid grid-4 mt-4">
        @for (c of cards(s); track c.label) {
          <a [routerLink]="c.link" class="card card-hover stat-card fade-up" [attr.data-testid]="'admin-stat-' + c.id">
            <span class="label"><lucide-icon [img]="c.icon" [size]="15" /> {{ c.label }}</span>
            <p class="stat-number mt-2">{{ c.value }}</p>
            <p class="dim mt-1 small">{{ c.hint }}</p>
          </a>
        }
      </div>
    } @else {
      <div class="grid grid-4 mt-4">@for (n of [1, 2, 3, 4]; track n) { <div class="skeleton" style="height: 150px"></div> }</div>
    }

    <div class="grid grid-2 mt-4">
      <a routerLink="/admin/eventi" class="card card-hover quick" data-testid="admin-quick-new-event">
        <lucide-icon [img]="i.CalendarDays" [size]="26" />
        <div><h3 class="h3">Gestisci eventi</h3><p class="muted">Crea nuovi eventi e consulta le prenotazioni.</p></div>
        <lucide-icon [img]="i.ArrowUpRight" [size]="20" class="arr" />
      </a>
      <a routerLink="/admin/progetti" class="card card-hover quick" data-testid="admin-quick-new-project">
        <lucide-icon [img]="i.FolderKanban" [size]="26" />
        <div><h3 class="h3">Registra progetti</h3><p class="muted">Aggiungi e aggiorna i progetti dell'associazione.</p></div>
        <lucide-icon [img]="i.ArrowUpRight" [size]="20" class="arr" />
      </a>
    </div>
  `,
  styles: `
    .small { font-size: .8rem; }
    .quick { display: flex; gap: 20px; align-items: flex-start; }
    .quick > lucide-icon:first-child { color: var(--gold); margin-top: 4px; }
    .arr { margin-left: auto; color: var(--gold); }
  `,
})
export default class AdminDashboardPage {
  private api = inject(AdminService);
  protected auth = inject(AuthService);
  protected readonly i = Icons;
  protected stats = toSignal(this.api.stats());

  cards(s: AdminStats) {
    return [
      { id: 'members', label: 'Soci', value: s.members_total, hint: `${s.members_in_good_standing} in regola nel ${s.current_year}`, icon: Icons.Users, link: '/admin/soci' },
      { id: 'pending', label: 'Tessere da rilasciare', value: s.members_pending_card, hint: `${s.members_pending_enrollment} iscrizioni da incassare`, icon: Icons.IdCard, link: '/admin/soci' },
      { id: 'bookings', label: 'Prenotazioni', value: s.bookings_total, hint: `${s.contacts_total} persone interessate`, icon: Icons.Ticket, link: '/admin/interessati' },
      { id: 'events', label: 'Eventi in programma', value: s.upcoming_events, hint: `${s.projects_total} progetti registrati`, icon: Icons.CalendarDays, link: '/admin/eventi' },
    ];
  }
}
