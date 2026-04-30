/**
 * TanStack Query client configuration.
 *
 * Optimizado para Railway Free Tier: retry conservador y stale time
 * largo para minimizar llamadas redundantes a la API.
 */

import { QueryClient } from '@tanstack/react-query';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5,   // 5 minutos — reduce re-fetches
      gcTime: 1000 * 60 * 30,     // 30 minutos — mantiene caché en memoria
      retry: 1,                    // Solo 1 retry para no saturar Railway
      refetchOnWindowFocus: false, // Evita re-fetches innecesarios en mobile
    },
    mutations: {
      retry: 0,
    },
  },
});
