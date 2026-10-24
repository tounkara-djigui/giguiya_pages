import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-not-found-page',
  imports: [RouterLink],
  template: `
    <section class="section page-top" style="min-height: 80vh">
      <div class="container center">
        <span class="overline">Errore 404</span>
        <h1 class="display mt-2" data-testid="not-found-title">Pagina <span class="gold-text">non trovata</span></h1>
        <p class="lead mt-3" style="margin-inline: auto">La pagina che cerchi non esiste o è stata spostata.</p>
        <a routerLink="/" class="btn btn-gold mt-4" data-testid="not-found-home-button">Torna alla home</a>
      </div>
    </section>
  `,
})
export default class NotFoundPage {}
