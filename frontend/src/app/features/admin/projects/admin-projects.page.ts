import { Component, OnInit, inject, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { LucideAngularModule } from 'lucide-angular';
import { Project } from '../../../core/models/project.model';
import { AdminService } from '../../../core/services/admin.service';
import { ToastService } from '../../../core/services/toast.service';
import { apiError } from '../../../core/utils/api.utils';
import { Icons } from '../../../shared/icons';
import { MediaUrlPipe } from '../../../shared/pipes/media-url.pipe';
import { ProjectFormComponent } from './project-form.component';

@Component({
  selector: 'app-admin-projects-page',
  imports: [RouterLink, LucideAngularModule, ProjectFormComponent, MediaUrlPipe],
  template: `
    <div class="row-between">
      <div>
        <span class="overline">Contenuti</span>
        <h1 class="admin-title mt-2">Progetti</h1>
        <p class="muted mt-1">Registra nuovi progetti e aggiorna quelli esistenti mostrati nella sezione Progetti del sito.</p>
      </div>
      <button class="btn btn-gold btn-sm" (click)="open(null)" data-testid="admin-new-project-button"><lucide-icon [img]="i.Plus" [size]="16" /> Nuovo progetto</button>
    </div>

    @if (projects(); as list) {
      <div class="grid grid-3 mt-4">
        @for (p of list; track p.id) {
          <div class="card pcard" [attr.data-testid]="'admin-project-card-' + p.slug">
            <div class="thumb"><img [src]="p.image_url | mediaUrl" [alt]="p.title" /></div>
            <div class="row mt-3">
              <span class="badge">{{ p.category }}</span>
              @if (!p.is_published) { <span class="badge badge-muted">Bozza</span> }
            </div>
            <h3 class="h3 mt-2">{{ p.title }}</h3>
            <p class="muted small mt-1">{{ p.subtitle }}</p>
            <div class="row mt-3">
              <button class="btn btn-ghost btn-sm" (click)="open(p)" [attr.data-testid]="'admin-project-edit-' + p.slug"><lucide-icon [img]="i.Pencil" [size]="14" /> Modifica</button>
              @if (p.is_published) {
                <a [routerLink]="['/progetti', p.slug]" target="_blank" class="btn btn-ghost btn-icon" title="Vedi sul sito"><lucide-icon [img]="i.ArrowUpRight" [size]="15" /></a>
              }
              @if (confirmId() === p.id) {
                <button class="btn btn-danger btn-sm" (click)="remove(p)" [attr.data-testid]="'admin-project-confirm-delete-' + p.slug">Conferma</button>
              } @else {
                <button class="btn btn-ghost btn-icon" (click)="confirmId.set(p.id)" title="Elimina" [attr.data-testid]="'admin-project-delete-' + p.slug"><lucide-icon [img]="i.Trash2" [size]="15" /></button>
              }
            </div>
          </div>
        } @empty {
          <div class="empty">Nessun progetto registrato.</div>
        }
      </div>
    } @else {
      <div class="skeleton mt-4" style="height: 300px"></div>
    }

    @if (formOpen()) {
      <app-project-form [project]="editing()" (closed)="formOpen.set(false)" (saved)="onSaved()" />
    }
  `,
  styles: `
    .pcard { padding: 20px; }
    .thumb { aspect-ratio: 16/9; border-radius: 12px; overflow: hidden; }
    .thumb img { width: 100%; height: 100%; object-fit: cover; }
    .small { font-size: .88rem; }
  `,
})
export default class AdminProjectsPage implements OnInit {
  private api = inject(AdminService);
  private toast = inject(ToastService);
  protected readonly i = Icons;
  protected projects = signal<Project[] | null>(null);
  protected formOpen = signal(false);
  protected editing = signal<Project | null>(null);
  protected confirmId = signal<string | null>(null);

  ngOnInit(): void {
    this.load();
  }

  load(): void {
    this.api.projects().subscribe({
      next: (p) => this.projects.set(p),
      error: (e) => this.toast.error(apiError(e)),
    });
  }

  open(p: Project | null): void {
    this.editing.set(p);
    this.formOpen.set(true);
  }

  onSaved(): void {
    this.formOpen.set(false);
    this.load();
  }

  remove(p: Project): void {
    this.api.deleteProject(p.id).subscribe({
      next: () => {
        this.toast.success('Progetto eliminato');
        this.confirmId.set(null);
        this.load();
      },
      error: (e) => this.toast.error(apiError(e)),
    });
  }
}
