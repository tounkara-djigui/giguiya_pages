import { Component, HostListener, inject, signal } from '@angular/core';
import { NavigationEnd, Router, RouterLink, RouterLinkActive } from '@angular/router';
import { LucideAngularModule } from 'lucide-angular';
import { filter } from 'rxjs';
import { AuthService } from '../../../core/services/auth.service';
import { Icons } from '../../icons';
import { LogoComponent } from '../logo/logo.component';

@Component({
  selector: 'app-navbar',
  imports: [RouterLink, RouterLinkActive, LucideAngularModule, LogoComponent],
  templateUrl: './navbar.component.html',
  styleUrl: './navbar.component.scss',
})
export class NavbarComponent {
  protected auth = inject(AuthService);
  private router = inject(Router);
  protected readonly i = Icons;
  protected readonly links = [
    { label: 'Home', path: '/', exact: true, id: 'home' },
    { label: 'Eventi', path: '/eventi', exact: false, id: 'eventi' },
    { label: 'Progetti', path: '/progetti', exact: false, id: 'progetti' },
    { label: 'Chi siamo', path: '/chi-siamo', exact: false, id: 'chi-siamo' },
    { label: '5x1000', path: '/5x1000', exact: false, id: '5x1000' },
  ];
  protected scrolled = signal(false);
  protected mobileOpen = signal(false);
  protected accessOpen = signal(false);

  constructor() {
    this.router.events.pipe(filter((e) => e instanceof NavigationEnd)).subscribe(() => {
      this.mobileOpen.set(false);
      this.accessOpen.set(false);
    });
  }

  @HostListener('window:scroll')
  onScroll(): void {
    this.scrolled.set(window.scrollY > 24);
  }

  @HostListener('document:click', ['$event'])
  onDocClick(e: MouseEvent): void {
    if (!(e.target as HTMLElement).closest('.access')) this.accessOpen.set(false);
  }
}
