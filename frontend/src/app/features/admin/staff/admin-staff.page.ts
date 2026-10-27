import { Component, OnInit, inject, signal } from '@angular/core';
import { LucideAngularModule } from 'lucide-angular';
import { StaffMember } from '../../../core/models/admin.model';
import { AdminService } from '../../../core/services/admin.service';
import { ToastService } from '../../../core/services/toast.service';
import { apiError } from '../../../core/utils/api.utils';
import { Icons } from '../../../shared/icons';
import { ItDatePipe } from '../../../shared/pipes/it-date.pipe';

@Component({
  selector: 'app-admin-staff-page',
  imports: [LucideAngularModule, ItDatePipe],
  template: `
    <span class="overline">Sicurezza</span>
    <h1 class="admin-title mt-2">Staff e amministratori</h1>
    <p class="muted mt-1">Chi si registra come staff può accedere all'area di gestione solo dopo la tua approvazione.</p>
    @if (staff(); as list) {
      @if (list.length) {
        <div class="table-wrap mt-4">
          <table class="table" data-testid="admin-staff-table">
            <thead><tr><th>Nome</th><th>Email</th><th>Richiesta</th><th>Stato</th><th></th></tr></thead>
            <tbody>
              @for (s of list; track s.id) {
                <tr [attr.data-testid]="'admin-staff-row-' + s.email">
                  <td><strong style="font-weight: 500">{{ s.last_name }} {{ s.first_name }}</strong></td>
                  <td>{{ s.email }}</td>
                  <td class="dim" style="white-space: nowrap">{{ s.created_at | itDate: 'date' }}</td>
                  <td [attr.data-testid]="'admin-staff-status-' + s.email">
                    @if (!s.email_verified) { <span class="badge badge-muted">Email da confermare</span> }
                    @else if (s.admin_status === 'approved') { <span class="badge badge-green">Approvato</span> }
                    @else { <span class="badge">In attesa</span> }
                  </td>
                  <td class="acts">
                    @if (s.admin_status === 'approved') {
                      <button class="btn btn-ghost btn-sm" (click)="act(s, 'revoke')" [disabled]="busy() === s.id" [attr.data-testid]="'admin-staff-revoke-' + s.email">Revoca</button>
                    } @else {
                      <button class="btn btn-gold btn-sm" (click)="act(s, 'approve')" [disabled]="busy() === s.id || !s.email_verified" [attr.data-testid]="'admin-staff-approve-' + s.email">
                        <lucide-icon [img]="i.Check" [size]="15" /> Approva
                      </button>
                    }
                    <button class="btn btn-danger btn-sm btn-icon" (click)="remove(s)" [disabled]="busy() === s.id" title="Elimina" [attr.data-testid]="'admin-staff-delete-' + s.email">
                      <lucide-icon [img]="i.Trash2" [size]="15" />
                    </button>
                  </td>
                </tr>
              }
            </tbody>
          </table>
        </div>
      } @else {
        <div class="empty mt-4" data-testid="admin-staff-empty">Nessuna richiesta di accesso staff.</div>
      }
    } @else {
      <div class="skeleton mt-4" style="height: 240px"></div>
    }
  `,
  styles: `.acts { display: flex; gap: 8px; justify-content: flex-end; white-space: nowrap; }`,
})
export default class AdminStaffPage implements OnInit {
  private api = inject(AdminService);
  private toast = inject(ToastService);
  protected readonly i = Icons;
  protected staff = signal<StaffMember[] | null>(null);
  protected busy = signal('');

  ngOnInit(): void {
    this.load();
  }

  load(): void {
    this.api.staff().subscribe({ next: (s) => this.staff.set(s), error: (e) => this.toast.error(apiError(e)) });
  }

  act(s: StaffMember, action: 'approve' | 'revoke'): void {
    this.run(s, this.api.staffAction(s.id, action));
  }

  remove(s: StaffMember): void {
    if (confirm(`Eliminare definitivamente l'account di ${s.first_name} ${s.last_name}?`)) this.run(s, this.api.deleteStaff(s.id));
  }

  private run(s: StaffMember, req: ReturnType<AdminService['deleteStaff']>): void {
    this.busy.set(s.id);
    req.subscribe({
      next: (r) => {
        this.busy.set('');
        this.toast.success(r.message);
        this.load();
      },
      error: (e) => {
        this.busy.set('');
        this.toast.error(apiError(e));
      },
    });
  }
}
