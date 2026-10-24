import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { API_URL } from '../config';
import { MemberDashboard, MemberRegistration } from '../models/member.model';
import { MessageResponse } from '../models/user.model';

@Injectable({ providedIn: 'root' })
export class MemberService {
  private http = inject(HttpClient);

  register(data: MemberRegistration) {
    return this.http.post<MessageResponse>(`${API_URL}/members/register`, data);
  }

  dashboard() {
    return this.http.get<MemberDashboard>(`${API_URL}/members/me`);
  }
}
