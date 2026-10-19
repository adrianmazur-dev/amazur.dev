import { settings } from './config';

export interface LinkedInProfile {
  first_name: string | null;
  last_name: string | null;
  headline: string | null;
  summary: string | null;
  industry: string | null;
  location: string | null;
}

export interface LinkedInExperience {
  company_name: string | null;
  title: string | null;
  description: string | null;
  location: string | null;
  start_date: string | null;
  end_date: string | null;
}

function isLinkedInExperience(value: unknown): value is LinkedInExperience {
  if (value === null || typeof value !== 'object' || Array.isArray(value)) return false;

  const experience = value as Record<string, unknown>;
  const fields = ['company_name', 'title', 'description', 'location', 'start_date', 'end_date'] as const;
  return fields.every((field) => experience[field] === null || typeof experience[field] === 'string');
}

function isLinkedInProfile(value: unknown): value is LinkedInProfile {
  if (value === null || typeof value !== 'object' || Array.isArray(value)) return false;

  const profile = value as Record<string, unknown>;
  const fields = ['first_name', 'last_name', 'headline', 'summary', 'industry', 'location'] as const;
  return fields.every((field) => profile[field] === null || typeof profile[field] === 'string');
}

export async function getLinkedInProfile(): Promise<LinkedInProfile> {
  const response = await fetch(`${settings.backendUrl}/linkedin/profile`, {
    headers: { Accept: 'application/json' },
    cache: 'no-store',
    signal: AbortSignal.timeout(settings.linkedinTimeoutMs),
  });
  if (!response.ok) throw new Error(`Profile request failed: ${response.status}`);

  const profile: unknown = await response.json();
  if (!isLinkedInProfile(profile)) throw new Error('Invalid profile response');
  return profile;
}

export async function getLinkedInExperience(): Promise<LinkedInExperience[]> {
  const response = await fetch(`${settings.backendUrl}/linkedin/experience`, {
    headers: { Accept: 'application/json' },
    cache: 'no-store',
    signal: AbortSignal.timeout(settings.linkedinTimeoutMs),
  });
  if (!response.ok) throw new Error(`Experience request failed: ${response.status}`);

  const experience: unknown = await response.json();
  if (!Array.isArray(experience) || !experience.every(isLinkedInExperience)) {
    throw new Error('Invalid experience response');
  }
  return experience;
}
