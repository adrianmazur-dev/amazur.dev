import { defineAction } from 'astro:actions';
import { getHealthStatus } from '../lib/health';

export const server = {
  getHealth: defineAction({
    handler: async () => {
      return await getHealthStatus();
    },
  }),
};
