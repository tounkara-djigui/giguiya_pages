export interface AdminStats {
  members_total: number;
  members_in_good_standing: number;
  members_pending_card: number;
  members_pending_enrollment: number;
  bookings_total: number;
  contacts_total: number;
  upcoming_events: number;
  projects_total: number;
  current_year: number;
}

export interface StaffMember {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  email_verified: boolean;
  admin_status: 'pending' | 'approved';
  created_at: string;
}

export interface Contact {
  email: string;
  first_name: string;
  last_name: string;
  phone: string | null;
  bookings_count: number;
  last_booking_at: string;
  events: string[];
  is_member: boolean;
}
