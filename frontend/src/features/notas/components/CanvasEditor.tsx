import { useRef, useEffect, useState, useCallback } from 'react';
import { Eraser, Pen, Undo, Trash2, Save } from 'lucide-react';
import type { Canvas as FabricCanvas } from 'fabric';


interface CanvasEditorProps {
  onSave: (canvasJson: string, thumbnail: string) => void;
  initialCanvas?: string;
}

export function CanvasEditor({ onSave, initialCanvas }: CanvasEditorProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [canvas, setCanvas] = useState<FabricCanvas | null>(null);
  const [tool, setTool] = useState<'pen' | 'eraser'>('pen');
  const [isLoading, setIsLoading] = useState(true);

  // Initialize Fabric.js
  useEffect(() => {
    let mounted = true;
    let fabricCanvas: FabricCanvas | null = null;

    const initFabric = async () => {
      if (!canvasRef.current) return;
      
      // Dynamic import
      const fabricModule = await import('fabric');
      if (!mounted) return;
      
      const fabricLib = fabricModule;
      if (!fabricLib?.Canvas) {
        console.error('Fabric.js failed to load');
        return;
      }
      
      const newCanvas = new fabricLib.Canvas(canvasRef.current, {
        isDrawingMode: true,
        width: 800,
        height: 400,
        backgroundColor: '#ffffff',
      });

      fabricCanvas = newCanvas;

      // Configure brush
      if (newCanvas.freeDrawingBrush) {
        newCanvas.freeDrawingBrush.color = '#000000';
        newCanvas.freeDrawingBrush.width = 2;
      }

      // Load initial canvas if provided
      if (initialCanvas) {
        newCanvas.loadFromJSON(initialCanvas, () => {
          newCanvas.renderAll();
        });
      }

      if (mounted) {
        setCanvas(newCanvas);
        setIsLoading(false);
      }
    };

    initFabric();

    return () => {
      mounted = false;
      if (fabricCanvas) {
        fabricCanvas.dispose();
      }
    };
  }, [initialCanvas]);

  const handleUndo = useCallback(() => {
    if (!canvas) return;
    const objects = canvas.getObjects();
    if (objects.length > 0) {
      canvas.remove(objects[objects.length - 1]);
      canvas.renderAll();
    }
  }, [canvas]);

  const handleClear = useCallback(() => {
    if (!canvas) return;
    canvas.clear();
    canvas.set('backgroundColor', '#ffffff');
    canvas.renderAll();
  }, [canvas]);

  const handleSave = useCallback(() => {
    if (!canvas) return;

    // Serialize canvas to JSON
    const json = JSON.stringify(canvas.toJSON());

    // Generate thumbnail
    const thumbnail = canvas.toDataURL({
      format: 'png',
      quality: 0.5,
      multiplier: 0.2,
    });

    onSave(json, thumbnail);
  }, [canvas, onSave]);

  const switchTool = useCallback((newTool: 'pen' | 'eraser') => {
    if (!canvas) return;
    setTool(newTool);

    if (newTool === 'eraser') {
      if (canvas.freeDrawingBrush) {
        canvas.freeDrawingBrush.color = '#ffffff';
        canvas.freeDrawingBrush.width = 20;
      }
    } else {
      if (canvas.freeDrawingBrush) {
        canvas.freeDrawingBrush.color = '#000000';
        canvas.freeDrawingBrush.width = 2;
      }
    }
  }, [canvas]);

  return (
    <div className="border rounded-lg p-4 space-y-4 bg-card">
      {/* Toolbar */}
      <div className="flex gap-2 flex-wrap">
        <button
          type="button"
          className={`px-3 py-1.5 rounded text-sm font-medium flex items-center gap-2 transition-colors ${
            tool === 'pen'
              ? 'bg-primary text-primary-foreground hover:bg-primary/90'
              : 'border border-input bg-background hover:bg-accent'
          } disabled:opacity-50`}
          onClick={() => switchTool('pen')}
          disabled={isLoading}
        >
          <Pen className="h-4 w-4" />
          Pen
        </button>
        <button
          type="button"
          className={`px-3 py-1.5 rounded text-sm font-medium flex items-center gap-2 transition-colors ${
            tool === 'eraser'
              ? 'bg-primary text-primary-foreground hover:bg-primary/90'
              : 'border border-input bg-background hover:bg-accent'
          } disabled:opacity-50`}
          onClick={() => switchTool('eraser')}
          disabled={isLoading}
        >
          <Eraser className="h-4 w-4" />
          Eraser
        </button>
        <div className="flex-1" />
        <button
          type="button"
          className="px-2 py-1.5 rounded text-sm hover:bg-accent disabled:opacity-50"
          onClick={handleUndo}
          disabled={isLoading}
          title="Undo"
        >
          <Undo className="h-4 w-4" />
        </button>
        <button
          type="button"
          className="px-2 py-1.5 rounded text-sm hover:bg-accent disabled:opacity-50"
          onClick={handleClear}
          disabled={isLoading}
          title="Clear"
        >
          <Trash2 className="h-4 w-4" />
        </button>
        <button
          type="button"
          className="px-3 py-1.5 rounded text-sm font-medium bg-primary text-primary-foreground hover:bg-primary/90 flex items-center gap-2 disabled:opacity-50"
          onClick={handleSave}
          disabled={isLoading}
        >
          <Save className="h-4 w-4" />
          Save
        </button>
      </div>

      {/* Canvas */}
      <div className="border rounded overflow-hidden bg-white flex justify-center">
        {isLoading && (
          <div className="h-[400px] flex items-center justify-center text-muted-foreground">
            Loading canvas...
          </div>
        )}
        <canvas 
          ref={canvasRef} 
          className={isLoading ? 'hidden' : 'block'}
        />
      </div>

      {/* Info */}
      <p className="text-xs text-muted-foreground">
        Supports mouse and stylus input. Use Pen for drawing, Eraser to remove strokes.
      </p>
    </div>
  );
}
