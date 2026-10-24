export interface EventInput {
  title: string;
  summary: string;
  description: string;
  category: string;
  location: string;
  start_at: string;
  end_at: string | null;
  image_url: string | null;
  capacity: number | null;
  price_label: string | null;
  is_published: boolean;
}

export interface EventItem extends EventInput {
  id: string;
  slug: string;
  bookings_count: number;
  spots_left: number | null;
  start_local: string | null;
  end_local: string | null;
  is_past: boolean;
}

export interface BookingInput {
  first_name: string;
  last_name: string;
  email: string;
  phone: string | null;
}

export interface Booking extends BookingInput {
  id: string;
  event_id: string;
  event_title: string;
  created_at: string;
}

export interface BookingCreated {
  id: string;
  message: string;
  email_sent: boolean;
}

export const EVENT_CATEGORIES = ['Cultura', 'Laboratorio', 'Musica', 'Sport', 'Gita', 'Incontro', 'Formazione'];
