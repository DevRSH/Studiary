/**
 * Periodos dashboard page — Sprint 0 placeholder.
 * Full implementation in Sprint 1.
 */

import type { ReactElement } from 'react';

/**
 * Dashboard page showing academic periods.
 * Displays Studiary branding while Sprint 1 is implemented.
 */
export function PeriodosPage(): ReactElement {
  return (
    <main className="min-h-screen bg-surface flex flex-col items-center justify-center p-6">
      {/* Logo area */}
      <div className="mb-8 flex flex-col items-center gap-4 animate-fade-in">
        <div className="w-20 h-20 rounded-3xl bg-gradient-to-br from-primary-500 to-primary-700 flex items-center justify-center shadow-2xl shadow-primary-900/50">
          <span className="text-4xl">📚</span>
        </div>
        <h1 className="gradient-text text-4xl font-bold tracking-tight">Studiary</h1>
        <p className="text-white/50 text-base text-center max-w-xs">
          Centro de Comando Académico
        </p>
      </div>

      {/* Status card */}
      <div className="glass-card p-6 w-full max-w-sm animate-slide-up">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse" />
          <span className="text-white/70 text-sm font-medium">Sistema inicializado</span>
        </div>
        <div className="space-y-2 text-sm text-white/40">
          <div className="flex justify-between">
            <span>Backend API</span>
            <span className="text-emerald-400 font-mono">:8001 ✓</span>
          </div>
          <div className="flex justify-between">
            <span>Frontend PWA</span>
            <span className="text-emerald-400 font-mono">:5174 ✓</span>
          </div>
          <div className="flex justify-between">
            <span>Sprint</span>
            <span className="text-white/60">0 — Foundation</span>
          </div>
        </div>

        {/* Demo Link */}
        <div className="mt-6 pt-6 border-t border-white/10">
          <a 
            href="/demo"
            className="flex items-center gap-2 text-primary-400 hover:text-primary-300 transition-colors group"
          >
            <span className="text-lg group-hover:scale-110 transition-transform">🎮</span>
            <span className="font-medium">Probar Demo del Calculador</span>
            <span className="ml-auto text-white/40 group-hover:text-white/60">→</span>
          </a>
          <p className="text-white/40 text-xs mt-1 ml-7">
            Página de demostración permanente para probar el motor predictivo
          </p>
        </div>
      </div>

      <p className="mt-8 text-white/20 text-xs text-center">
        Studiary v1.0.0 — Sprint 0 completado
      </p>
    </main>
  );
}
