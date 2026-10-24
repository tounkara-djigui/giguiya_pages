import { Injectable, signal } from '@angular/core';

export interface Toast {
  id: number;
  type: 'success' | 'error' | 'info';
  message: string;
}

const DEFAULT_TOAST_DURATION_MS = 4500;
const ERROR_TOAST_DURATION_MS = 6000;

@Injectable({ providedIn: 'root' })
export class ToastService {
  readonly toasts = signal<Toast[]>([]);
  private seq = 0;

  show(message: string, type: Toast['type'] = 'success', ms = DEFAULT_TOAST_DURATION_MS): void {
    const id = ++this.seq;
    this.toasts.update((t) => [...t, { id, type, message }]);
    setTimeout(() => this.dismiss(id), ms);
  }

  success(message: string) { this.show(message, 'success'); }
  error(message: string) { this.show(message, 'error', ERROR_TOAST_DURATION_MS); }
  info(message: string) { this.show(message, 'info'); }

  dismiss(id: number): void {
    this.toasts.update((t) => t.filter((x) => x.id !== id));
  }
}
