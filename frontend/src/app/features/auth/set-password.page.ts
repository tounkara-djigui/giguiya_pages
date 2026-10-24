import { Component, inject, input, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { LucideAngularModule } from 'lucide-angular';
import { AuthService } from '../../core/services/auth.service';
import { apiError } from '../../core/utils/api.utils';
import { AuthShellComponent } from '../../shared/components/auth-shell/auth-shell.component';
import { Icons } from '../../shared/icons';

@Component({
  selector: 'app-set-password-page',
  imports: [ReactiveFormsModule, RouterLink, LucideAngularModule, AuthShellComponent],
  template: `
    <app-auth-shell overline="Area soci" title="Crea la tua password" subtitle="Scegli una password personale per accedere al sito e controllare la tua situazione associativa.">
      @if (done()) {
        <div class="center fade-up" data-testid="set-password-success">
          <div class="ok"><lucide-icon [img]="i.CircleCheck" [size]="32" /></div>
          <h3 class="h3 mt-3">Password impostata!</h3>
          <p class="muted mt-2">Ora puoi accedere con la tua email e la nuova password.</p>
          <a routerLink="/accesso" class="btn btn-gold mt-4" data-testid="set-password-login-button">Accedi</a>
        </div>
      } @else if (!token()) {
        <div class="alert alert-error" data-testid="set-password-missing-token">Link non valido. Usa il pulsante ricevuto via email.</div>
      } @else {
        <form [formGroup]="form" (ngSubmit)="submit()" class="form" novalidate>
          <label class="field"><span class="label">Nuova password</span>
            <input class="input" type="password" formControlName="password" autocomplete="new-password" data-testid="set-password-input" />
            <span class="dim small">Almeno 8 caratteri</span>
          </label>
          <label class="field"><span class="label">Conferma password</span>
            <input class="input" type="password" formControlName="confirm" autocomplete="new-password" data-testid="set-password-confirm-input" />
          </label>
          @if (error()) { <div class="alert alert-error" data-testid="set-password-error">{{ error() }}</div> }
          <button class="btn btn-gold btn-block" type="submit" [disabled]="loading()" data-testid="set-password-submit-button">
            @if (loading()) { <span class="spinner"></span> } @else { <lucide-icon [img]="i.KeyRound" [size]="16" /> } Salva password
          </button>
        </form>
      }
    </app-auth-shell>
  `,
  styles: `
    .ok { width: 72px; height: 72px; margin: 0 auto; border-radius: 50%; display: grid; place-items: center; background: rgba(16,185,129,.12); color: var(--green); border: 1px solid rgba(16,185,129,.4); }
    .small { font-size: .8rem; }
  `,
})
export default class SetPasswordPage {
  private fb = inject(FormBuilder);
  private auth = inject(AuthService);
  readonly token = input<string>();
  protected readonly i = Icons;
  protected loading = signal(false);
  protected error = signal('');
  protected done = signal(false);
  protected form = this.fb.nonNullable.group({
    password: ['', [Validators.required, Validators.minLength(8)]],
    confirm: ['', Validators.required],
  });

  submit(): void {
    const { password, confirm } = this.form.getRawValue();
    if (password.length < 8) return this.error.set('La password deve avere almeno 8 caratteri');
    if (password !== confirm) return this.error.set('Le password non coincidono');
    this.loading.set(true);
    this.error.set('');
    this.auth.setPassword(this.token()!, password).subscribe({
      next: () => {
        this.loading.set(false);
        this.done.set(true);
      },
      error: (e) => {
        this.loading.set(false);
        this.error.set(apiError(e));
      },
    });
  }
}
