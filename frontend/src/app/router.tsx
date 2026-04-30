/**
 * Application router using React Router v6 data routing.
 * Uses lazy loading per feature for optimal bundle splitting.
 */

import { lazy, Suspense } from 'react';
import type { ReactElement } from 'react';
import { createBrowserRouter, RouterProvider, Outlet } from 'react-router-dom';

// Lazy-loaded feature pages
const DashboardPage = lazy(() => import('@features/periodos').then((m) => ({ default: m.PeriodosPage })));

function RootLayout(): ReactElement {
  return (
    <div className="min-h-screen bg-surface">
      <Outlet />
    </div>
  );
}

function LoadingFallback(): ReactElement {
  return (
    <div className="min-h-screen bg-surface flex items-center justify-center">
      <div className="flex flex-col items-center gap-4 animate-pulse-soft">
        <div className="w-12 h-12 rounded-2xl bg-primary-600" />
        <span className="text-white/50 text-sm font-medium">Cargando…</span>
      </div>
    </div>
  );
}

const router = createBrowserRouter([
  {
    path: '/',
    element: <RootLayout />,
    children: [
      {
        index: true,
        element: (
          <Suspense fallback={<LoadingFallback />}>
            <DashboardPage />
          </Suspense>
        ),
      },
    ],
  },
]);

export function Router(): ReactElement {
  return <RouterProvider router={router} />;
}
