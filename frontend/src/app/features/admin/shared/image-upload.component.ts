import { Component, inject, input, output, signal } from '@angular/core';
import { LucideAngularModule } from 'lucide-angular';
import { AdminService } from '../../../core/services/admin.service';
import { ToastService } from '../../../core/services/toast.service';
import { apiError } from '../../../core/utils/api.utils';
import { Icons } from '../../../shared/icons';
import { mediaUrl } from '../../../shared/pipes/media-url.pipe';

const MAX_MB = 8;

@Component({
  selector: 'app-image-upload',
  imports: [LucideAngularModule],
  template: `
    <div class="up">
      @if (value()) {
        <img [src]="preview()" alt="Anteprima" class="thumb" data-testid="image-upload-preview" />
      }
      <label class="btn btn-ghost btn-sm" [class.disabled]="loading()" [attr.data-testid]="testId() + '-button'">
        @if (loading()) { <span class="spinner"></span> Caricamento… } @else { <lucide-icon [img]="i.Plus" [size]="15" /> Carica immagine }
        <input type="file" accept="image/jpeg,image/png,image/webp,image/gif" hidden (change)="onFile($event)" [attr.data-testid]="testId() + '-input'" />
      </label>
      <span class="dim hint">JPG, PNG, WEBP o GIF · max {{ maxMb }} MB</span>
    </div>
  `,
  styles: `
    .up { display: flex; align-items: center; gap: 14px; flex-wrap: wrap; }
    .thumb { width: 96px; height: 64px; object-fit: cover; border-radius: 10px; border: 1px solid var(--gold-border); }
    .hint { font-size: .78rem; }
    .disabled { pointer-events: none; opacity: .6; }
  `,
})
export class ImageUploadComponent {
  private api = inject(AdminService);
  private toast = inject(ToastService);
  readonly value = input<string | null>('');
  readonly testId = input('image-upload');
  readonly uploaded = output<string>();
  protected readonly i = Icons;
  protected readonly maxMb = MAX_MB;
  protected loading = signal(false);

  preview(): string {
    return mediaUrl(this.value());
  }

  onFile(e: Event): void {
    const el = e.target as HTMLInputElement;
    const file = el.files?.[0];
    el.value = '';
    if (!file) return;
    if (file.size > MAX_MB * 1024 * 1024) {
      this.toast.error(`Immagine troppo grande (massimo ${MAX_MB} MB)`);
      return;
    }
    this.loading.set(true);
    this.api.uploadImage(file).subscribe({
      next: (r) => {
        this.loading.set(false);
        this.uploaded.emit(r.url);
        this.toast.success('Immagine caricata');
      },
      error: (err) => {
        this.loading.set(false);
        this.toast.error(apiError(err));
      },
    });
  }
}
