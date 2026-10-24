export interface MemberRegistration {
  first_name: string;
  last_name: string;
  email: string;
  phone: string | null;
  birth_date: string | null;
  birth_place: string | null;
  fiscal_code: string | null;
  address: string | null;
  city: string | null;
  privacy_accepted: boolean;
}

export interface Fee {
  year: number;
  amount: number;
  paid_at: string;
}

export interface Member {
  id: string;
  user_id: string;
  email: string;
  first_name: string;
  last_name: string;
  phone: string | null;
  membership_number: string;
  birth_date: string | null;
  birth_place: string | null;
  fiscal_code: string | null;
  address: string | null;
  city: string | null;
  enrollment_paid: boolean;
  enrollment_paid_at: string | null;
  card_issued: boolean;
  card_issued_at: string | null;
  notes: string | null;
  created_at: string;
  account_active: boolean;
  fees: Fee[];
  current_year: number;
  current_year_paid: boolean;
  in_good_standing: boolean;
  enrollment_fee: string;
  annual_fee: string;
}

export interface MemberBooking {
  id: string;
  event_title: string;
  event_slug: string;
  event_start: string;
  created_at: string;
}

export interface MemberDashboard {
  member: Member;
  bookings: MemberBooking[];
}

export interface MemberUpdate {
  enrollment_paid?: boolean;
  card_issued?: boolean;
  notes?: string | null;
  phone?: string | null;
  address?: string | null;
  city?: string | null;
}
