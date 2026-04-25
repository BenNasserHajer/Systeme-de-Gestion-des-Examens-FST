#!/bin/bash

# Script de test de l'API de génération automatique
# Usage: ./test_api_generation.sh

echo "=========================================="
echo "TEST DE L'API DE GÉNÉRATION AUTOMATIQUE"
echo "=========================================="
echo ""

# Vérifier que le serveur est démarré
echo "🔍 Vérification du serveur..."
if ! curl -s http://localhost:8000/health > /dev/null; then
    echo "❌ Le serveur n'est pas démarré!"
    echo "   Démarrez-le avec: uvicorn app.main:app --reload"
    exit 1
fi
echo "✅ Serveur démarré"
echo ""

# Test 1: Health check
echo "📋 Test 1: Health Check"
echo "----------------------------------------"
curl -s http://localhost:8000/health | python -m json.tool
echo ""
echo ""

# Test 2: Liste des planifications
echo "📋 Test 2: Liste des Planifications"
echo "----------------------------------------"
curl -s http://localhost:8000/api/planifications/ | python -m json.tool
echo ""
echo ""

# Test 3: Génération automatique
echo "📋 Test 3: Génération Automatique"
echo "----------------------------------------"
echo "Envoi de la requête de génération..."
RESPONSE=$(curl -s -X POST http://localhost:8000/api/sessions/1/generer \
  -H "Content-Type: application/json" \
  -d @test_generation_request.json)

echo "$RESPONSE" | python -m json.tool

# Extraire les résultats
NB_CREES=$(echo "$RESPONSE" | python -c "import sys, json; print(json.load(sys.stdin).get('nb_crees', 0))")
NB_CONFLITS=$(echo "$RESPONSE" | python -c "import sys, json; print(json.load(sys.stdin).get('nb_conflits', 0))")

echo ""
echo "📊 Résultats:"
echo "  - Planifications créées: $NB_CREES"
echo "  - Conflits détectés: $NB_CONFLITS"
echo ""

# Test 4: Vérifier les planifications créées
if [ "$NB_CREES" -gt 0 ]; then
    echo "📋 Test 4: Vérification des Planifications Créées"
    echo "----------------------------------------"
    curl -s "http://localhost:8000/api/planifications/?session_id=1" | python -m json.tool
    echo ""
fi

echo ""
echo "=========================================="
if [ "$NB_CREES" -gt 0 ] && [ "$NB_CONFLITS" -eq 0 ]; then
    echo "✅ TOUS LES TESTS SONT PASSÉS!"
else
    echo "⚠️  Tests terminés avec des avertissements"
fi
echo "=========================================="
