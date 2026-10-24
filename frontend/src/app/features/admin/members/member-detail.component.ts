import { Component, OnChanges, inject, input, output, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { LucideAngularModule } from 'lucide-angular';
import { Member } from '../../../core/models/member.model';
import { AdminService } from '../../../core/services/admin.service';
import { ToastService } from '../../../core/services/toast.service';
import { apiError } from '../../../core/utils/api.utils';
import { Icons } from '../../../shared/icons';
import { ItDatePipe } from '../../../shared/pipes/it-date.pipe';

@Component({
  selector: 'app-member-detail',
  imports: [FormsModule, LucideAngularModule, ItDatePipe],
  template: `
    @let m = member();
    <div class="modal-backdrop" (click)="closed.emit()">
      <div class="modal" (click)="$event.stopPropagation()" data-testid="admin-member-detail-modal">
        <div class="modal-head">
          <div>
            <span class="overline">{{ m.membership_number }}</span>
            <h2 class="h2 mt-1">{{ m.first_name }} {{ m.last_name }}</h2>
            <div class="row mt-2">
              <span class="badge" [class.badge-green]="m.in_good_standing" [class.badge-red]="!m.in_good_standing">{{ m.in_good_standing ? 'In regola' : 'Non in regola' }}</span>
              <span class="badge" [class.badge-muted]="!m.account_active">{{ m.account_active ? 'Account attivo' : 'Password non impostata' }}</span>
            </div>
          </div>
          <button class="btn btn-ghost btn-icon" (click)="closed.emit()" data-testid="admin-member-detail-close"><lucide-icon [img]="i.X" [size]="18" /></button>
        </div>

        <dl class="dl">
          <dt>Email</dt><dd>{{ m.email }}</dd>
          <dt>Telefono</dt><dd>{{ m.phone || '—' }}</dd>
          <dt>Nascita</dt><dd>{{ m.birth_date ? (m.birth_date | itDate: 'date') : '—' }} {{ m.birth_place ? '· ' + m.birth_place : '' }}</dd>
          <dt>Codice fiscale</dt><dd class="mono">{{ m.fiscal_code || '—' }}</dd>
          <dt>Indirizzo</dt><dd>{{ m.address || '—' }} {{ m.city ? '· ' + m.city : '' }}</dd>
          <dt>Domanda</dt><dd>{{ m.created_at | itDate: 'datetime' }}</dd>
          <dt>Iscrizione 5€</dt><dd>{{ m.enrollment_paid ? 'Pagata il ' + (m.enrollment_paid_at | itDate: 'date') : 'Da pagare' }}</dd>
          <dt>Tessera</dt><dd>{{ m.card_issued ? 'Rilasciata il ' + (m.card_issued_at | itDate: 'date') : 'Da rilasciare' }}</dd>
        </dl>

        <hr class="divider mt-3" />
        <span class="label mt-3" style="display: block">Quote annuali ({{ m.annual_fee }}€)</span>
        <div class="years mt-2">
          @for (y of years; track y) {
            <button class="chip" [class.active]="paid(y)" (click)="toggleYear(y)" [attr.data-testid]="'admin-member-year-' + y">
              {{ y }} {{ paid(y) ? '✓' : '' }}
            </button>
          }
        </div>

        <label class="field mt-3"><span class="label">Note interne</span>
          <textarea class="input" [(ngModel)]="notes" rows="3" data-testid="admin-member-notes-input"></textarea>
        </label>

        <div class="row-between mt-3">
          <div class="row">
            <button class="btn btn-gold btn-sm" (click)="saveNotes()" data-testid="admin-member-save-notes">Salva note</button>
            <button class="btn btn-ghost btn-sm" (click)="resend()" [disabled]="sending()" data-testid="admin-member-resend-invite">
              <lucide-icon [img]="i.Mail" [size]="15" /> Reinvia email di accesso
            </button>
          </div>
          @if (confirmDelete()) {
            <div class="row">
              <span class="dim small">Confermi?</span>
              <button class="btn btn-danger btn-sm" (click)="remove()" data-testid="admin-member-confirm-delete">Elimina</button>
              <button class="btn btn-ghost btn-sm" (click)="confirmDelete.set(false)">Annulla</button>
            </div>
          } @else {
            <button class="btn btn-danger btn-sm" (click)="confirmDelete.set(true)" data-testid="admin-member-delete-button"><lucide-icon [img]="i.Trash2" [size]="15" /> Elimina socio</button>
          }
        </div>
      </div>
    </div>
  `,
  styles: `
    .dl { display: grid; grid-template-columns: 140px 1fr; gap: 10px 20px; margin: 0; font-size: .92rem; }
    .dl dt { color: var(--text-3); }
    .dl dd { margin: 0; word-break: break-word; }
    .years { display: flex; gap: 8px; flex-wrap: wrap; }
    .small { font-size: .85rem; }
  `,
})
export class MemberDetailComponent implements OnChanges {
  private api = inject(AdminService);
  private toast = inject(ToastService);
  readonly member = input.required<Member>();
  readonly closed = output<void>();
  readonly changed = output<Member>();
  readonly deleted = output<string>();
  protected readonly i = Icons;
  protected notes = '';
  protected sending = signal(false);
  protected confirmDelete = signal(false);
  protected years: number[] = [];

  ngOnChanges(): void {
    const m = this.member();
    this.notes = m.notes ?? '';
    const y = m.current_year;
    this.years = [y - 2, y - 1, y, y + 1];
  }

  paid(year: number): boolean {
    return this.member().fees.some((f) => f.year === year);
  }

  toggleYear(year: number): void {
    this.api.setFee(this.member().id, year, !this.paid(year)).subscribe({
      next: (m) => this.changed.emit(m),
      error: (e) => this.toast.error(apiError(e)),
    });
  }

  saveNotes(): void {
    this.api.updateMember(this.member().id, { notes: this.notes || null }).subscribe({
      next: (m) => {
        this.changed.emit(m);
        this.toast.success('Note salvate');
      },
      error: (e) => this.toast.error(apiError(e)),
    });
  }

  resend(): void {
    this.sending.set(true);
    this.api.resendInvite(this.member().id).subscribe({
      next: (r) => {
        this.sending.set(false);
        r.email_sent ? this.toast.success(r.message) : this.toast.error(r.message);
      },
      error: (e) => {
        this.sending.set(false);
        this.toast.error(apiError(e));
      },
    });
  }

  remove(): void {
    const id = this.member().id;
    this.api.deleteMember(id).subscribe({
      next: () => {
        this.toast.success('Socio eliminato');
        this.deleted.emit(id);
      },
      error: (e) => this.toast.error(apiError(e)),
    });
  }
}
