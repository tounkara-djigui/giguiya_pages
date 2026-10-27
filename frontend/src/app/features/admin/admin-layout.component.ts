import { Component, inject } from '@angular/core';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { LucideAngularModule } from 'lucide-angular';
import { AuthService } from '../../core/services/auth.service';
import { Icons } from '../../shared/icons';

@Component({
  selector: 'app-admin-layout',
  imports: [RouterOutlet, RouterLink, RouterLinkActive, LucideAngularModule],
  template: `
    <div class="admin-shell" data-testid="admin-shell">
      <aside class="admin-side">
        <div class="who hide-mobile">
          <span class="label">Gestione sito</span>
          <p class="name">{{ auth.user()?.first_name }} {{ auth.user()?.last_name }}</p>
          <p class="dim mail">{{ auth.user()?.email }}</p>
        </div>
        @for (l of links; track l.path) {
          <a [routerLink]="l.path" routerLinkActive="active" [routerLinkActiveOptions]="{ exact: l.exact }" class="admin-link"
             [attr.data-testid]="'admin-nav-' + l.id">
            <lucide-icon [img]="l.icon" [size]="18" /> {{ l.label }}
          </a>
        }
        @if (auth.user()?.is_super_admin) {
          <a routerLink="/admin/staff" routerLinkActive="active" class="admin-link" data-testid="admin-nav-staff">
            <lucide-icon [img]="i.ShieldCheck" [size]="18" /> Staff
          </a>
        }
        <div class="spacer hide-mobile"></div>
        <a routerLink="/" class="admin-link" data-testid="admin-nav-site"><lucide-icon [img]="i.Globe" [size]="18" /> Vai al sito</a>
        <button class="admin-link as-btn" (click)="auth.logout()" data-testid="admin-logout-button"><lucide-icon [img]="i.LogOut" [size]="18" /> Esci</button>
      </aside>
      <section class="admin-main"><router-outlet /></section>
    </div>
  `,
  styles: `
    .who { padding: 0 14px 24px; margin-bottom: 12px; border-bottom: 1px solid var(--gold-border); }
    .name { font-family: var(--font-display); font-size: 1.4rem; margin-top: 8px; }
    .mail { font-size: .8rem; word-break: break-all; }
    .spacer { flex: 1; }
    .as-btn { background: none; border: 0; cursor: pointer; font-family: inherit; text-align: left; }
  `,
})
export default class AdminLayoutComponent {
  protected auth = inject(AuthService);
  protected readonly i = Icons;
  protected readonly links = [
    { path: '/admin', label: 'Dashboard', icon: Icons.LayoutDashboard, exact: true, id: 'dashboard' },
    { path: '/admin/soci', label: 'Soci', icon: Icons.IdCard, exact: false, id: 'soci' },
    { path: '/admin/interessati', label: 'Interessati', icon: Icons.Contact, exact: false, id: 'interessati' },
    { path: '/admin/eventi', label: 'Eventi', icon: Icons.CalendarDays, exact: false, id: 'eventi' },
    { path: '/admin/progetti', label: 'Progetti', icon: Icons.FolderKanban, exact: false, id: 'progetti' },
  ];
}
