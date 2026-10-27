export interface ProjectInput {
  title: string;
  subtitle: string;
  category: string;
  summary: string;
  description: string;
  image_url: string | null;
  gallery: string[];
  partners: string;
  year_label: string;
  highlights: string[];
  is_published: boolean;
  sort_order: number;
}

export interface Project extends ProjectInput {
  id: string;
  slug: string;
  created_at: string;
}
