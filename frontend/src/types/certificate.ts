export interface Certificate {
  certificate_id: string;
  recipient_name: string;
  course_name: string;
  issue_date: string;
  content: string;
  qr_code?: string;
  qr_code_url?: string;
}

export interface VerificationResult {
  success: boolean;
  data?: Certificate;
  error?: string;
}
