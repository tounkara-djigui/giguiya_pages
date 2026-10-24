import { Component, OnInit, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { LucideAngularModule } from 'lucide-angular';
import { MemberDashboard } from '../../core/models/member.model';
import { AuthService } from '../../core/services/auth.service';
import { MemberService } from '../../core/services/member.service';
import { ToastService } from '../../core/services/toast.service';
import { apiError } from '../../core/utils/api.utils';
import { Icons } from '../../shared/icons';
import { ItDatePipe } from '../../shared/pipes/it-date.pipe';

@Component({
  selector: 'app-member-dashboard-page',
  imports: [RouterLink, ReactiveFormsModule, LucideAngularModule, ItDatePipe],
  templateUrl: './member-dashboard.page.html',
  styleUrl: './member-dashboard.page.scss',
})
export default class MemberDashboardPage implements OnInit {
  private api = inject(MemberService);
  private auth = inject(AuthService);
  private toast = inject(ToastService);
  private fb = inject(FormBuilder);
  protected readonly i = Icons;
  protected data = signal<MemberDashboard | null>(null);
  protected error = signal('');
  protected pwdLoading = signal(false);
  protected pwdForm = this.fb.nonNullable.group({
    current: ['', Validators.required],
    next: ['', [Validators.required, Validators.minLength(8)]],
  });

  ngOnInit(): void {
    this.api.dashboard().subscribe({
      next: (d) => this.data.set(d),
      error: (e) => this.error.set(apiError(e)),
    });
  }

  logout(): void {
    this.auth.logout();
  }

  changePassword(): void {
    if (this.pwdForm.invalid) return;
    const { current, next } = this.pwdForm.getRawValue();
    this.pwdLoading.set(true);
    this.auth.changePassword(current, next).subscribe({
      next: () => {
        this.pwdLoading.set(false);
        this.pwdForm.reset();
        this.toast.success('Password aggiornata');
      },
      error: (e) => {
        this.pwdLoading.set(false);
        this.toast.error(apiError(e));
      },
    });
  }
}
