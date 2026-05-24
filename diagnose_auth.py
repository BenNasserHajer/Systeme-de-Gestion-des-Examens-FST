"""
Script de diagnostic complet pour l'authentification
"""
import requests
import json
import sys

def print_section(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_backend_health():
    """Test 1: Vérifier que le backend est accessible"""
    print_section("TEST 1: Backend Health Check")
    
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        print(f"✅ Backend accessible")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return True
    except requests.exceptions.ConnectionError:
        print("❌ Backend non accessible sur http://localhost:8000")
        print("   → Démarrer le backend: cd server && python -m uvicorn app.main:app --reload")
        return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_api_docs():
    """Test 2: Vérifier que la documentation API est accessible"""
    print_section("TEST 2: API Documentation")
    
    try:
        response = requests.get("http://localhost:8000/docs", timeout=5)
        if response.status_code == 200:
            print("✅ Documentation API accessible: http://localhost:8000/docs")
            return True
        else:
            print(f"⚠️  Documentation retourne status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_admin_login():
    """Test 3: Tester le login admin"""
    print_section("TEST 3: Admin Login")
    
    url = "http://localhost:8000/api/auth/login"
    payload = {
        "email": "admin@fst.utm.tn",
        "mot_de_passe": "Admin@2026"
    }
    
    print(f"URL: {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, json=payload, timeout=5)
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Login réussi!")
            data = response.json()
            print(f"\nToken: {data.get('access_token', 'N/A')[:50]}...")
            print(f"User Type: {data.get('user', {}).get('type', 'N/A')}")
            print(f"User Email: {data.get('user', {}).get('email', 'N/A')}")
            return True, data.get('access_token')
        elif response.status_code == 422:
            print("❌ Erreur 422: Validation échouée")
            print(f"Détails: {json.dumps(response.json(), indent=2)}")
            print("\n💡 Cause probable: Champs manquants ou mal nommés")
            print("   → Vérifier que le backend attend bien 'email' et 'mot_de_passe'")
            return False, None
        elif response.status_code == 401:
            print("❌ Erreur 401: Credentials invalides")
            print(f"Détails: {json.dumps(response.json(), indent=2)}")
            print("\n💡 Cause probable: Mot de passe incorrect ou email non reconnu")
            print("   → Vérifier ADMIN_EMAIL et ADMIN_PASSWORD dans crud_auth.py")
            return False, None
        else:
            print(f"❌ Erreur {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            return False, None
            
    except requests.exceptions.ConnectionError:
        print("❌ Impossible de se connecter au backend")
        return False, None
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False, None

def test_auth_me(token):
    """Test 4: Vérifier le token avec /auth/me"""
    print_section("TEST 4: Token Validation (/auth/me)")
    
    if not token:
        print("⏭️  Skipped (pas de token)")
        return False
    
    url = "http://localhost:8000/api/auth/me"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Token valide!")
            print(f"User Info: {json.dumps(response.json(), indent=2)}")
            return True
        else:
            print(f"❌ Token invalide ou expiré")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_cors():
    """Test 5: Vérifier la configuration CORS"""
    print_section("TEST 5: CORS Configuration")
    
    url = "http://localhost:8000/api/auth/login"
    headers = {
        "Origin": "http://localhost:3000",
        "Content-Type": "application/json"
    }
    payload = {
        "email": "admin@fst.utm.tn",
        "mot_de_passe": "Admin@2026"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=5)
        
        cors_headers = {
            "Access-Control-Allow-Origin": response.headers.get("Access-Control-Allow-Origin"),
            "Access-Control-Allow-Credentials": response.headers.get("Access-Control-Allow-Credentials"),
        }
        
        print(f"CORS Headers: {json.dumps(cors_headers, indent=2)}")
        
        if cors_headers["Access-Control-Allow-Origin"] in ["*", "http://localhost:3000"]:
            print("✅ CORS configuré correctement")
            return True
        else:
            print("⚠️  CORS pourrait bloquer les requêtes depuis le frontend")
            print("   → Vérifier _cors_origins dans main.py")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def main():
    """Exécuter tous les tests"""
    print("\n" + "🔍 DIAGNOSTIC D'AUTHENTIFICATION".center(60))
    print("="*60)
    
    results = []
    
    # Test 1: Backend Health
    results.append(("Backend Health", test_backend_health()))
    
    if not results[0][1]:
        print("\n❌ Backend non accessible. Arrêt du diagnostic.")
        print("   Démarrer le backend puis relancer ce script.")
        sys.exit(1)
    
    # Test 2: API Docs
    results.append(("API Docs", test_api_docs()))
    
    # Test 3: Admin Login
    login_success, token = test_admin_login()
    results.append(("Admin Login", login_success))
    
    # Test 4: Token Validation
    if token:
        results.append(("Token Validation", test_auth_me(token)))
    
    # Test 5: CORS
    results.append(("CORS Config", test_cors()))
    
    # Résumé
    print_section("RÉSUMÉ")
    
    for test_name, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {test_name}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n🎉 Tous les tests sont passés!")
        print("\n📋 Prochaines étapes:")
        print("   1. Démarrer le frontend: cd frontend && npm run dev")
        print("   2. Ouvrir: http://localhost:3000/login")
        print("   3. Se connecter avec: admin@fst.utm.tn / Admin@2026")
        print("   4. Vérifier la redirection vers /planification")
    else:
        print("\n⚠️  Certains tests ont échoué. Voir les détails ci-dessus.")
        print("\n📖 Consulter: GUIDE_LOGIN_ADMIN.md pour plus d'aide")

if __name__ == "__main__":
    main()
