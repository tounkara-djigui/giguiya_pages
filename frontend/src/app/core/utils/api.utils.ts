import { HttpErrorResponse } from '@angular/common/http';

export function apiError(err: unknown): string {
  if (!(err instanceof HttpErrorResponse)) return 'Si è verificato un errore. Riprova.';
  const detail = err.error?.detail;
  if (typeof detail === 'string') return detail;
  if (Array.isArray(detail)) {
    return detail
      .map((d) => (typeof d?.msg === 'string' ? d.msg.replace(/^Value error, /, '') : ''))
      .filter(Boolean)
      .join(' ');
  }
  if (err.status === 0) return 'Impossibile contattare il server. Controlla la connessione.';
  return 'Si è verificato un errore. Riprova.';
}

export function downloadCsv(filename: string, rows: (string | number | null | undefined)[][]): void {
  const csv = rows
    .map((r) => r.map((c) => `"${String(c ?? '').replace(/"/g, '""')}"`).join(';'))
    .join('\n');
  const blob = new Blob(['\ufeff' + csv], { type: 'text/csv;charset=utf-8' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = filename;
  a.click();
  URL.revokeObjectURL(a.href);
}
