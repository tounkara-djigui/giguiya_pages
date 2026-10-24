import { Routes } from '@angular/router';
import { adminGuard, memberGuard } from './core/guards/role.guard';

export const routes: Routes = [
  { path: '', loadComponent: () => import('./features/home/home.page'), title: 'Giguiya · Associazione della comunità maliana a Torino' },
  { path: 'eventi', loadComponent: () => import('./features/events/events-list.page'), title: 'Eventi · Giguiya' },
  { path: 'eventi/:slug', loadComponent: () => import('./features/events/event-detail.page'), title: 'Evento · Giguiya' },
  { path: 'progetti', loadComponent: () => import('./features/projects/projects-list.page'), title: 'Progetti · Giguiya' },
  { path: 'progetti/:slug', loadComponent: () => import('./features/projects/project-detail.page'), title: 'Progetto · Giguiya' },
  { path: 'chi-siamo', loadComponent: () => import('./features/about/about.page'), title: 'Chi siamo · Giguiya' },
  { path: '5x1000', loadComponent: () => import('./features/five-per-mille/five-per-mille.page'), title: '5x1000 · Giguiya' },
  { path: 'diventa-socio', loadComponent: () => import('./features/membership/become-member.page'), title: 'Diventa socio · Giguiya' },
  {
    path: 'accesso',
    children: [
      { path: '', loadComponent: () => import('./features/auth/login.page'), title: 'Accesso · Giguiya' },
      { path: 'registrazione-admin', loadComponent: () => import('./features/auth/admin-register.page'), title: 'Registrazione amministratore · Giguiya' },
      { path: 'verifica-email', loadComponent: () => import('./features/auth/verify-email.page'), title: 'Verifica email · Giguiya' },
      { path: 'imposta-password', loadComponent: () => import('./features/auth/set-password.page'), title: 'Imposta password · Giguiya' },
      { path: 'password-dimenticata', loadComponent: () => import('./features/auth/forgot-password.page'), title: 'Password dimenticata · Giguiya' },
    ],
  },
  { path: 'area-socio', canActivate: [memberGuard], loadComponent: () => import('./features/member/member-dashboard.page'), title: 'Area socio · Giguiya' },
  {
    path: 'admin',
    canActivate: [adminGuard],
    loadComponent: () => import('./features/admin/admin-layout.component'),
    children: [
      { path: '', loadComponent: () => import('./features/admin/dashboard/admin-dashboard.page'), title: 'Dashboard · Admin Giguiya' },
      { path: 'soci', loadComponent: () => import('./features/admin/members/admin-members.page'), title: 'Soci · Admin Giguiya' },
      { path: 'interessati', loadComponent: () => import('./features/admin/contacts/admin-contacts.page'), title: 'Interessati · Admin Giguiya' },
      { path: 'eventi', loadComponent: () => import('./features/admin/events/admin-events.page'), title: 'Eventi · Admin Giguiya' },
      { path: 'progetti', loadComponent: () => import('./features/admin/projects/admin-projects.page'), title: 'Progetti · Admin Giguiya' },
    ],
  },
  { path: '**', loadComponent: () => import('./features/not-found/not-found.page'), title: 'Pagina non trovata · Giguiya' },
];
