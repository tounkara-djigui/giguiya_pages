import { Component, inject, signal } from '@angular/core';
import { AbstractControl, FormBuilder, ReactiveFormsModule, ValidationErrors, Validators } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { LucideAngularModule } from 'lucide-angular';
import { SITE } from '../../core/config';
import { AuthService } from '../../core/services/auth.service';
import { apiError } from '../../core/utils/api.utils';
import { AuthShellComponent } from '../../shared/components/auth-shell/auth-shell.component';
import { Icons } from '../../shared/icons';

const domainValidator = (c: AbstractControl): ValidationErrors | null =>
  c.value && !String(c.value).toLowerCase().endsWith('@' + SITE.adminDomain) ? { domain: true } : null;

@Component({
  selector: 'app-admin-register-page',
  imports: [ReactiveFormsModule, RouterLink, LucideAngularModule, AuthShellComponent],
  template: `
    <app-auth-shell overline="Staff Giguiya" title="Registrazione amministratore"
      [subtitle]="'Riservata agli indirizzi @' + site.adminDomain + '. Dopo la registrazione riceverai un link per confermare la tua email.'">
      @if (sent(); as s) {
        <div class="center fade-up" data-testid="admin-register-success">
          <div class="ok"><lucide-icon [img]="i.Mail" [size]="30" /></div>
          <h3 class="h3 mt-3">Controlla la tua casella</h3>
          <p class="muted mt-2">
            @if (s.emailSent) { Abbiamo inviato il link di conferma a <strong class="gold">{{ s.email }}</strong>. Il link è valido 48 ore. Dopo la conferma, l'amministratore principale dovrà approvare il tuo account. }
            @else { Account creato, ma l'invio dell'email non è riuscito. Riprova più tardi registrandoti di nuovo con la stessa email. }
          </p>
          <a routerLink="/accesso" class="btn btn-ghost mt-4">Vai al login</a>
        </div>
      } @else {
        <form [formGroup]="form" (ngSubmit)="submit()" class="form" novalidate>
          <div class="form-row">
            <label class="field"><span class="label">Nome <span class="req">*</span></span>
              <input class="input" formControlName="first_name" data-testid="admin-register-first-name-input" /></label>
            <label class="field"><span class="label">Cognome <span class="req">*</span></span>
              <input class="input" formControlName="last_name" data-testid="admin-register-last-name-input" /></label>
          </div>
          <label class="field"><span class="label">Email &#64;{{ site.adminDomain }} <span class="req">*</span></span>
            <input class="input" type="email" formControlName="email" [placeholder]="'nome@' + site.adminDomain" [class.invalid]="bad('email')" data-testid="admin-register-email-input" />
            @if (form.controls.email.hasError('domain') && bad('email')) { <span class="field-error" data-testid="admin-register-domain-error">Usa un indirizzo &#64;{{ site.adminDomain }}</span> }
          </label>
          <div class="form-row">
            <label class="field"><span class="label">Password <span class="req">*</span></span>
              <input class="input" type="password" formControlName="password" autocomplete="new-password" [class.invalid]="bad('password')" data-testid="admin-register-password-input" />
              @if (bad('password')) { <span class="field-error">Almeno 8 caratteri</span> }
            </label>
            <label class="field"><span class="label">Conferma <span class="req">*</span></span>
              <input class="input" type="password" formControlName="confirm" autocomplete="new-password" data-testid="admin-register-confirm-input" />
            </label>
          </div>
          @if (mismatch()) { <span class="field-error">Le password non coincidono</span> }
          @if (error()) { <div class="alert alert-error" data-testid="admin-register-error">{{ error() }}</div> }
          <button class="btn btn-gold btn-block" type="submit" [disabled]="loading()" data-testid="admin-register-submit-button">
            @if (loading()) { <span class="spinner"></span> } @else { <lucide-icon [img]="i.Shield" [size]="16" /> } Crea account
          </button>
          <a routerLink="/accesso" class="link-gold small">Hai già un account? Accedi</a>
        </form>
      }
    </app-auth-shell>
  `,
  styles: `
    .ok { width: 72px; height: 72px; margin: 0 auto; border-radius: 50%; display: grid; place-items: center; background: rgba(212,160,60,.1); color: var(--gold); border: 1px solid var(--gold-border-strong); }
    .gold { color: var(--gold-light); font-weight: 500; }
    .small { font-size: .88rem; }
  `,
})
export default class AdminRegisterPage {
  private fb = inject(FormBuilder);
  private auth = inject(AuthService);
  protected readonly i = Icons;
  protected readonly site = SITE;
  protected loading = signal(false);
  protected error = signal('');
  protected mismatch = signal(false);
  protected sent = signal<{ email: string; emailSent: boolean } | null>(null);
  protected form = this.fb.nonNullable.group({
    first_name: ['', Validators.required],
    last_name: ['', Validators.required],
    email: ['', [Validators.required, Validators.email, domainValidator]],
    password: ['', [Validators.required, Validators.minLength(8)]],
    confirm: ['', Validators.required],
  });

  bad(name: 'email' | 'password'): boolean {
    const c = this.form.controls[name];
    return c.invalid && c.touched;
  }

  submit(): void {
    this.form.markAllAsTouched();
    const v = this.form.getRawValue();
    this.mismatch.set(v.password !== v.confirm);
    if (this.form.invalid || this.mismatch()) return;
    this.loading.set(true);
    this.error.set('');
    const { confirm, ...data } = v;
    this.auth.registerAdmin(data).subscribe({
      next: (r) => {
        this.loading.set(false);
        this.sent.set({ email: data.email, emailSent: !!r.email_sent });
      },
      error: (e) => {
        this.loading.set(false);
        this.error.set(apiError(e));
      },
    });
  }
}
