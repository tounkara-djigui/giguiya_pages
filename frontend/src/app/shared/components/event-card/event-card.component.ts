import { Component, input } from '@angular/core';
import { RouterLink } from '@angular/router';
import { LucideAngularModule } from 'lucide-angular';
import { EventItem } from '../../../core/models/event.model';
import { Icons } from '../../icons';
import { ItDatePipe } from '../../pipes/it-date.pipe';
import { MediaUrlPipe } from '../../pipes/media-url.pipe';

@Component({
  selector: 'app-event-card',
  imports: [RouterLink, LucideAngularModule, ItDatePipe, MediaUrlPipe],
  template: `
    @let e = event();
    <a [routerLink]="['/eventi', e.slug]" class="ev card-hover" [attr.data-testid]="'event-card-' + e.slug">
      <div class="media">
        <img [src]="e.image_url | mediaUrl" [alt]="e.title" loading="lazy" />
        <div class="date">
          <span class="d">{{ e.start_at | itDate: 'day' }}</span>
          <span class="m">{{ e.start_at | itDate: 'month' }}</span>
        </div>
        <span class="badge cat">{{ e.category }}</span>
      </div>
      <div class="body">
        <h3 class="title">{{ e.title }}</h3>
        <p class="muted sum">{{ e.summary }}</p>
        <div class="meta">
          <span class="info-row"><lucide-icon [img]="i.Clock" [size]="15" /> {{ e.start_at | itDate: 'weekday' }} · {{ e.start_at | itDate: 'time' }}</span>
          <span class="info-row"><lucide-icon [img]="i.MapPin" [size]="15" /> {{ e.location || 'Torino' }}</span>
        </div>
        <div class="foot">
          @if (e.is_past) {
            <span class="badge badge-muted">Concluso</span>
          } @else if (e.spots_left === 0) {
            <span class="badge badge-red">Al completo</span>
          } @else if (e.spots_left !== null) {
            <span class="badge">{{ e.spots_left }} posti liberi</span>
          } @else {
            <span class="badge">{{ e.price_label || 'Aperto a tutti' }}</span>
          }
          <span class="link-gold">{{ e.is_past ? 'Dettagli' : 'Prenota' }} <lucide-icon [img]="i.ArrowUpRight" [size]="16" /></span>
        </div>
      </div>
    </a>
  `,
  styles: `
    .ev { display: flex; flex-direction: column; height: 100%; background: var(--bg-card); border: 1px solid var(--gold-border); border-radius: var(--radius); overflow: hidden; }
    .media { position: relative; aspect-ratio: 16/10; overflow: hidden; }
    .media img { width: 100%; height: 100%; object-fit: cover; transition: transform 1.2s var(--ease); }
    .ev:hover .media img { transform: scale(1.06); }
    .media::after { content: ''; position: absolute; inset: 0; background: linear-gradient(180deg, transparent 40%, rgba(12,13,16,.85)); }
    .date { position: absolute; top: 16px; left: 16px; z-index: 1; display: flex; flex-direction: column; align-items: center; padding: 8px 14px; border-radius: 12px; background: rgba(12,13,16,.85); backdrop-filter: blur(12px); border: 1px solid var(--gold-border-strong); }
    .d { font-family: var(--font-display); font-size: 1.7rem; line-height: 1; color: var(--gold-light); }
    .m { font-family: var(--font-mono); font-size: .65rem; letter-spacing: .15em; text-transform: uppercase; color: var(--text-2); }
    .cat { position: absolute; bottom: 14px; left: 16px; z-index: 1; }
    .body { padding: 24px 26px 26px; display: flex; flex-direction: column; gap: 12px; flex: 1; }
    .title { font-size: 1.6rem; }
    .sum { font-size: .92rem; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
    .meta { display: flex; flex-direction: column; gap: 6px; margin-top: 4px; }
    .meta .info-row { font-size: .85rem; }
    .foot { margin-top: auto; padding-top: 16px; border-top: 1px solid rgba(255,255,255,.06); display: flex; justify-content: space-between; align-items: center; }
  `,
})
export class EventCardComponent {
  readonly event = input.required<EventItem>();
  protected readonly i = Icons;
}
