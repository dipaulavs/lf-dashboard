#!/bin/bash

echo "🛑 Parando Dashboard de Imóveis..."

# Matar processos
pkill -f "python.*app.py" 2>/dev/null && echo "✅ Flask parado"
pkill -f "ngrok" 2>/dev/null && echo "✅ Ngrok parado"

echo "✅ Todos os processos foram encerrados"
