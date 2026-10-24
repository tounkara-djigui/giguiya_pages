import { Component, OnInit, inject, input, output, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { LucideAngularModule } from 'lucide-angular';
import { EVENT_CATEGORIES, EventItem } from '../../../core/models/event.model';
import { AdminService } from '../../../core/services/admin.service';
import { ToastService } from '../../../core/services/toast.service';
import { apiError } from '../../../core/utils/api.utils';
import { Icons } from '../../../shared/icons';

@Component({
  selector: 'app-event-form',
  imports: [ReactiveFormsModule, LucideAngularModule],
  template: `
    <div class="modal-backdrop" (click)="closed.emit()">
      <div class="modal" (click)="$event.stopPropagation()" data-testid="admin-event-form-modal">
        <div class="modal-head">
          <h2 class="h2">{{ event() ? 'Modifica evento' : 'Nuovo evento' }}</h2>
          <button class="btn btn-ghost btn-icon" (click)="closed.emit()" data-testid="admin-event-form-close"><lucide-icon [img]="i.X" [size]="18" /></button>
        </div>
        <form [formGroup]="form" (ngSubmit)="save()" class="form" novalidate>
          <label class="field"><span class="label">Titolo <span class="req">*</span></span>
            <input class="input" formControlName="title" data-testid="admin-event-title-input" /></label>
          <label class="field"><span class="label">Breve descrizione</span>
            <input class="input" formControlName="summary" maxlength="400" data-testid="admin-event-summary-input" /></label>
          <label class="field"><span class="label">Descrizione completa</span>
            <textarea class="input" formControlName="description" rows="5" data-testid="admin-event-description-input"></textarea></label>
          <div class="form-row">
            <label class="field"><span class="label">Categoria</span>
              <select class="input" formControlName="category" data-testid="admin-event-category-select">
                @for (c of categories; track c) { <option [value]="c">{{ c }}</option> }
              </select></label>
            <label class="field"><span class="label">Luogo</span>
              <input class="input" formControlName="location" data-testid="admin-event-location-input" /></label>
          </div>
          <div class="form-row">
            <label class="field"><span class="label">Inizio <span class="req">*</span></span>
              <input class="input" type="datetime-local" formControlName="start_at" data-testid="admin-event-start-input" /></label>
            <label class="field"><span class="label">Fine</span>
              <input class="input" type="datetime-local" formControlName="end_at" data-testid="admin-event-end-input" /></label>
          </div>
          <div class="form-row">
            <label class="field"><span class="label">Posti disponibili <span class="opt">(vuoto = illimitati)</span></span>
              <input class="input" type="number" min="1" formControlName="capacity" data-testid="admin-event-capacity-input" /></label>
            <label class="field"><span class="label">Partecipazione</span>
              <input class="input" formControlName="price_label" placeholder="es. Gratuito, 10€" data-testid="admin-event-price-input" /></label>
          </div>
          <label class="field"><span class="label">URL immagine</span>
            <input class="input" formControlName="image_url" placeholder="/images/musica.jpg oppure https://…" data-testid="admin-event-image-input" /></label>
          <label class="checkbox"><input type="checkbox" formControlName="is_published" data-testid="admin-event-published-checkbox" /> Pubblicato sul sito</label>
          @if (error()) { <div class="alert alert-error" data-testid="admin-event-form-error">{{ error() }}</div> }
          <div class="row">
            <button class="btn btn-gold" type="submit" [disabled]="saving()" data-testid="admin-event-save-button">
              @if (saving()) { <span class="spinner"></span> } Salva evento
            </button>
            <button class="btn btn-ghost" type="button" (click)="closed.emit()">Annulla</button>
          </div>
        </form>
      </div>
    </div>
  `,
})
export class EventFormComponent implements OnInit {
  private fb = inject(FormBuilder);
  private api = inject(AdminService);
  private toast = inject(ToastService);
  readonly event = input<EventItem | null>(null);
  readonly closed = output<void>();
  readonly saved = output<void>();
  protected readonly i = Icons;
  protected readonly categories = EVENT_CATEGORIES;
  protected saving = signal(false);
  protected error = signal('');
  protected form = this.fb.group({
    title: ['', [Validators.required, Validators.minLength(3)]],
    summary: [''],
    description: [''],
    category: ['Cultura'],
    location: [''],
    start_at: ['', Validators.required],
    end_at: [''],
    capacity: [null as number | null],
    price_label: [''],
    image_url: [''],
    is_published: [true],
  });

  ngOnInit(): void {
    const e = this.event();
    if (e) {
      this.form.patchValue({ ...e, start_at: e.start_local ?? '', end_at: e.end_local ?? '' });
    }
  }

  save(): void {
    this.form.markAllAsTouched();
    if (this.form.invalid) {
      this.error.set('Compila titolo (min. 3 caratteri) e data di inizio');
      return;
    }
    const v = this.form.getRawValue();
    this.saving.set(true);
    this.error.set('');
    this.api
      .saveEvent(
        {
          title: v.title!.trim(), summary: v.summary ?? '', description: v.description ?? '', category: v.category ?? 'Cultura',
          location: v.location ?? '', start_at: v.start_at!, end_at: v.end_at || null,
          capacity: v.capacity ? Number(v.capacity) : null, price_label: v.price_label || null,
          image_url: v.image_url || null, is_published: !!v.is_published,
        },
        this.event()?.id,
      )
      .subscribe({
        next: () => {
          this.saving.set(false);
          this.toast.success('Evento salvato');
          this.saved.emit();
        },
        error: (e) => {
          this.saving.set(false);
          this.error.set(apiError(e));
        },
      });
  }
}
