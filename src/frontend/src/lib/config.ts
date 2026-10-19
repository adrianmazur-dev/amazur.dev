export interface Settings {
  readonly backendUrl: string;
  readonly linkedinTimeoutMs: number;
  readonly healthTimeoutMs: number;
}

export function loadSettings(): Settings {
  const rawBackendUrl = process.env.BACKEND_URL || import.meta.env.BACKEND_URL || 'http://127.0.0.1:8000';

  return Object.freeze({
    backendUrl: rawBackendUrl.replace(/\/+$/, ''),
    linkedinTimeoutMs: 10000,
    healthTimeoutMs: 20000,
  });
}

export const settings: Settings = loadSettings();
