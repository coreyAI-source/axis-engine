import axios from "axios";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const api = axios.create({
  baseURL: API_BASE,
  headers: { "Content-Type": "application/json" },
});

// Attach JWT from localStorage on every request
api.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("axis_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

// ---- Typed helpers ----

export const auth = {
  login: (email: string, password: string) =>
    api.post<{ access_token: string }>("/auth/login", new URLSearchParams({ username: email, password }), {
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
    }),
};

export const dashboard = {
  summary: () => api.get("/dashboard/summary"),
};

export const processes = {
  list: () => api.get("/processes/"),
  get: (id: string) => api.get(`/processes/${id}`),
  create: (data: object) => api.post("/processes/", data),
  update: (id: string, data: object) => api.patch(`/processes/${id}`, data),
};

export const audits = {
  list: (params?: object) => api.get("/audits/", { params }),
  get: (id: string) => api.get(`/audits/${id}`),
  create: (data: object) => api.post("/audits/", data),
  update: (id: string, data: object) => api.patch(`/audits/${id}`, data),
  prompts: (id: string) => api.get("/audit-prompts/", { params: { audit_id: id } }),
  generatePrompts: (id: string) => api.post("/audit-prompts/generate", null, { params: { audit_id: id } }),
};

export const findings = {
  list: (params?: object) => api.get("/findings/", { params }),
  get: (id: string) => api.get(`/findings/${id}`),
};

export const actions = {
  list: (params?: object) => api.get("/actions/", { params }),
  overdue: () => api.get("/actions/overdue"),
  atRisk: () => api.get("/actions/at-risk"),
  update: (id: string, data: object) => api.patch(`/actions/${id}`, data),
  comment: (id: string, text: string) => api.post(`/actions/${id}/comments`, { action_id: id, comment_text: text }),
};

export const reports = {
  documentReview: (auditId: string) => api.get(`/reports/audits/${auditId}/document-review`),
  auditPlan: (auditId: string) => api.get(`/reports/audits/${auditId}/audit-plan`),
  timetable: (auditId: string) => api.get(`/reports/audits/${auditId}/timetable`),
  auditReport: (auditId: string) => api.get(`/reports/audits/${auditId}/report`),
  findingsRegister: (auditId: string) => api.get(`/reports/audits/${auditId}/findings-register`),
};

export const monitoring = {
  tasks: (params?: object) => api.get("/monitoring-tasks/", { params }),
  runs: (taskId: string) => api.get("/monitoring-runs/", { params: { task_id: taskId } }),
};

export const standards = {
  list: () => api.get("/standards/"),
  clauses: (standardId: string) => api.get(`/standards/${standardId}/clauses`),
};
