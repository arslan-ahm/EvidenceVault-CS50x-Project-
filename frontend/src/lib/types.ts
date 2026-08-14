export type User = {
  id: string;
  email: string;
  name: string;
  occupation?: string | null;
  profile_image_url?: string | null;
  is_admin?: boolean;
  created_at: string;
};

export type UserUpdate = {
  name?: string;
  occupation?: string | null;
  profile_image_url?: string | null;
};

export type ForgotPasswordRequest = {
  email: string;
};

export type ResetPasswordRequest = {
  token: string;
  password: string;
};

export type ChangePasswordRequest = {
  current_password: string;
  new_password: string;
};

export type Case = {
  id: string;
  title: string;
  description?: string | null;
  organization_id?: string | null;
  organization_name?: string | null;
  category?: string;
  severity?: string;
  status?: string;
  is_public?: boolean;
  user_id: string;
  views_count?: number;
  upvotes_count?: number;
  created_at: string;
};

export type Comment = {
  id: string;
  case_id: string;
  user_id: string;
  body: string;
  author_name: string;
  created_at: string;
  updated_at?: string | null;
};

export type Organization = {
  id: string;
  name: string;
  slug: string;
  description?: string | null;
  website?: string | null;
  industry?: string | null;
  logo_url?: string | null;
  created_at: string;
};

export type AdminStats = {
  total_users: number;
  admin_users: number;
  banned_users: number;
  total_cases: number;
  public_cases: number;
  total_organizations: number;
  total_comments: number;
};

export type AdminUser = {
  id: string;
  email: string;
  name: string;
  is_admin: boolean;
  is_banned: boolean;
  case_count: number;
  created_at: string;
};

export type AdminCase = {
  id: string;
  title: string;
  owner_email: string;
  organization_name?: string | null;
  category: string;
  severity: string;
  status: string;
  is_public: boolean;
  views_count: number;
  upvotes_count: number;
  created_at: string;
};

export type AdminCountPoint = { key: string; label: string; count: number };
export type AdminDayPoint = { date: string; count: number };
export type AdminOrgCount = { name: string; count: number };

export type AdminAnalytics = {
  cases_by_category: AdminCountPoint[];
  cases_by_status: AdminCountPoint[];
  cases_by_severity: AdminCountPoint[];
  cases_per_day: AdminDayPoint[];
  signups_per_day: AdminDayPoint[];
  top_organizations: AdminOrgCount[];
};

export type PublicStats = {
  total_reports: number;
  total_organizations: number;
  resolved_reports: number;
  pending_reports: number;
  active_researchers: number;
  total_evidence_items: number;
};

export type PublicReport = {
  id: string;
  title: string;
  description?: string | null;
  organization_name?: string | null;
  category: string;
  severity: string;
  status: string;
  views_count: number;
  upvotes_count: number;
  created_at: string;
};

export type PublicOrganization = {
  id: string;
  name: string;
  slug: string;
  description?: string | null;
  website?: string | null;
  industry?: string | null;
  total_reports: number;
  resolved_reports: number;
  open_reports: number;
};

export type PublicReportDetail = {
  report: PublicReport;
  evidence: Evidence[];
  timeline: TimelineEvent[];
};

export type Evidence = {
  id: string;
  case_id: string;
  user_id: string;
  file_path: string;
  file_name: string;
  file_type: string;
  extracted_text?: string | null;
  metadata_json: Record<string, unknown>;
  uploaded_at: string;
};

export type TimelineEvent = {
  id: string;
  case_id: string;
  event_text: string;
  event_date?: string | null;
  source_evidence_id?: string | null;
  created_at: string;
};

export type SearchResult = {
  case_id: string;
  case_title: string;
  evidence_id?: string | null;
  snippet: string;
};
