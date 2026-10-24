import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { API_URL } from '../config';
import { BookingCreated, BookingInput, EventItem } from '../models/event.model';
import { Project } from '../models/project.model';

@Injectable({ providedIn: 'root' })
export class PublicService {
  private http = inject(HttpClient);

  events(scope: 'upcoming' | 'past' | 'all' = 'upcoming') {
    return this.http.get<EventItem[]>(`${API_URL}/events`, { params: new HttpParams().set('scope', scope) });
  }

  event(slug: string) {
    return this.http.get<EventItem>(`${API_URL}/events/${slug}`);
  }

  book(slug: string, data: BookingInput) {
    return this.http.post<BookingCreated>(`${API_URL}/events/${slug}/bookings`, data);
  }

  projects() {
    return this.http.get<Project[]>(`${API_URL}/projects`);
  }

  project(slug: string) {
    return this.http.get<Project>(`${API_URL}/projects/${slug}`);
  }
}
