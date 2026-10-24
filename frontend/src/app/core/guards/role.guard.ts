import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { Role } from '../models/user.model';
import { AuthService } from '../services/auth.service';

const roleGuard = (role: Role): CanActivateFn => (_route, state) => {
  const auth = inject(AuthService);
  const router = inject(Router);
  const user = auth.user();
  if (user?.role === role) return true;
  return router.createUrlTree(['/accesso'], { queryParams: { redirect: state.url } });
};

export const adminGuard = roleGuard('admin');
export const memberGuard = roleGuard('member');
