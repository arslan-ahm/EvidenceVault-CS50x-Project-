export type User = {
  id: string;
  email: string;
  created_at: string;
};

export type Case = {
  id: string;
  title: string;
  description?: string | null;
  user_id: string;
  created_at: string;
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
