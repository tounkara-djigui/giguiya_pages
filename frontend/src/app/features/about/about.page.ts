import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';
import { LucideAngularModule } from 'lucide-angular';
import { SITE } from '../../core/config';
import { PageHeaderComponent } from '../../shared/components/page-header/page-header.component';
import { RevealDirective } from '../../shared/directives/reveal.directive';
import { Icons } from '../../shared/icons';

@Component({
  selector: 'app-about-page',
  imports: [RouterLink, LucideAngularModule, PageHeaderComponent, RevealDirective],
  template: `
    <app-page-header overline="Chi siamo" title="La comunità maliana," accent="nel cuore di Torino."
      lead="Giguiya è un'associazione che riunisce la comunità maliana di Torino e la apre alla città: cultura, sport, ascolto e partecipazione." />

    <section class="section">
      <div class="container split reverse">
        <div class="img-frame tall" appReveal><img src="/images/community.jpg" alt="Comunità Giguiya" loading="lazy" /></div>
        <div appReveal [revealDelay]="150">
          <span class="overline">La nostra missione</span>
          <h2 class="h2 mt-2">Valorizzare le radici, <span class="gold-text">costruire cittadinanza.</span></h2>
          <p class="lead mt-3">
            Lavoriamo per creare occasioni di incontro tra culture, sostenere i percorsi di inclusione della comunità
            maliana e promuovere lo sport e la cultura come strumenti di partecipazione.
          </p>
          <div class="vals mt-4">
            @for (v of values; track v.title) {
              <div class="val"><lucide-icon [img]="v.icon" [size]="22" /><div><h4>{{ v.title }}</h4><p class="muted">{{ v.text }}</p></div></div>
            }
          </div>
        </div>
      </div>
    </section>

    <section class="section partners-sec">
      <div class="container">
        <span class="overline">Hanno collaborato con noi</span>
        <div class="partners mt-4" appReveal>
          <span>Città di Torino</span><i>✦</i><span>INTERSOS</span><i>✦</i><span>UNHCR</span>
        </div>
      </div>
    </section>

    <section class="section">
      <div class="container split">
        <div appReveal>
          <span class="overline">Statuto</span>
          <h2 class="h2 mt-2">Lo statuto <span class="gold-text">dell'associazione</span></h2>
          <p class="lead mt-3">Lo statuto definisce finalità, organi e regole di funzionamento dell'Associazione Giguiya.</p>
          <div class="statuto card mt-4" data-testid="about-statuto-placeholder">
            <lucide-icon [img]="i.FileText" [size]="28" />
            <div>
              <h4>[STATUTO DA FORNIRE]</h4>
              <p class="muted">Il testo completo dello statuto sarà pubblicato a breve in questa sezione.</p>
            </div>
          </div>
        </div>
        <aside class="card" appReveal [revealDelay]="150">
          <span class="overline">Contatti</span>
          <div class="stack mt-3">
            <span class="info-row"><lucide-icon [img]="i.MapPin" [size]="18" /> {{ site.address }}</span>
            <span class="info-row"><lucide-icon [img]="i.Mail" [size]="18" /> {{ site.email }}</span>
            <span class="info-row"><lucide-icon [img]="i.Phone" [size]="18" /> {{ site.phone }}</span>
          </div>
          <hr class="divider mt-4" />
          <a routerLink="/diventa-socio" class="btn btn-gold btn-block mt-4" data-testid="about-diventa-socio-button">Diventa socio</a>
        </aside>
      </div>
    </section>
  `,
  styles: `
    .tall { aspect-ratio: 4/5; }
    .vals { display: grid; gap: 22px; }
    .val { display: flex; gap: 16px; }
    .val lucide-icon { color: var(--gold); margin-top: 4px; flex-shrink: 0; }
    .val h4 { font-size: 1.45rem; }
    .partners-sec { background: #0f1014; border-block: 1px solid var(--gold-border); }
    .partners { display: flex; flex-wrap: wrap; gap: 28px 40px; align-items: center; }
    .partners span { font-family: var(--font-display); font-size: clamp(2rem, 4vw, 3.4rem); color: var(--text); }
    .partners i { color: var(--gold); font-style: normal; }
    .statuto { display: flex; gap: 20px; align-items: flex-start; border-style: dashed; }
    .statuto lucide-icon { color: var(--gold); }
    .statuto h4 { font-size: 1.4rem; }
  `,
})
export default class AboutPage {
  protected readonly i = Icons;
  protected readonly site = SITE;
  protected readonly values = [
    { icon: Icons.HeartHandshake, title: 'Accoglienza', text: 'Uno spazio aperto in cui ogni persona si sente parte di una comunità.' },
    { icon: Icons.Globe, title: 'Intercultura', text: 'La cultura maliana come ricchezza da condividere con tutta la città.' },
    { icon: Icons.Trophy, title: 'Sport', text: 'Disciplina, squadra e rispetto: valori che portiamo in campo ogni settimana.' },
    { icon: Icons.Landmark, title: 'Cittadinanza', text: 'Accompagnare le persone nei percorsi di inclusione e partecipazione attiva.' },
  ];
}
