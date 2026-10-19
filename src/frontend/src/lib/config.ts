export interface Settings {
  readonly appVersion: string;
  readonly backendUrl: string;
  readonly linkedinTimeoutMs: number;
  readonly healthTimeoutMs: number;
}

export function loadSettings(): Settings {
  const rawAppVersion = process.env.APP_VERSION || import.meta.env.APP_VERSION || 'dev';
  const rawBackendUrl = process.env.BACKEND_URL || import.meta.env.BACKEND_URL || 'http://127.0.0.1:8000';

  return Object.freeze({
    appVersion: rawAppVersion.trim(),
    backendUrl: rawBackendUrl.replace(/\/+$/, ''),
    linkedinTimeoutMs: 10000,
    healthTimeoutMs: 20000,
  });
}

export const settings: Settings = loadSettings();
