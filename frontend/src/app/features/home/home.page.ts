import { Component, inject } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { RouterLink } from '@angular/router';
import { LucideAngularModule } from 'lucide-angular';
import { catchError, map, of } from 'rxjs';
import { SITE } from '../../core/config';
import { PublicService } from '../../core/services/public.service';
import { EventCardComponent } from '../../shared/components/event-card/event-card.component';
import { RevealDirective } from '../../shared/directives/reveal.directive';
import { Icons } from '../../shared/icons';
import { ItDatePipe } from '../../shared/pipes/it-date.pipe';

@Component({
  selector: 'app-home-page',
  imports: [RouterLink, LucideAngularModule, EventCardComponent, RevealDirective, ItDatePipe],
  templateUrl: './home.page.html',
  styleUrl: './home.page.scss',
})
export default class HomePage {
  private api = inject(PublicService);
  protected readonly i = Icons;
  protected readonly site = SITE;
  protected events = toSignal(this.api.events('upcoming').pipe(map((e) => e.slice(0, 3)), catchError(() => of([]))));
  protected projects = toSignal(this.api.projects().pipe(catchError(() => of([]))));
  protected readonly marquee = ['Cultura', 'Sport', 'Inclusione', 'Comunità', 'Musica', 'Cucina maliana', 'Treccine', 'Cittadinanza'];
  protected readonly pillars = [
    { icon: Icons.HeartHandshake, title: 'Comunità', text: 'Uno spazio di riferimento per la comunità maliana di Torino, dove sentirsi a casa e crescere insieme.' },
    { icon: Icons.Sparkles, title: 'Cultura', text: 'Laboratori, musica, cucina e tradizioni del Mali condivisi con tutta la cittadinanza.' },
    { icon: Icons.Landmark, title: 'Inclusione', text: 'Ascolto, orientamento e accompagnamento nei percorsi di inclusione e cittadinanza.' },
  ];
}
