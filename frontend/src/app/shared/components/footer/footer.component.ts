import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';
import { LucideAngularModule } from 'lucide-angular';
import { SITE } from '../../../core/config';
import { PHOTO_CREDITS } from '../../../core/content/association.content';
import { Icons } from '../../icons';
import { LogoComponent } from '../logo/logo.component';

@Component({
  selector: 'app-footer',
  imports: [RouterLink, LucideAngularModule, LogoComponent],
  template: `
    <footer class="footer" data-testid="footer">
      <div class="container">
        <div class="cta-strip">
          <h3 class="h2">Insieme, <span class="gold-text">intrecciamo comunità.</span></h3>
          <div class="row">
            <a routerLink="/diventa-socio" class="btn btn-gold" data-testid="footer-diventa-socio-button">Diventa socio <lucide-icon [img]="i.ArrowRight" [size]="16" /></a>
            <a routerLink="/5x1000" class="btn btn-ghost" data-testid="footer-5x1000-button">Dona il 5x1000</a>
          </div>
        </div>
        <hr class="divider" />
        <div class="cols">
          <div class="stack">
            <app-logo />
            <p class="muted small">{{ site.fullName }} – {{ site.acronym }}. Associazione di Promozione Sociale: solidarietà, integrazione, cooperazione tra Italia e Mali.</p>
          </div>
          <div class="stack">
            <span class="label">Esplora</span>
            <a routerLink="/eventi" class="f-link" data-testid="footer-eventi-link">Eventi</a>
            <a routerLink="/progetti" class="f-link" data-testid="footer-progetti-link">Progetti</a>
            <a routerLink="/chi-siamo" class="f-link" data-testid="footer-chi-siamo-link">Chi siamo</a>
            <a routerLink="/5x1000" class="f-link" data-testid="footer-5x1000-link">5x1000</a>
          </div>
          <div class="stack">
            <span class="label">Accesso</span>
            <a routerLink="/accesso" class="f-link" data-testid="footer-login-link">Login</a>
            <a routerLink="/diventa-socio" class="f-link" data-testid="footer-registrazione-link">Registrazione socio</a>
            <a routerLink="/accesso/registrazione-admin" class="f-link" data-testid="footer-admin-register-link">Area staff</a>
          </div>
          <div class="stack">
            <span class="label">Contatti</span>
            <a class="info-row f-link" href="https://maps.google.com/?q=Corso+Casale+97+Torino" target="_blank" rel="noopener" data-testid="footer-address"><lucide-icon [img]="i.MapPin" [size]="16" /> {{ site.address }}</a>
            <a class="info-row f-link" [href]="'mailto:' + site.email" data-testid="footer-email"><lucide-icon [img]="i.Mail" [size]="16" /> {{ site.email }}</a>
            <a class="info-row f-link" [href]="'tel:' + site.phoneHref" data-testid="footer-phone"><lucide-icon [img]="i.Phone" [size]="16" /> {{ site.phone }}</a>
          </div>
        </div>
        <div class="bottom">
          <span>© {{ year }} {{ site.acronym }} APS · C.F. {{ site.fiscalCode }}</span>
          <a href="https://commons.wikimedia.org" target="_blank" rel="noopener" class="credits" data-testid="footer-photo-credits">{{ credits }}</a>
          <span class="mono">Torino · Mali</span>
        </div>
      </div>
    </footer>
  `,
  styles: `
    .footer { border-top: 1px solid var(--gold-border); background: #0a0b0d; padding: 96px 0 40px; position: relative; overflow: hidden; }
    .footer::before { content: ''; position: absolute; inset: 0; background: var(--gold-halo); opacity: .6; pointer-events: none; }
    .cta-strip { display: flex; flex-direction: column; gap: 28px; justify-content: space-between; padding-bottom: 64px; position: relative; }
    @media (min-width: 1024px) { .cta-strip { flex-direction: row; align-items: flex-end; } }
    .cols { display: grid; gap: 40px; grid-template-columns: 1fr; padding: 64px 0; position: relative; }
    @media (min-width: 768px) { .cols { grid-template-columns: 2fr 1fr 1fr 1.6fr; } }
    .small { font-size: .9rem; max-width: 34ch; }
    .f-link { color: var(--text-2); font-size: .95rem; transition: color .2s ease; width: fit-content; }
    .f-link:hover { color: var(--gold-light); }
    .credits { color: var(--text-3); }
    .credits:hover { color: var(--gold-light); }
    .bottom { display: flex; justify-content: space-between; flex-wrap: wrap; gap: 12px; font-size: .8rem; color: var(--text-3); border-top: 1px solid rgba(255,255,255,.05); padding-top: 28px; position: relative; }
  `,
})
export class FooterComponent {
  protected readonly i = Icons;
  protected readonly site = SITE;
  protected readonly credits = PHOTO_CREDITS;
  protected readonly year = new Date().getFullYear();
}
