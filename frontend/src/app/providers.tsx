/**
 * Providers composition root.
 * Wraps the app with QueryClientProvider and React Router.
 */

import type { ReactElement, ReactNode } from 'react';
import { QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { queryClient } from '@shared/api/queryClient';

interface ProvidersProps {
  children: ReactNode;
}

/**
 * Global providers composition root.
 * Add new global providers here (e.g., ThemeProvider, AuthProvider).
 */
export function Providers({ children }: ProvidersProps): ReactElement {
  return (
    <QueryClientProvider client={queryClient}>
      {children}
      {import.meta.env.DEV && <ReactQueryDevtools initialIsOpen={false} />}
    </QueryClientProvider>
  );
}
