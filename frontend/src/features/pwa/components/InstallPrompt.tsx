import { useEffect, useState } from 'react';
import { Download, X } from 'lucide-react';

interface BeforeInstallPromptEvent extends Event {
  prompt: () => Promise<void>;
  userChoice: Promise<{ outcome: 'accepted' | 'dismissed' }>;
}

export function InstallPrompt() {
  const [deferredPrompt, setDeferredPrompt] = useState<BeforeInstallPromptEvent | null>(null);
  const [showPrompt, setShowPrompt] = useState(false);

  useEffect(() => {
    const handler = (e: Event) => {
      e.preventDefault();
      setDeferredPrompt(e as BeforeInstallPromptEvent);
      
      // Mostrar prompt después de 30 segundos de uso
      setTimeout(() => {
        const dismissed = localStorage.getItem('pwa-install-dismissed');
        if (!dismissed) {
          setShowPrompt(true);
        }
      }, 30000);
    };

    window.addEventListener('beforeinstallprompt', handler);

    return () => {
      window.removeEventListener('beforeinstallprompt', handler);
    };
  }, []);

  const handleInstall = async () => {
    if (!deferredPrompt) return;

    deferredPrompt.prompt();
    const { outcome } = await deferredPrompt.userChoice;

    if (outcome === 'accepted') {
      setShowPrompt(false);
      setDeferredPrompt(null);
    }
  };

  const handleDismiss = () => {
    setShowPrompt(false);
    localStorage.setItem('pwa-install-dismissed', 'true');
  };

  if (!showPrompt || !deferredPrompt) return null;

  return (
    <div className="fixed bottom-4 left-4 right-4 md:left-auto md:w-96 z-50">
      <div className="p-4 bg-white rounded-lg shadow-lg border-2 border-cyan-500">
        <div className="flex items-start gap-3">
          <Download className="h-5 w-5 text-cyan-600 flex-shrink-0 mt-0.5" />
          <div className="flex-1 space-y-2">
            <h3 className="font-semibold text-sm">Instalar Studiary</h3>
            <p className="text-xs text-gray-600">
              Instala la app en tu dispositivo para acceso rápido y uso offline
            </p>
            <div className="flex gap-2">
              <button 
                onClick={handleInstall} 
                className="flex-1 px-3 py-1.5 text-sm bg-cyan-600 text-white rounded hover:bg-cyan-700"
              >
                Instalar
              </button>
              <button 
                onClick={handleDismiss}
                className="px-3 py-1.5 text-sm text-gray-600 hover:bg-gray-100 rounded"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
