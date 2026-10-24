import { HttpErrorResponse, HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { catchError, switchMap, throwError } from 'rxjs';
import { API_URL } from '../config';
import { AuthService } from '../services/auth.service';

const SKIP_REFRESH = ['/auth/login', '/auth/refresh', '/auth/me', '/auth/logout'];
const HTTP_UNAUTHORIZED = 401;

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  if (!req.url.startsWith(API_URL)) return next(req);
  const auth = inject(AuthService);
  const request = req.clone({ withCredentials: true });
  return next(request).pipe(
    catchError((err: HttpErrorResponse) => {
      if (err.status !== HTTP_UNAUTHORIZED || SKIP_REFRESH.some((p) => req.url.includes(p)) || !auth.user()) {
        return throwError(() => err);
      }
      return auth.refresh().pipe(
        switchMap(() => next(request)),
        catchError((refreshErr) => {
          auth.clear();
          return throwError(() => refreshErr);
        }),
      );
    }),
  );
};
