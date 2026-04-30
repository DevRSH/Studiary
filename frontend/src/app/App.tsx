/**
 * App root — composes Providers and Router.
 */

import type { ReactElement } from 'react';
import { Providers } from './providers';
import { Router } from './router';

/**
 * Main application component.
 * Combines providers and routing logic.
 */
export function App(): ReactElement {
  return (
    <Providers>
      <Router />
    </Providers>
  );
}
