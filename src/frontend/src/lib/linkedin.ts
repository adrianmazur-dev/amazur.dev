export interface LinkedInProfile {
  first_name: string | null;
  last_name: string | null;
  headline: string | null;
  summary: string | null;
  industry: string | null;
  location: string | null;
}

function isLinkedInProfile(value: unknown): value is LinkedInProfile {
  if (value === null || typeof value !== 'object' || Array.isArray(value)) return false;

  const profile = value as Record<string, unknown>;
  const fields = ['first_name', 'last_name', 'headline', 'summary', 'industry', 'location'] as const;
  return fields.every((field) => profile[field] === null || typeof profile[field] === 'string');
}

export async function getLinkedInProfile(): Promise<LinkedInProfile> {
  const response = await fetch('/linkedin/profile', {
    headers: { Accept: 'application/json' },
    cache: 'no-store',
    signal: AbortSignal.timeout(10000),
  });
  if (!response.ok) throw new Error(`Profile request failed: ${response.status}`);

  const profile: unknown = await response.json();
  if (!isLinkedInProfile(profile)) throw new Error('Invalid profile response');
  return profile;
}
