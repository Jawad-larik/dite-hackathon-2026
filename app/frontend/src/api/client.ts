import type { RoleInfo, Question, QuestionEvaluation, SessionReport } from '../types';
import sampleReportFixture from '../fixtures/report-sample.json';

const rawBase = (import.meta.env.VITE_API_URL as string | undefined) || '';
export const API_BASE = rawBase ? `${rawBase.replace(/\/$/, '')}/api` : '/api';

export function getAuthToken(): string | null {
  if (typeof localStorage === 'undefined') return null;
  return localStorage.getItem('auth_token') || localStorage.getItem('token');
}

export function setAuthToken(token: string, user?: { id: string; email: string }) {
  if (typeof localStorage === 'undefined') return;
  localStorage.setItem('auth_token', token);
  localStorage.setItem('token', token);
  if (user) {
    localStorage.setItem('auth_user', JSON.stringify(user));
  }
}

export function clearAuthToken() {
  if (typeof localStorage === 'undefined') return;
  localStorage.removeItem('auth_token');
  localStorage.removeItem('token');
  localStorage.removeItem('auth_user');
}

export function getStoredUser(): { id: string; email: string } | null {
  if (typeof localStorage === 'undefined') return null;
  const str = localStorage.getItem('auth_user');
  if (!str) return null;
  try {
    return JSON.parse(str);
  } catch {
    return null;
  }
}

/**
 * Robust fetch with explicit timeout to prevent hanging on offline backends,
 * automatically injecting Bearer JWT token and handling 401 Unauthorized.
 */
async function fetchWithTimeout(url: string, options: RequestInit = {}, timeoutMs = 8000): Promise<Response> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);

  const token = getAuthToken();
  const headers = new Headers(options.headers || {});
  if (token && !headers.has('Authorization')) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  try {
    const response = await fetch(url, {
      ...options,
      headers,
      signal: controller.signal,
    });

    if (response.status === 401) {
      clearAuthToken();
      if (typeof window !== 'undefined') {
        window.dispatchEvent(new CustomEvent('auth-unauthorized'));
      }
    }

    return response;
  } finally {
    clearTimeout(timer);
  }
}

/* =========================================================================
   AUTH APIS
========================================================================= */

export async function apiSignup(email: string, password: string): Promise<{ token: string; user: { id: string; email: string } }> {
  const res = await fetchWithTimeout(`${API_BASE}/auth/signup`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Registration failed' }));
    throw new Error(err.detail || 'Registration failed');
  }
  const data = await res.json();
  setAuthToken(data.token, data.user);
  return data;
}

export async function apiLogin(email: string, password: string): Promise<{ token: string; user: { id: string; email: string } }> {
  const res = await fetchWithTimeout(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Invalid credentials' }));
    throw new Error(err.detail || 'Invalid email or password');
  }
  const data = await res.json();
  setAuthToken(data.token, data.user);
  return data;
}

export async function apiGetMe(): Promise<{ id: string; email: string }> {
  const res = await fetchWithTimeout(`${API_BASE}/auth/me`);
  if (!res.ok) throw new Error('Not authenticated');
  const user = await res.json();
  if (typeof localStorage !== 'undefined') {
    localStorage.setItem('auth_user', JSON.stringify(user));
  }
  return user;
}

/* =========================================================================
   INTERVIEW & SESSION APIS
========================================================================= */

export async function fetchRoles(): Promise<RoleInfo[]> {
  try {
    const res = await fetchWithTimeout(`${API_BASE}/roles`);
    if (!res.ok) throw new Error('Backend offline');
    return res.json();
  } catch {
    return [
      { id: 'software_engineer', title: 'Software Engineer', description: 'Distributed systems, system design, algorithm concurrency' },
      { id: 'product_manager', title: 'Product Manager', description: 'Product strategy, execution, technical roadmapping' },
      { id: 'data_scientist', title: 'Data Scientist', description: 'Applied machine learning, causal inference, data systems' },
    ];
  }
}

export async function startSession(
  roleId: string, 
  interviewType: string = 'all', 
  numQuestions: number = 5,
  language: string = 'en',
  jdText?: string,
  resumeText?: string
): Promise<{ session_id: string; role_id: string; role_title: string; language: string; total_questions: number; first_question: Question }> {
  const res = await fetchWithTimeout(`${API_BASE}/sessions/start`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      role_id: roleId,
      interview_type: interviewType,
      num_questions: numQuestions,
      language: language,
      jd_text: jdText || '',
      resume_text: resumeText || ''
    })
  }, 25000);
  if (!res.ok) throw new Error('Failed to start interview session');
  return res.json();
}

export async function fetchSessionQuestions(sessionId: string): Promise<Question[]> {
  const res = await fetchWithTimeout(`${API_BASE}/sessions/${sessionId}/questions`, {}, 15000);
  if (!res.ok) throw new Error('Failed to fetch questions for session');
  return res.json();
}

export async function submitAnswer(
  sessionId: string,
  payload: {
    question_id: string;
    transcript: string;
    duration_seconds: number;
    language?: string;
    confidence_score?: number;
    audio_filler_count?: number;
  }
): Promise<QuestionEvaluation> {
  const res = await fetchWithTimeout(`${API_BASE}/sessions/${sessionId}/evaluate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      session_id: sessionId,
      ...payload
    })
  }, 25000);
  if (!res.ok) throw new Error('Failed to evaluate answer');
  return res.json();
}

export async function analyzeWebcamFrame(imageBase64: string): Promise<{
  face_detected: boolean;
  confidence_score: number;
  eye_contact: string;
  is_smiling?: boolean;
}> {
  try {
    const res = await fetchWithTimeout(`${API_BASE}/vision/analyze-frame`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ image_base64: imageBase64 })
    }, 4000);
    if (!res.ok) throw new Error('Vision analysis request failed');
    return res.json();
  } catch {
    return { face_detected: true, confidence_score: 80.0, eye_contact: 'Good' };
  }
}

export async function transcribeAudio(audioBlob: Blob, language: string = 'en'): Promise<{
  transcript: string;
  duration: number;
  detected_language?: string;
}> {
  const formData = new FormData();
  formData.append('audio_file', audioBlob, 'response.webm');
  formData.append('language', language);

  const res = await fetchWithTimeout(`${API_BASE}/speech/transcribe`, {
    method: 'POST',
    body: formData
  }, 15000);
  if (!res.ok) throw new Error('Speech transcription failed');
  return res.json();
}

export async function transcribeSessionAudio(sessionId: string, audioBlob: Blob, language: string = 'en'): Promise<{
  transcript: string;
  duration: number;
  confidence?: number;
}> {
  const formData = new FormData();
  formData.append('audio_file', audioBlob, 'response.webm');
  formData.append('language', language);

  const res = await fetchWithTimeout(`${API_BASE}/sessions/${sessionId}/transcribe`, {
    method: 'POST',
    body: formData
  }, 15000);
  if (!res.ok) throw new Error('Session speech transcription failed');
  return res.json();
}

export async function fetchSessionReport(sessionId: string): Promise<SessionReport> {
  try {
    const res = await fetchWithTimeout(`${API_BASE}/sessions/${sessionId}/report`, {}, 15000);
    if (!res.ok) throw new Error('Failed to generate interview report from backend');
    return res.json();
  } catch (err) {
    console.warn('[API Client] Backend report unavailable, using cached report dossier fixture:', err);
    return sampleReportFixture as unknown as SessionReport;
  }
}

export function getDownloadPdfUrl(sessionId: string): string {
  const token = getAuthToken();
  const base = `${API_BASE}/sessions/${sessionId}/pdf`;
  return token ? `${base}?token=${encodeURIComponent(token)}` : base;
}

export interface HistoricalSessionSummary {
  id: string;
  session_id: string;
  role_id: string;
  role_title: string;
  created_at: string;
  overall_score: number;
  content_score: number;
  clarity_score: number;
  confidence_score: number;
  composure_score?: number;
  status: string;
  is_demo?: boolean;
  total_questions: number;
}

export async function fetchHistoricalSessions(limit = 20, offset = 0): Promise<{ total: number; sessions: HistoricalSessionSummary[] }> {
  try {
    const res = await fetchWithTimeout(`${API_BASE}/sessions?limit=${limit}&offset=${offset}`, {}, 8000);
    if (!res.ok) throw new Error('Failed to fetch historical sessions');
    return res.json();
  } catch (err) {
    console.warn('[API Client] Backend offline or unavailable, falling back to local cache:', err);
    throw err;
  }
}

export async function endSession(sessionId: string): Promise<SessionReport> {
  try {
    const res = await fetchWithTimeout(`${API_BASE}/sessions/${sessionId}/end`, { method: 'POST' }, 15000);
    if (!res.ok) throw new Error('Failed to conclude session');
    return res.json();
  } catch (err) {
    console.warn('[API Client] Error concluding session via backend:', err);
    return fetchSessionReport(sessionId);
  }
}

export async function extractPdfText(file: File): Promise<{ text: string }> {
  if (file.type !== 'application/pdf' && !file.name.toLowerCase().endsWith('.pdf')) {
    throw new Error('Unsupported file type. Please upload a PDF document.');
  }
  if (file.size > 2 * 1024 * 1024) {
    throw new Error('Max 2 MB');
  }

  const formData = new FormData();
  formData.append('file', file);

  const res = await fetchWithTimeout(`${API_BASE}/extract`, {
    method: 'POST',
    body: formData,
  }, 25000);

  if (res.status === 413) {
    throw new Error('Max 2 MB');
  }
  if (res.status === 415) {
    throw new Error('Unsupported media type. Only PDF files are accepted.');
  }
  if (res.status === 422) {
    throw new Error('This PDF has no selectable text. Please paste the text manually.');
  }
  if (!res.ok) {
    const errorJson = await res.json().catch(() => ({ detail: 'Failed to extract text from PDF' }));
    throw new Error(errorJson.detail || 'Failed to extract text from PDF');
  }

  return res.json();
}
