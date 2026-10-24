import { Pipe, PipeTransform } from '@angular/core';
import { environment } from '../../../environments/environment';

export function mediaUrl(url: string | null | undefined, fallback = ''): string {
  if (!url) return fallback;
  if (url.startsWith('/api/')) return `${environment.apiUrl}${url}`;
  return url.startsWith('/') ? url.slice(1) : url;
}

@Pipe({ name: 'mediaUrl' })
export class MediaUrlPipe implements PipeTransform {
  transform(url: string | null | undefined, fallback = 'images/community.jpg'): string {
    return mediaUrl(url, fallback);
  }
}
