import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { App } from '@app/App';
import '@styles/globals.css';

// Registrar el Service Worker de Vite PWA
// (autoUpdate — actualiza en segundo plano sin interrumpir al usuario)
import { registerSW } from 'virtual:pwa-register';

registerSW({ immediate: true });

const rootElement = document.getElementById('root');

if (!rootElement) {
  throw new Error('[Studiary] Root element #root not found in the document');
}

createRoot(rootElement).render(
  <StrictMode>
    <App />
  </StrictMode>
);
