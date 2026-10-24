import { Component, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { LucideAngularModule } from 'lucide-angular';
import { AuthService } from '../../core/services/auth.service';
import { apiError } from '../../core/utils/api.utils';
import { AuthShellComponent } from '../../shared/components/auth-shell/auth-shell.component';
import { Icons } from '../../shared/icons';

@Component({
  selector: 'app-forgot-password-page',
  imports: [ReactiveFormsModule, RouterLink, LucideAngularModule, AuthShellComponent],
  template: `
    <app-auth-shell overline="Recupero" title="Password dimenticata" subtitle="Inserisci la tua email: ti invieremo un link per impostare una nuova password.">
      @if (message()) {
        <div class="alert alert-success" data-testid="forgot-password-success">{{ message() }}</div>
        <a routerLink="/accesso" class="btn btn-ghost mt-4">Torna al login</a>
      } @else {
        <form [formGroup]="form" (ngSubmit)="submit()" class="form" novalidate>
          <label class="field"><span class="label">Email</span>
            <input class="input" type="email" formControlName="email" data-testid="forgot-password-email-input" /></label>
          @if (error()) { <div class="alert alert-error">{{ error() }}</div> }
          <button class="btn btn-gold btn-block" type="submit" [disabled]="loading() || form.invalid" data-testid="forgot-password-submit-button">
            @if (loading()) { <span class="spinner"></span> } @else { <lucide-icon [img]="i.Send" [size]="16" /> } Invia link
          </button>
          <a routerLink="/accesso" class="link-gold">Torna al login</a>
        </form>
      }
    </app-auth-shell>
  `,
})
export default class ForgotPasswordPage {
  private fb = inject(FormBuilder);
  private auth = inject(AuthService);
  protected readonly i = Icons;
  protected loading = signal(false);
  protected error = signal('');
  protected message = signal('');
  protected form = this.fb.nonNullable.group({ email: ['', [Validators.required, Validators.email]] });

  submit(): void {
    this.loading.set(true);
    this.auth.forgotPassword(this.form.getRawValue().email).subscribe({
      next: (r) => {
        this.loading.set(false);
        this.message.set(r.message);
      },
      error: (e) => {
        this.loading.set(false);
        this.error.set(apiError(e));
      },
    });
  }
}
