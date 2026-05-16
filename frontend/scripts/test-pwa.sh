#!/bin/bash

echo "🧪 Testing PWA Locally..."

# Build con PWA enabled
npm run build

# Servir con preview
npm run preview &
SERVER_PID=$!

echo "✅ Server running at http://localhost:4173"
echo "📱 Test PWA features:"
echo "   1. Open DevTools → Application → Service Workers"
echo "   2. Check 'Offline' and reload"
echo "   3. Test install prompt"
echo ""
echo "Press Ctrl+C to stop server"

wait $SERVER_PID
