import { Component, inject } from '@angular/core';
import { NavigationEnd, Router, RouterOutlet } from '@angular/router';
import { toSignal } from '@angular/core/rxjs-interop';
import { filter, map } from 'rxjs';
import { NavbarComponent } from './shared/components/navbar/navbar.component';
import { FooterComponent } from './shared/components/footer/footer.component';
import { ToastContainerComponent } from './shared/components/toast/toast-container.component';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, NavbarComponent, FooterComponent, ToastContainerComponent],
  template: `
    <app-navbar />
    <main data-testid="app-main">
      <router-outlet />
    </main>
    @if (!isAdmin()) {
      <app-footer />
    }
    <app-toast-container />
  `,
})
export class App {
  private router = inject(Router);
  protected isAdmin = toSignal(
    this.router.events.pipe(
      filter((e) => e instanceof NavigationEnd),
      map((e) => (e as NavigationEnd).urlAfterRedirects.startsWith('/admin')),
    ),
    { initialValue: false },
  );
}
