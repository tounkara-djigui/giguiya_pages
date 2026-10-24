export type Role = 'admin' | 'member';

export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  phone?: string | null;
  role: Role;
}

export interface MessageResponse {
  message: string;
  email_sent?: boolean | null;
}
