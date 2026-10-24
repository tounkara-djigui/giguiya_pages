import { Component, inject, input, output, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { LucideAngularModule } from 'lucide-angular';
import { EventItem } from '../../core/models/event.model';
import { PublicService } from '../../core/services/public.service';
import { ToastService } from '../../core/services/toast.service';
import { apiError } from '../../core/utils/api.utils';
import { Icons } from '../../shared/icons';

@Component({
  selector: 'app-booking-form',
  imports: [ReactiveFormsModule, LucideAngularModule, RouterLink],
  template: `
    <div class="card booking" data-testid="booking-card">
      <div class="halo"></div>
      @if (done(); as d) {
        <div class="success fade-up" data-testid="booking-success">
          <div class="ok"><lucide-icon [img]="i.CircleCheck" [size]="34" /></div>
          <h3 class="h3 mt-2">Prenotazione confermata!</h3>
          <p class="muted mt-2">
            @if (d.emailSent) {
              Ti abbiamo inviato un'email di conferma a <strong class="gold">{{ d.email }}</strong>.
            } @else {
              La prenotazione è registrata, ma al momento non siamo riusciti a inviare l'email di conferma.
            }
          </p>
          <div class="row mt-3" style="justify-content: center">
            <button class="btn btn-ghost btn-sm" (click)="done.set(null)" data-testid="booking-new-button">Nuova prenotazione</button>
            <a routerLink="/diventa-socio" class="btn btn-gold btn-sm" data-testid="booking-become-member-link">Diventa socio</a>
          </div>
        </div>
      } @else {
        <div class="rel">
          <span class="overline">Prenota</span>
          <h3 class="h3 mt-2">Riserva il tuo posto</h3>
          @if (event().spots_left !== null) {
            <p class="dim mt-1" data-testid="booking-spots-left">{{ event().spots_left }} posti disponibili</p>
          }
          <form [formGroup]="form" (ngSubmit)="submit()" class="form mt-3" novalidate>
            <div class="form-row">
              <label class="field"><span class="label">Nome <span class="req">*</span></span>
                <input class="input" formControlName="first_name" [class.invalid]="bad('first_name')" autocomplete="given-name" data-testid="booking-first-name-input" />
                @if (bad('first_name')) { <span class="field-error">Il nome è obbligatorio</span> }
              </label>
              <label class="field"><span class="label">Cognome <span class="req">*</span></span>
                <input class="input" formControlName="last_name" [class.invalid]="bad('last_name')" autocomplete="family-name" data-testid="booking-last-name-input" />
                @if (bad('last_name')) { <span class="field-error">Il cognome è obbligatorio</span> }
              </label>
            </div>
            <label class="field"><span class="label">Email <span class="req">*</span></span>
              <input class="input" type="email" formControlName="email" [class.invalid]="bad('email')" autocomplete="email" data-testid="booking-email-input" />
              @if (bad('email')) { <span class="field-error">Inserisci un'email valida</span> }
            </label>
            <label class="field"><span class="label">Telefono <span class="opt">(opzionale)</span></span>
              <input class="input" type="tel" formControlName="phone" autocomplete="tel" data-testid="booking-phone-input" />
            </label>
            @if (error()) { <div class="alert alert-error" data-testid="booking-error">{{ error() }}</div> }
            <button type="submit" class="btn btn-gold btn-block" [disabled]="loading()" data-testid="event-booking-submit-button">
              @if (loading()) { <span class="spinner"></span> } @else { <lucide-icon [img]="i.Send" [size]="16" /> }
              Conferma prenotazione
            </button>
            <p class="dim tiny">Riceverai un'email di conferma. I tuoi dati sono usati solo per la gestione dell'evento.</p>
          </form>
        </div>
      }
    </div>
  `,
  styles: `
    .booking { overflow: hidden; }
    .rel { position: relative; }
    .tiny { font-size: .78rem; }
    .success { text-align: center; position: relative; padding: 12px 0; }
    .ok { width: 72px; height: 72px; margin: 0 auto; border-radius: 50%; display: grid; place-items: center; background: rgba(16,185,129,.12); color: var(--green); border: 1px solid rgba(16,185,129,.4); }
    .gold { color: var(--gold-light); font-weight: 500; }
  `,
})
export class BookingFormComponent {
  private fb = inject(FormBuilder);
  private api = inject(PublicService);
  private toast = inject(ToastService);
  readonly event = input.required<EventItem>();
  readonly booked = output<void>();
  protected readonly i = Icons;
  protected loading = signal(false);
  protected error = signal('');
  protected done = signal<{ email: string; emailSent: boolean } | null>(null);

  protected form = this.fb.nonNullable.group({
    first_name: ['', [Validators.required, Validators.maxLength(100)]],
    last_name: ['', [Validators.required, Validators.maxLength(100)]],
    email: ['', [Validators.required, Validators.email]],
    phone: [''],
  });

  bad(name: keyof typeof this.form.controls): boolean {
    const c = this.form.controls[name];
    return c.invalid && (c.touched || c.dirty);
  }

  submit(): void {
    this.form.markAllAsTouched();
    if (this.form.invalid) return;
    this.loading.set(true);
    this.error.set('');
    const v = this.form.getRawValue();
    this.api.book(this.event().slug, { ...v, phone: v.phone.trim() || null }).subscribe({
      next: (res) => {
        this.loading.set(false);
        this.done.set({ email: v.email, emailSent: res.email_sent });
        this.toast.success('Prenotazione confermata!');
        this.form.reset();
        this.booked.emit();
      },
      error: (err) => {
        this.loading.set(false);
        this.error.set(apiError(err));
      },
    });
  }
}
