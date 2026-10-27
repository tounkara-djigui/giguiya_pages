import { HttpClient } from '@angular/common/http';
import { Injectable, computed, inject, signal } from '@angular/core';
import { Router } from '@angular/router';
import { Observable, catchError, firstValueFrom, of, tap } from 'rxjs';
import { API_URL } from '../config';
import { MessageResponse, User } from '../models/user.model';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private http = inject(HttpClient);
  private router = inject(Router);
  private readonly base = `${API_URL}/auth`;

  readonly user = signal<User | null>(null);
  readonly isAdmin = computed(() => this.user()?.role === 'admin');
  readonly isMember = computed(() => this.user()?.role === 'member');

  init(): Promise<unknown> {
    return firstValueFrom(
      this.http.get<User>(`${this.base}/me`).pipe(
        catchError(() => this.http.post<User>(`${this.base}/refresh`, {}).pipe(catchError(() => of(null)))),
        tap((u) => this.user.set(u)),
      ),
    );
  }

  login(email: string, password: string): Observable<User> {
    return this.http.post<User>(`${this.base}/login`, { email, password }).pipe(tap((u) => this.user.set(u)));
  }

  refresh(): Observable<User> {
    return this.http.post<User>(`${this.base}/refresh`, {}).pipe(tap((u) => this.user.set(u)));
  }

  logout(): void {
    this.http.post(`${this.base}/logout`, {}).pipe(catchError(() => of(null))).subscribe(() => {
      this.clear();
      this.router.navigateByUrl('/');
    });
  }

  clear(): void {
    this.user.set(null);
  }

  registerAdmin(data: { first_name: string; last_name: string; email: string; password: string }) {
    return this.http.post<MessageResponse>(`${this.base}/admin/register`, data);
  }

  verifyEmail(token: string) {
    return this.http.post<MessageResponse>(`${this.base}/verify-email`, { token });
  }

  setPassword(token: string, password: string) {
    return this.http.post<MessageResponse>(`${this.base}/set-password`, { token, password });
  }

  forgotPassword(email: string) {
    return this.http.post<MessageResponse>(`${this.base}/forgot-password`, { email });
  }

  changePassword(current_password: string, new_password: string) {
    return this.http.post<MessageResponse>(`${this.base}/change-password`, { current_password, new_password });
  }

  homeFor(user: User): string {
    return user.role === 'admin' ? '/admin' : user.role === 'member' ? '/area-socio' : '/';
  }
}
