import { Component, inject } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { RouterLink } from '@angular/router';
import { LucideAngularModule } from 'lucide-angular';
import { catchError, map, of } from 'rxjs';
import { SITE } from '../../core/config';
import { AIMS, MALI_PLACES } from '../../core/content/association.content';
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
  protected readonly places = MALI_PLACES;
  protected readonly marquee = ['Solidarietà', 'Integrazione', 'Cooperazione Italia – Mali', 'Cultura', 'Giovani', 'Sport', 'Inclusione', 'Cittadinanza'];
  protected readonly pillars = AIMS.slice(1, 5).map((a, idx) => ({ ...a, icon: [Icons.HeartHandshake, Icons.Users, Icons.Globe, Icons.Landmark][idx] }));
}
