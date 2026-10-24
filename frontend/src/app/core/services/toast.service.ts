import { Injectable, signal } from '@angular/core';

export interface Toast {
  id: number;
  type: 'success' | 'error' | 'info';
  message: string;
}

@Injectable({ providedIn: 'root' })
export class ToastService {
  readonly toasts = signal<Toast[]>([]);
  private seq = 0;

  show(message: string, type: Toast['type'] = 'success', ms = 4500): void {
    const id = ++this.seq;
    this.toasts.update((t) => [...t, { id, type, message }]);
    setTimeout(() => this.dismiss(id), ms);
  }

  success(message: string) { this.show(message, 'success'); }
  error(message: string) { this.show(message, 'error', 6000); }
  info(message: string) { this.show(message, 'info'); }

  dismiss(id: number): void {
    this.toasts.update((t) => t.filter((x) => x.id !== id));
  }
}
