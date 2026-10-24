import { Component, inject } from '@angular/core';
import { LucideAngularModule } from 'lucide-angular';
import { ToastService } from '../../../core/services/toast.service';
import { Icons } from '../../icons';

@Component({
  selector: 'app-toast-container',
  imports: [LucideAngularModule],
  template: `
    <div class="toasts" aria-live="polite">
      @for (t of toast.toasts(); track t.id) {
        <div class="toast" [class]="'toast ' + t.type" data-testid="toast-message">
          <lucide-icon [img]="t.type === 'error' ? i.CircleAlert : t.type === 'info' ? i.Info : i.CircleCheck" [size]="18" />
          <span>{{ t.message }}</span>
          <button (click)="toast.dismiss(t.id)" aria-label="Chiudi" data-testid="toast-close-button"><lucide-icon [img]="i.X" [size]="14" /></button>
        </div>
      }
    </div>
  `,
  styles: `
    .toasts { position: fixed; bottom: 24px; right: 24px; left: 24px; z-index: 120; display: flex; flex-direction: column; align-items: flex-end; gap: 10px; pointer-events: none; }
    .toast { pointer-events: auto; display: flex; align-items: center; gap: 12px; max-width: 420px; padding: 14px 16px; border-radius: 14px; background: rgba(20,22,28,.97); backdrop-filter: blur(16px); border: 1px solid var(--gold-border-strong); box-shadow: 0 20px 50px -15px rgba(0,0,0,.7); font-size: .92rem; animation: fadeUp .35s var(--ease) both; }
    .toast.success lucide-icon:first-child { color: var(--green); }
    .toast.error { border-color: rgba(239,68,68,.45); }
    .toast.error lucide-icon:first-child { color: var(--red); }
    .toast.info lucide-icon:first-child { color: var(--gold); }
    button { background: none; border: 0; color: var(--text-3); cursor: pointer; display: flex; padding: 2px; }
  `,
})
export class ToastContainerComponent {
  protected toast = inject(ToastService);
  protected readonly i = Icons;
}
