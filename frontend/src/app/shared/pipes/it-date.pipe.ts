import { Pipe, PipeTransform } from '@angular/core';

type Mode = 'full' | 'date' | 'time' | 'day' | 'month' | 'weekday' | 'datetime';

const OPTIONS: Record<Mode, Intl.DateTimeFormatOptions> = {
  full: { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' },
  date: { day: '2-digit', month: '2-digit', year: 'numeric' },
  time: { hour: '2-digit', minute: '2-digit' },
  day: { day: '2-digit' },
  month: { month: 'short' },
  weekday: { weekday: 'short' },
  datetime: { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' },
};

@Pipe({ name: 'itDate' })
export class ItDatePipe implements PipeTransform {
  transform(value: string | null | undefined, mode: Mode = 'full'): string {
    if (!value) return '';
    return new Intl.DateTimeFormat('it-IT', { ...OPTIONS[mode], timeZone: 'Europe/Rome' }).format(new Date(value));
  }
}
