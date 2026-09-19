export interface Project {
  id: number
  name: string
  created_at: string
  updated_at: string
  last_viewed_paper_id: number | null
  paper_count: number
}

export interface TagOption {
  id: number
  value: string
  position: number
  weight: number
  children: TagOption[]
}

export interface TagField {
  id: number
  name: string
  is_protected: boolean
  position: number
  options: TagOption[]
}

export interface PaperListItem {
  id: number
  title: string
  doi: string | null
  authors: string | null
  year: number | null
  order_index: number
  filled_field_count: number
  total_field_count: number
  notes: string
  rating: number | null
  score: number
}

export type PaperSource = 'xlsx_import' | 'crossref_doi' | 'crossref_title' | 'manual'

export interface PaperDetail {
  id: number
  project_id: number
  title: string
  abstract: string | null
  doi: string | null
  authors: string | null
  year: number | null
  source_title: string | null
  notes: string
  source: PaperSource
  order_index: number
  tags: Record<number, number[]>
  rating: number | null
  score: number
}

export interface DuplicateInfo {
  is_duplicate: boolean
  reason: 'doi' | 'title' | null
  matched_paper_id: number | null
  matched_title: string | null
}

export interface PaperCreateResult {
  paper: PaperDetail | null
  duplicate: DuplicateInfo | null
}

export interface ImportPreviewRow {
  row_index: number
  title: string
  abstract: string | null
  doi: string | null
  authors: string | null
  year: number | null
  source_title: string | null
  raw_metadata: Record<string, unknown>
  is_duplicate: boolean
  duplicate_reason: 'doi' | 'title' | null
  matched_paper_id: number | null
  matched_title: string | null
  default_action: 'add' | 'skip'
}

export interface ImportPreviewResponse {
  rows: ImportPreviewRow[]
  new_count: number
  duplicate_count: number
}

export interface ImportCommitResponse {
  added_count: number
  skipped_count: number
  paper_ids: number[]
}

export interface LookupCandidate {
  title: string
  doi: string | null
  abstract: string | null
  abstract_available: boolean
  authors: string | null
  year: number | null
  source_title: string | null
  score: number | null
  raw_metadata: Record<string, unknown>
  duplicate: DuplicateInfo
}

export interface ApiErrorBody {
  detail?: string | { message: string; affected_paper_ids?: number[] }
}

export interface TagDistributionEntry {
  field_id: number
  field_name: string
  option_id: number
  option_path: string
  weight: number
  count: number
}

export interface DashboardStats {
  total_papers: number
  fully_tagged_count: number
  rated_count: number
  with_notes_count: number
  average_rating: number | null
  average_score: number
  max_rating: number
  max_score: number
  tag_distribution: TagDistributionEntry[]
  top_papers: PaperListItem[]
}
