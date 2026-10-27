import { Component, inject, input, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { LucideAngularModule } from 'lucide-angular';
import { SITE } from '../../core/config';
import { AuthService } from '../../core/services/auth.service';
import { apiError } from '../../core/utils/api.utils';
import { AuthShellComponent } from '../../shared/components/auth-shell/auth-shell.component';
import { Icons } from '../../shared/icons';

@Component({
  selector: 'app-login-page',
  imports: [ReactiveFormsModule, RouterLink, LucideAngularModule, AuthShellComponent],
  template: `
    <app-auth-shell overline="Accesso" title="Bentornato" subtitle="Accedi all'area soci per controllare la tua situazione associativa, oppure all'area di gestione se fai parte dello staff.">
      <form [formGroup]="form" (ngSubmit)="submit()" class="form" novalidate>
        <label class="field"><span class="label">Email</span>
          <input class="input" type="email" formControlName="email" autocomplete="email" data-testid="login-email-input" />
        </label>
        <label class="field"><span class="label">Password</span>
          <input class="input" type="password" formControlName="password" autocomplete="current-password" data-testid="login-password-input" />
        </label>
        <div class="row-between">
          <span></span>
          <a routerLink="/accesso/password-dimenticata" class="link-gold small" data-testid="login-forgot-link">Password dimenticata?</a>
        </div>
        @if (error()) { <div class="alert alert-error" data-testid="login-error">{{ error() }}</div> }
        <button class="btn btn-gold btn-block" type="submit" [disabled]="loading() || form.invalid" data-testid="login-submit-button">
          @if (loading()) { <span class="spinner"></span> } @else { <lucide-icon [img]="i.LogIn" [size]="16" /> } Accedi
        </button>
      </form>
      <hr class="divider mt-4" />
      <div class="alt mt-4">
        <a routerLink="/diventa-socio" class="alt-item" data-testid="login-become-member-link">
          <lucide-icon [img]="i.UserPlus" [size]="20" />
          <span><strong>Non sei ancora socio?</strong><small>Registrati come nuovo socio</small></span>
        </a>
        <a routerLink="/accesso/registrazione-admin" class="alt-item" data-testid="login-admin-register-link">
          <lucide-icon [img]="i.Shield" [size]="20" />
          <span><strong>Staff Giguiya</strong><small>Crea l'account dell'area di gestione</small></span>
        </a>
      </div>
    </app-auth-shell>
  `,
  styles: `
    .small { font-size: .85rem; }
    .alt { display: grid; gap: 10px; }
    .alt-item { display: flex; gap: 14px; align-items: center; padding: 14px 16px; border-radius: 12px; border: 1px solid var(--line); transition: border-color .2s ease, background-color .2s ease; }
    .alt-item:hover { border-color: var(--gold-border-strong); background: rgba(212,160,60,.05); }
    .alt-item lucide-icon { color: var(--gold); }
    .alt-item span { display: flex; flex-direction: column; }
    .alt-item strong { font-weight: 500; }
    .alt-item small { color: var(--text-3); }
  `,
})
export default class LoginPage {
  private fb = inject(FormBuilder);
  private auth = inject(AuthService);
  private router = inject(Router);
  readonly redirect = input<string>();
  protected readonly i = Icons;
  protected readonly site = SITE;
  protected loading = signal(false);
  protected error = signal('');
  protected form = this.fb.nonNullable.group({
    email: ['', [Validators.required, Validators.email]],
    password: ['', Validators.required],
  });

  constructor() {
    const u = this.auth.user();
    if (u) this.router.navigateByUrl(this.auth.homeFor(u));
  }

  submit(): void {
    if (this.form.invalid) return;
    this.loading.set(true);
    this.error.set('');
    const { email, password } = this.form.getRawValue();
    this.auth.login(email, password).subscribe({
      next: (u) => {
        const target = this.redirect();
        const allowed = target && target.startsWith(u.role === 'admin' ? '/admin' : '/area-socio');
        this.router.navigateByUrl(allowed ? target : this.auth.homeFor(u));
      },
      error: (e) => {
        this.loading.set(false);
        this.error.set(apiError(e));
      },
    });
  }
}
