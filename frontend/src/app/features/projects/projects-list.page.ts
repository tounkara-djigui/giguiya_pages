import { Component, inject } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { RouterLink } from '@angular/router';
import { LucideAngularModule } from 'lucide-angular';
import { catchError, of } from 'rxjs';
import { AuthService } from '../../core/services/auth.service';
import { PublicService } from '../../core/services/public.service';
import { PageHeaderComponent } from '../../shared/components/page-header/page-header.component';
import { RevealDirective } from '../../shared/directives/reveal.directive';
import { Icons } from '../../shared/icons';
import { MediaUrlPipe } from '../../shared/pipes/media-url.pipe';

@Component({
  selector: 'app-projects-list-page',
  imports: [RouterLink, LucideAngularModule, PageHeaderComponent, RevealDirective, MediaUrlPipe],
  template: `
    <app-page-header overline="I nostri progetti" title="Idee che diventano" accent="impatto" image="/images/mali-dogon.jpg"
      lead="Sport, cultura e inclusione: i progetti con cui Giguiya costruisce ogni giorno una comunità più forte e aperta.">
      @if (auth.isAdmin()) {
        <a routerLink="/admin/progetti" class="btn btn-gold btn-sm" data-testid="projects-admin-new-button"><lucide-icon [img]="i.Plus" [size]="16" /> Registra nuovo progetto</a>
      }
    </app-page-header>

    <section class="section-tight">
      <div class="container list">
        @if (projects() === undefined) {
          <div class="skeleton" style="height: 420px"></div>
        }
        @for (p of projects(); track p.id; let idx = $index) {
          <article class="proj" [class.flip]="idx % 2 === 1" appReveal [attr.data-testid]="'project-row-' + p.slug">
            <a [routerLink]="['/progetti', p.slug]" class="img-frame media"><img [src]="p.image_url | mediaUrl" [alt]="p.title" loading="lazy" /></a>
            <div class="copy">
              <span class="num mono">0{{ idx + 1 }}</span>
              <div class="row"><span class="badge">{{ p.category }}</span>@if (p.year_label) { <span class="badge badge-muted">{{ p.year_label }}</span> }</div>
              <h2 class="h2 mt-2">{{ p.title }}</h2>
              <p class="gold-sub mt-1">{{ p.subtitle }}</p>
              <p class="muted mt-2">{{ p.summary }}</p>
              @if (p.highlights.length) {
                <ul class="hl mt-3">
                  @for (h of p.highlights.slice(0, 4); track h) { <li><lucide-icon [img]="i.CircleCheck" [size]="16" /> {{ h }}</li> }
                </ul>
              }
              <a [routerLink]="['/progetti', p.slug]" class="link-gold mt-3" [attr.data-testid]="'project-link-' + p.slug">Scopri il progetto <lucide-icon [img]="i.ArrowRight" [size]="16" /></a>
            </div>
          </article>
        } @empty {
          @if (projects() !== undefined) { <div class="empty">Nessun progetto pubblicato.</div> }
        }
      </div>
    </section>
  `,
  styles: `
    .list { display: flex; flex-direction: column; gap: 96px; }
    .proj { display: grid; gap: 40px; align-items: center; }
    @media (min-width: 1024px) { .proj { grid-template-columns: 1.1fr 1fr; gap: 72px; } .proj.flip .media { order: 2; } }
    .media { aspect-ratio: 4/3; }
    .copy { position: relative; }
    .num { position: absolute; top: -40px; right: 0; font-size: 4.5rem; color: rgba(212,160,60,.12); line-height: 1; }
    .gold-sub { color: var(--gold-light); font-family: var(--font-display); font-style: italic; font-size: 1.3rem; }
    .hl { list-style: none; padding: 0; margin: 0; display: grid; gap: 10px; }
    .hl li { display: flex; gap: 10px; align-items: center; color: var(--text-2); font-size: .95rem; }
    .hl lucide-icon { color: var(--gold); }
  `,
})
export default class ProjectsListPage {
  private api = inject(PublicService);
  protected auth = inject(AuthService);
  protected readonly i = Icons;
  protected projects = toSignal(this.api.projects().pipe(catchError(() => of([]))));
}
