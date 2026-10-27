import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { API_URL } from '../config';
import { AdminStats, Contact, StaffMember } from '../models/admin.model';
import { Booking, EventInput, EventItem } from '../models/event.model';
import { Member, MemberUpdate } from '../models/member.model';
import { Project, ProjectInput } from '../models/project.model';
import { MessageResponse } from '../models/user.model';

@Injectable({ providedIn: 'root' })
export class AdminService {
  private http = inject(HttpClient);
  private readonly base = `${API_URL}/admin`;

  stats() {
    return this.http.get<AdminStats>(`${this.base}/stats`);
  }

  members(q = '', status = 'all') {
    return this.http.get<Member[]>(`${this.base}/members`, { params: new HttpParams().set('q', q).set('status', status) });
  }

  updateMember(id: string, data: MemberUpdate) {
    return this.http.patch<Member>(`${this.base}/members/${id}`, data);
  }

  setFee(id: string, year: number, paid: boolean) {
    return this.http.put<Member>(`${this.base}/members/${id}/fees/${year}`, { paid });
  }

  resendInvite(id: string) {
    return this.http.post<MessageResponse>(`${this.base}/members/${id}/resend-invite`, {});
  }

  deleteMember(id: string) {
    return this.http.delete<MessageResponse>(`${this.base}/members/${id}`);
  }

  contacts(q = '') {
    return this.http.get<Contact[]>(`${this.base}/contacts`, { params: new HttpParams().set('q', q) });
  }

  events() {
    return this.http.get<EventItem[]>(`${this.base}/events`);
  }

  saveEvent(data: EventInput, id?: string) {
    return id
      ? this.http.put<EventItem>(`${this.base}/events/${id}`, data)
      : this.http.post<EventItem>(`${this.base}/events`, data);
  }

  deleteEvent(id: string) {
    return this.http.delete<MessageResponse>(`${this.base}/events/${id}`);
  }

  eventBookings(id: string) {
    return this.http.get<Booking[]>(`${this.base}/events/${id}/bookings`);
  }

  deleteBooking(id: string) {
    return this.http.delete<MessageResponse>(`${this.base}/bookings/${id}`);
  }

  projects() {
    return this.http.get<Project[]>(`${this.base}/projects`);
  }

  saveProject(data: ProjectInput, id?: string) {
    return id
      ? this.http.put<Project>(`${this.base}/projects/${id}`, data)
      : this.http.post<Project>(`${this.base}/projects`, data);
  }

  deleteProject(id: string) {
    return this.http.delete<MessageResponse>(`${this.base}/projects/${id}`);
  }

  uploadImage(file: File) {
    const body = new FormData();
    body.append('file', file);
    return this.http.post<{ url: string; path: string }>(`${this.base}/uploads`, body);
  }

  staff() {
    return this.http.get<StaffMember[]>(`${this.base}/staff`);
  }

  staffAction(id: string, action: 'approve' | 'revoke') {
    return this.http.post<MessageResponse>(`${this.base}/staff/${id}/${action}`, {});
  }

  deleteStaff(id: string) {
    return this.http.delete<MessageResponse>(`${this.base}/staff/${id}`);
  }
}
