import { Component, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { LucideAngularModule } from 'lucide-angular';
import { SITE } from '../../core/config';
import { PageHeaderComponent } from '../../shared/components/page-header/page-header.component';
import { RevealDirective } from '../../shared/directives/reveal.directive';
import { Icons } from '../../shared/icons';

@Component({
  selector: 'app-five-per-mille-page',
  imports: [RouterLink, LucideAngularModule, PageHeaderComponent, RevealDirective],
  template: `
    <app-page-header overline="Sostienici" title="Il tuo 5x1000 a" accent="Giguiya" image="/images/mali-timbuktu.jpg"
      lead="Destinare il 5x1000 non ti costa nulla: è una quota delle imposte che lo Stato riserva agli enti del terzo settore. Con la tua firma sostieni integrazione, solidarietà e progetti di cooperazione tra Italia e Mali." />

    <section class="section-tight">
      <div class="container split">
        <div class="stack" style="gap: 20px">
          @for (s of steps; track s.title; let idx = $index) {
            <div class="step card" appReveal [revealDelay]="idx * 100">
              <span class="n mono">0{{ idx + 1 }}</span>
              <div><h3 class="h3">{{ s.title }}</h3><p class="muted mt-1">{{ s.text }}</p></div>
            </div>
          }
        </div>
        <aside class="cf-card card" appReveal [revealDelay]="200">
          <div class="halo"></div>
          <div class="rel">
            <span class="overline">Codice fiscale</span>
            <p class="code mono mt-3" data-testid="five-per-mille-fiscal-code">{{ site.fiscalCode }}</p>
            <button class="btn btn-gold btn-block mt-4" (click)="copy()" data-testid="five-per-mille-copy-button">
              <lucide-icon [img]="copied() ? i.Check : i.Copy" [size]="16" /> {{ copied() ? 'Copiato!' : 'Copia codice fiscale' }}
            </button>
            <p class="dim mt-3 small">Valido per modello 730, Redditi PF e CU. Puoi indicarlo anche al tuo CAF o commercialista.</p>
          </div>
        </aside>
      </div>
    </section>

    <section class="section">
      <div class="container">
        <span class="overline">Cosa sostieni</span>
        <div class="grid grid-3 mt-4">
          @for (w of where; track w.title; let idx = $index) {
            <div class="card card-hover" appReveal [revealDelay]="idx * 100">
              <lucide-icon [img]="w.icon" [size]="26" style="color: var(--gold)" />
              <h3 class="h3 mt-3">{{ w.title }}</h3>
              <p class="muted mt-2">{{ w.text }}</p>
            </div>
          }
        </div>
        <a routerLink="/progetti" class="link-gold mt-4" data-testid="five-per-mille-projects-link">Scopri i nostri progetti <lucide-icon [img]="i.ArrowRight" [size]="16" /></a>
      </div>
    </section>
  `,
  styles: `
    .step { display: flex; gap: 24px; align-items: flex-start; padding: 28px; }
    .n { font-size: 1.8rem; color: var(--gold); line-height: 1; }
    .cf-card { overflow: hidden; }
    .rel { position: relative; }
    .code { font-size: clamp(1.4rem, 3vw, 2rem); color: var(--gold-light); letter-spacing: .08em; word-break: break-all; }
    .small { font-size: .82rem; }
  `,
})
export default class FivePerMillePage {
  protected readonly i = Icons;
  protected readonly site = SITE;
  protected copied = signal(false);
  protected readonly steps = [
    { title: 'Compila la dichiarazione', text: 'Nel modello 730, Redditi o CU trova il riquadro dedicato alla scelta del 5x1000.' },
    { title: 'Firma nel riquadro', text: 'Firma nella sezione "Sostegno degli enti del terzo settore".' },
    { title: 'Inserisci il codice fiscale', text: 'Scrivi il codice fiscale dell\u2019Associazione Giguiya sotto la tua firma.' },
  ];
  protected readonly where = [
    { icon: Icons.HeartHandshake, title: 'Integrazione', text: 'Accoglienza, ascolto e accompagnamento dei nuovi arrivati, insieme ai maliani che vivono da tempo in Italia.' },
    { icon: Icons.Globe, title: 'Cooperazione in Mali', text: 'Progetti di cooperazione tra Italia e Mali per creare opportunità di lavoro per i giovani.' },
    { icon: Icons.Users, title: 'Giovani e fragili', text: 'Attenzione a bambini, adolescenti, giovani e anziani, con sport, cultura e servizi sociali.' },
  ];

  copy(): void {
    navigator.clipboard?.writeText(this.site.fiscalCode).then(() => {
      this.copied.set(true);
      setTimeout(() => this.copied.set(false), 2000);
    });
  }
}
