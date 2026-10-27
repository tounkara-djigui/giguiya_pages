export type Role = 'admin' | 'member' | 'pending';

export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  phone?: string | null;
  role: Role;
  is_super_admin?: boolean;
}

export interface MessageResponse {
  message: string;
  email_sent?: boolean | null;
}
