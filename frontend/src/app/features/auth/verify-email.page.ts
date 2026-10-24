import { Component, OnInit, inject, input, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { LucideAngularModule } from 'lucide-angular';
import { AuthService } from '../../core/services/auth.service';
import { apiError } from '../../core/utils/api.utils';
import { AuthShellComponent } from '../../shared/components/auth-shell/auth-shell.component';
import { Icons } from '../../shared/icons';

@Component({
  selector: 'app-verify-email-page',
  imports: [RouterLink, LucideAngularModule, AuthShellComponent],
  template: `
    <app-auth-shell overline="Verifica email" title="Conferma account">
      <div class="center" data-testid="verify-email-status">
        @switch (state()) {
          @case ('loading') { <p class="muted">Verifica in corso…</p> }
          @case ('ok') {
            <div class="ic ok"><lucide-icon [img]="i.CircleCheck" [size]="32" /></div>
            <h3 class="h3 mt-3" data-testid="verify-email-success">Email confermata!</h3>
            <p class="muted mt-2">Il tuo account amministratore è attivo.</p>
            <a routerLink="/accesso" class="btn btn-gold mt-4" data-testid="verify-email-login-button">Accedi ora</a>
          }
          @default {
            <div class="ic ko"><lucide-icon [img]="i.CircleAlert" [size]="32" /></div>
            <h3 class="h3 mt-3" data-testid="verify-email-error">Link non valido</h3>
            <p class="muted mt-2">{{ message() }}</p>
            <a routerLink="/accesso/registrazione-admin" class="btn btn-ghost mt-4">Richiedi un nuovo link</a>
          }
        }
      </div>
    </app-auth-shell>
  `,
  styles: `
    .ic { width: 72px; height: 72px; margin: 0 auto; border-radius: 50%; display: grid; place-items: center; }
    .ok { background: rgba(16,185,129,.12); color: var(--green); border: 1px solid rgba(16,185,129,.4); }
    .ko { background: rgba(239,68,68,.1); color: var(--red); border: 1px solid rgba(239,68,68,.35); }
  `,
})
export default class VerifyEmailPage implements OnInit {
  private auth = inject(AuthService);
  readonly token = input<string>();
  protected readonly i = Icons;
  protected state = signal<'loading' | 'ok' | 'error'>('loading');
  protected message = signal('Il link è scaduto o è già stato utilizzato.');

  ngOnInit(): void {
    const token = this.token();
    if (!token) {
      this.state.set('error');
      return;
    }
    this.auth.verifyEmail(token).subscribe({
      next: () => this.state.set('ok'),
      error: (e) => {
        this.message.set(apiError(e));
        this.state.set('error');
      },
    });
  }
}
