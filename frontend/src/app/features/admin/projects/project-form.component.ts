import { Component, OnInit, inject, input, output, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { LucideAngularModule } from 'lucide-angular';
import { Project } from '../../../core/models/project.model';
import { AdminService } from '../../../core/services/admin.service';
import { ToastService } from '../../../core/services/toast.service';
import { apiError } from '../../../core/utils/api.utils';
import { Icons } from '../../../shared/icons';
import { ImageUploadComponent } from '../shared/image-upload.component';
import { MediaUrlPipe } from '../../../shared/pipes/media-url.pipe';

@Component({
  selector: 'app-project-form',
  imports: [ReactiveFormsModule, LucideAngularModule, ImageUploadComponent, MediaUrlPipe],
  template: `
    <div class="modal-backdrop" (click)="closed.emit()">
      <div class="modal" (click)="$event.stopPropagation()" data-testid="admin-project-form-modal">
        <div class="modal-head">
          <h2 class="h2">{{ project() ? 'Modifica progetto' : 'Nuovo progetto' }}</h2>
          <button class="btn btn-ghost btn-icon" (click)="closed.emit()" data-testid="admin-project-form-close"><lucide-icon [img]="i.X" [size]="18" /></button>
        </div>
        <form [formGroup]="form" (ngSubmit)="save()" class="form" novalidate>
          <label class="field"><span class="label">Titolo <span class="req">*</span></span>
            <input class="input" formControlName="title" data-testid="admin-project-title-input" /></label>
          <label class="field"><span class="label">Sottotitolo</span>
            <input class="input" formControlName="subtitle" data-testid="admin-project-subtitle-input" /></label>
          <div class="form-row">
            <label class="field"><span class="label">Categoria</span>
              <input class="input" formControlName="category" placeholder="es. Sport, Comunità" data-testid="admin-project-category-input" /></label>
            <label class="field"><span class="label">Anno / periodo</span>
              <input class="input" formControlName="year_label" placeholder="es. 2023, In corso" data-testid="admin-project-year-input" /></label>
          </div>
          <label class="field"><span class="label">Partner</span>
            <input class="input" formControlName="partners" placeholder="es. Città di Torino" data-testid="admin-project-partners-input" /></label>
          <label class="field"><span class="label">Sintesi</span>
            <textarea class="input" formControlName="summary" rows="2" maxlength="600" data-testid="admin-project-summary-input"></textarea></label>
          <label class="field"><span class="label">Descrizione completa</span>
            <textarea class="input" formControlName="description" rows="5" data-testid="admin-project-description-input"></textarea></label>
          <label class="field"><span class="label">Attività / punti chiave <span class="opt">(uno per riga)</span></span>
            <textarea class="input" formControlName="highlights" rows="4" data-testid="admin-project-highlights-input"></textarea></label>
          <div class="form-row">
            <label class="field"><span class="label">Immagine</span>
              <input class="input" formControlName="image_url" placeholder="/images/sport.jpg oppure https://…" data-testid="admin-project-image-input" /></label>
            <label class="field"><span class="label">Ordine</span>
              <input class="input" type="number" formControlName="sort_order" data-testid="admin-project-order-input" /></label>
          </div>
          <app-image-upload [value]="form.controls.image_url.value" testId="admin-project-image-upload" (uploaded)="form.controls.image_url.setValue($event)" />
          <div class="field">
            <span class="label">Galleria foto <span class="opt">({{ gallery().length }}/{{ maxGallery }})</span></span>
            @if (gallery().length) {
              <div class="gal" data-testid="admin-project-gallery">
                @for (g of gallery(); track g; let idx = $index) {
                  <div class="gal-item">
                    <img [src]="g | mediaUrl" alt="" />
                    <button type="button" class="gal-x" (click)="removeImage(idx)" title="Rimuovi" [attr.data-testid]="'admin-project-gallery-remove-' + idx"><lucide-icon [img]="i.X" [size]="14" /></button>
                  </div>
                }
              </div>
            }
            @if (gallery().length < maxGallery) {
              <app-image-upload value="" testId="admin-project-gallery-upload" (uploaded)="addImage($event)" />
            }
          </div>
          <label class="checkbox"><input type="checkbox" formControlName="is_published" data-testid="admin-project-published-checkbox" /> Pubblicato sul sito</label>
          @if (error()) { <div class="alert alert-error" data-testid="admin-project-form-error">{{ error() }}</div> }
          <div class="row">
            <button class="btn btn-gold" type="submit" [disabled]="saving()" data-testid="admin-project-save-button">
              @if (saving()) { <span class="spinner"></span> } Salva progetto
            </button>
            <button class="btn btn-ghost" type="button" (click)="closed.emit()">Annulla</button>
          </div>
        </form>
      </div>
    </div>
  `,
  styles: `
    .gal { display: grid; grid-template-columns: repeat(auto-fill, minmax(96px, 1fr)); gap: 10px; margin-bottom: 10px; }
    .gal-item { position: relative; aspect-ratio: 4/3; border-radius: 10px; overflow: hidden; border: 1px solid var(--gold-border); }
    .gal-item img { width: 100%; height: 100%; object-fit: cover; }
    .gal-x { position: absolute; top: 4px; right: 4px; width: 24px; height: 24px; border-radius: 50%; border: 0; display: grid; place-items: center;
      background: rgba(12,13,16,.8); color: #fff; cursor: pointer; transition: background-color .2s ease; }
    .gal-x:hover { background: var(--red); }
  `,
})
export class ProjectFormComponent implements OnInit {
  private fb = inject(FormBuilder);
  private api = inject(AdminService);
  private toast = inject(ToastService);
  readonly project = input<Project | null>(null);
  readonly closed = output<void>();
  readonly saved = output<void>();
  protected readonly i = Icons;
  protected saving = signal(false);
  protected error = signal('');
  protected gallery = signal<string[]>([]);
  protected readonly maxGallery = 12;
  protected form = this.fb.nonNullable.group({
    title: ['', [Validators.required, Validators.minLength(3)]],
    subtitle: [''],
    category: ['Comunità'],
    year_label: [''],
    partners: [''],
    summary: [''],
    description: [''],
    highlights: [''],
    image_url: [''],
    sort_order: [0],
    is_published: [true],
  });

  ngOnInit(): void {
    const p = this.project();
    if (p) {
      this.form.patchValue({ ...p, image_url: p.image_url ?? '', highlights: p.highlights.join('\n') });
      this.gallery.set(p.gallery ?? []);
    }
  }

  addImage(url: string): void {
    this.gallery.update((g) => [...g, url]);
  }

  removeImage(idx: number): void {
    this.gallery.update((g) => g.filter((_, i) => i !== idx));
  }

  save(): void {
    if (this.form.invalid) {
      this.error.set('Il titolo è obbligatorio (min. 3 caratteri)');
      return;
    }
    const v = this.form.getRawValue();
    this.saving.set(true);
    this.error.set('');
    this.api
      .saveProject(
        {
          ...v,
          title: v.title.trim(),
          image_url: v.image_url.trim() || null,
          gallery: this.gallery(),
          sort_order: Number(v.sort_order) || 0,
          highlights: v.highlights.split('\n').map((h) => h.trim()).filter(Boolean),
        },
        this.project()?.id,
      )
      .subscribe({
        next: () => {
          this.saving.set(false);
          this.toast.success('Progetto salvato');
          this.saved.emit();
        },
        error: (e) => {
          this.saving.set(false);
          this.error.set(apiError(e));
        },
      });
  }
}
