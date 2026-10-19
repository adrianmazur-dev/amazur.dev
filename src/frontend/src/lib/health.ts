import { settings } from './config';

export type JsonValue = string | number | boolean | null | JsonValue[] | { [key: string]: JsonValue };

export interface HealthCheck {
  name: string;
  available: boolean;
  details?: Record<string, JsonValue>;
}

export interface HealthStatus {
  checks: HealthCheck[];
}

function isHealthCheck(value: unknown): value is HealthCheck {
  if (value === null || typeof value !== 'object' || Array.isArray(value)) return false;
  const check = value as Record<string, unknown>;
  return typeof check.name === 'string' && check.name.trim().length > 0
    && typeof check.available === 'boolean'
    && (check.details === undefined || (check.details !== null
      && typeof check.details === 'object' && !Array.isArray(check.details)));
}

function isHealthStatus(value: unknown): value is HealthStatus {
  if (value === null || typeof value !== 'object' || Array.isArray(value)) return false;
  const status = value as Record<string, unknown>;
  return Array.isArray(status.checks) && status.checks.every(isHealthCheck);
}

export async function getHealthStatus(): Promise<HealthStatus> {
  const response = await fetch(`${settings.backendUrl}/health`, {
    headers: { Accept: 'application/json' },
    cache: 'no-store',
    signal: AbortSignal.timeout(settings.healthTimeoutMs),
  });
  if (!response.ok && response.status !== 503) throw new Error(`Health request failed: ${response.status}`);

  const status: unknown = await response.json();
  if (!isHealthStatus(status)) throw new Error('Invalid health response');
  return status;
}
