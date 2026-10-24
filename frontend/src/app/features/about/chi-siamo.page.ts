import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';
import { LucideAngularModule } from 'lucide-angular';
import { SITE } from '../../core/config';
import { ACTIVITIES, AIMS, ORGANS, STATUTE } from '../../core/content/association.content';
import { PageHeaderComponent } from '../../shared/components/page-header/page-header.component';
import { RevealDirective } from '../../shared/directives/reveal.directive';
import { Icons } from '../../shared/icons';

@Component({
  selector: 'app-chi-siamo-page',
  imports: [RouterLink, LucideAngularModule, PageHeaderComponent, RevealDirective],
  templateUrl: './chi-siamo.page.html',
  styleUrl: './chi-siamo.page.scss',
})
export default class ChiSiamoPage {
  protected readonly i = Icons;
  protected readonly site = SITE;
  protected readonly statute = STATUTE;
  protected readonly aims = AIMS;
  protected readonly activities = ACTIVITIES;
  protected readonly organs = ORGANS;
}
