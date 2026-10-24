import { Component, OnInit, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { LucideAngularModule } from 'lucide-angular';
import { Subject, debounceTime } from 'rxjs';
import { Member } from '../../../core/models/member.model';
import { AdminService } from '../../../core/services/admin.service';
import { ToastService } from '../../../core/services/toast.service';
import { apiError, downloadCsv } from '../../../core/utils/api.utils';
import { Icons } from '../../../shared/icons';
import { ItDatePipe } from '../../../shared/pipes/it-date.pipe';
import { MemberDetailComponent } from './member-detail.component';

@Component({
  selector: 'app-admin-members-page',
  imports: [FormsModule, LucideAngularModule, ItDatePipe, MemberDetailComponent],
  templateUrl: './admin-members.page.html',
})
export default class AdminMembersPage implements OnInit {
  private api = inject(AdminService);
  private toast = inject(ToastService);
  protected readonly i = Icons;
  protected members = signal<Member[] | null>(null);
  protected selected = signal<Member | null>(null);
  protected q = '';
  protected status = signal('all');
  private search$ = new Subject<void>();
  protected readonly filters = [
    { id: 'all', label: 'Tutti' },
    { id: 'in_regola', label: 'In regola' },
    { id: 'non_in_regola', label: 'Non in regola' },
    { id: 'tessera_da_rilasciare', label: 'Tessera da rilasciare' },
  ];

  ngOnInit(): void {
    this.search$.pipe(debounceTime(300)).subscribe(() => this.load());
    this.load();
  }

  onSearch(): void {
    this.search$.next();
  }

  setStatus(s: string): void {
    this.status.set(s);
    this.load();
  }

  load(): void {
    this.api.members(this.q, this.status()).subscribe({
      next: (m) => this.members.set(m),
      error: (e) => this.toast.error(apiError(e)),
    });
  }

  replace(m: Member): void {
    this.members.update((list) => list?.map((x) => (x.id === m.id ? m : x)) ?? null);
    if (this.selected()?.id === m.id) this.selected.set(m);
  }

  toggle(m: Member, field: 'enrollment_paid' | 'card_issued'): void {
    this.api.updateMember(m.id, { [field]: !m[field] }).subscribe({
      next: (u) => {
        this.replace(u);
        this.toast.success('Socio aggiornato');
      },
      error: (e) => this.toast.error(apiError(e)),
    });
  }

  toggleFee(m: Member): void {
    this.api.setFee(m.id, m.current_year, !m.current_year_paid).subscribe({
      next: (u) => {
        this.replace(u);
        this.toast.success(`Quota ${m.current_year} aggiornata`);
      },
      error: (e) => this.toast.error(apiError(e)),
    });
  }

  removed(id: string): void {
    this.selected.set(null);
    this.members.update((list) => list?.filter((x) => x.id !== id) ?? null);
  }

  exportCsv(): void {
    const rows = (this.members() ?? []).map((m) => [
      m.membership_number, m.last_name, m.first_name, m.email, m.phone, m.fiscal_code, m.city,
      m.enrollment_paid ? 'Sì' : 'No', m.current_year_paid ? 'Sì' : 'No', m.card_issued ? 'Sì' : 'No',
      m.in_good_standing ? 'In regola' : 'Non in regola',
    ]);
    downloadCsv('soci-giguiya.csv', [
      ['N° socio', 'Cognome', 'Nome', 'Email', 'Telefono', 'Codice fiscale', 'Città', 'Iscrizione pagata', 'Quota anno corrente', 'Tessera rilasciata', 'Stato'],
      ...rows,
    ]);
  }
}
