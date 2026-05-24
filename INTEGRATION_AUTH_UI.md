# 🎨 Intégration de l'UI d'Authentification

## ✅ Composants Créés

### 1. Page de Login (`/login`)
**Fichier:** `frontend/src/app/login/page.tsx`

**Fonctionnalités:**
- ✅ Design moderne avec gradient
- ✅ Formulaire de connexion avec validation
- ✅ Gestion des erreurs
- ✅ État de chargement
- ✅ Icônes SVG intégrées
- ✅ Informations de test affichées
- ✅ Responsive design

**Comptes de test affichés:**
- Admin: `admin / admin123`
- Enseignant: `nom.prenom / password123`

### 2. AuthProvider
**Fichier:** `frontend/src/components/auth/AuthProvider.tsx`

**Fonctionnalités:**
- ✅ Context API pour l'état global
- ✅ Gestion du token JWT
- ✅ Persistance dans localStorage
- ✅ Redirection automatique
- ✅ Hook `useAuth()` personnalisé

### 3. UserMenu
**Fichier:** `frontend/src/components/auth/UserMenu.tsx`

**Fonctionnalités:**
- ✅ Avatar avec initiales
- ✅ Menu dropdown
- ✅ Affichage du profil
- ✅ Badge administrateur
- ✅ Bouton de déconnexion
- ✅ Fermeture au clic extérieur

## 🔧 Intégration dans le Projet

### Étape 1: Wrapper l'application avec AuthProvider

**Fichier:** `frontend/src/app/layout.tsx`

```typescript
import { AuthProvider } from "@/components/auth/AuthProvider";

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="fr" suppressHydrationWarning>
      <body suppressHydrationWarning>
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  );
}
```

**Note:** `suppressHydrationWarning` corrige l'avertissement d'hydration.

### Étape 2: Ajouter UserMenu à la Navbar

**Fichier:** `frontend/src/components/ui/Navbar.tsx`

```typescript
import UserMenu from "@/components/auth/UserMenu";

export default function Navbar() {
  return (
    <nav className="bg-white border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          {/* Logo et navigation */}
          <div className="flex">
            {/* ... */}
          </div>

          {/* Menu utilisateur */}
          <div className="flex items-center">
            <UserMenu />
          </div>
        </div>
      </div>
    </nav>
  );
}
```

### Étape 3: Protéger les Routes

**Fichier:** `frontend/src/app/(admin)/layout.tsx`

```typescript
"use client";

import { useAuth } from "@/components/auth/AuthProvider";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { isAuthenticated, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !isAuthenticated) {
      router.push("/login");
    }
  }, [isAuthenticated, loading, router]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  return <>{children}</>;
}
```

### Étape 4: Utiliser l'Auth dans les Composants

```typescript
"use client";

import { useAuth } from "@/components/auth/AuthProvider";

export default function MyComponent() {
  const { user, token, isAuthenticated, logout } = useAuth();

  if (!isAuthenticated) {
    return <div>Non authentifié</div>;
  }

  return (
    <div>
      <h1>Bonjour {user?.enseignant.prenom}!</h1>
      {user?.is_admin && <p>Vous êtes administrateur</p>}
      <button onClick={logout}>Se déconnecter</button>
    </div>
  );
}
```

## 🎨 Personnalisation du Design

### Couleurs

Le design utilise un gradient bleu-violet. Pour changer:

```typescript
// Dans login/page.tsx
className="bg-gradient-to-br from-blue-600 to-purple-600"
// Remplacer par:
className="bg-gradient-to-br from-green-600 to-teal-600"
```

### Logo

Remplacer l'icône SVG par votre logo:

```typescript
<div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-blue-600 to-purple-600 rounded-2xl mb-4 shadow-lg">
  <img src="/logo.png" alt="Logo" className="w-10 h-10" />
</div>
```

### Textes

Modifier les textes dans `login/page.tsx`:

```typescript
<h1 className="text-3xl font-bold text-gray-900 mb-2">
  Votre Titre Personnalisé
</h1>
<p className="text-gray-600">
  Votre sous-titre personnalisé
</p>
```

## 🔐 Sécurité

### Token JWT

Le token est stocké dans `localStorage` et envoyé dans les headers:

```typescript
const response = await fetch("http://localhost:8000/api/...", {
  headers: {
    "Authorization": `Bearer ${token}`,
    "Content-Type": "application/json",
  },
});
```

### Expiration du Token

Le token expire après 30 minutes (configurable dans le backend).

Pour gérer l'expiration:

```typescript
// Dans AuthProvider.tsx
const checkTokenExpiration = () => {
  const token = localStorage.getItem("access_token");
  if (token) {
    // Décoder le JWT et vérifier l'expiration
    const payload = JSON.parse(atob(token.split('.')[1]));
    const exp = payload.exp * 1000; // Convertir en millisecondes
    
    if (Date.now() >= exp) {
      logout();
    }
  }
};

// Vérifier toutes les minutes
useEffect(() => {
  const interval = setInterval(checkTokenExpiration, 60000);
  return () => clearInterval(interval);
}, []);
```

## 🧪 Tests

### Test de la Page de Login

1. Démarrer le backend et frontend
2. Aller sur: http://localhost:3000/login
3. Tester avec:
   - Username: `admin`
   - Password: `admin123`
4. Vérifier la redirection vers `/`

### Test du UserMenu

1. Se connecter
2. Cliquer sur l'avatar en haut à droite
3. Vérifier que le menu s'ouvre
4. Cliquer sur "Se déconnecter"
5. Vérifier la redirection vers `/login`

### Test de Protection des Routes

1. Se déconnecter
2. Essayer d'accéder à `/surveillance`
3. Vérifier la redirection vers `/login`

## 🐛 Correction de l'Avertissement d'Hydration

L'avertissement d'hydration est causé par des différences entre le rendu serveur et client.

**Solution appliquée:**

```typescript
// Dans layout.tsx
<html lang="fr" suppressHydrationWarning>
  <body suppressHydrationWarning>
    {children}
  </body>
</html>
```

Cela supprime l'avertissement pour les attributs ajoutés par les extensions de navigateur.

## 📱 Responsive Design

Le design est responsive:

- **Mobile (< 768px):** Avatar seul, menu dropdown
- **Tablet (768px - 1024px):** Avatar + nom
- **Desktop (> 1024px):** Avatar + nom + grade

## 🎯 Prochaines Étapes

### Fonctionnalités à Ajouter

1. **Page de Profil**
   - Afficher les informations de l'enseignant
   - Modifier le mot de passe
   - Voir l'historique des connexions

2. **Récupération de Mot de Passe**
   - Formulaire "Mot de passe oublié"
   - Envoi d'email de réinitialisation
   - Page de réinitialisation

3. **Authentification à Deux Facteurs (2FA)**
   - QR Code pour Google Authenticator
   - Vérification du code à la connexion

4. **Gestion des Sessions**
   - Voir les sessions actives
   - Déconnecter les autres appareils

5. **Notifications**
   - Toast pour connexion réussie
   - Toast pour déconnexion
   - Toast pour erreurs

## 📚 Documentation API

### Endpoints Utilisés

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/api/auth/login` | POST | Connexion |
| `/api/auth/logout` | POST | Déconnexion |
| `/api/auth/me` | GET | Profil utilisateur |

### Format de Réponse Login

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@university.edu",
    "is_admin": true,
    "enseignant": {
      "id": 1,
      "nom": "Dupont",
      "prenom": "Jean",
      "grade": "Professeur"
    }
  }
}
```

## ✅ Checklist d'Intégration

- [ ] AuthProvider ajouté dans layout.tsx
- [ ] suppressHydrationWarning ajouté
- [ ] UserMenu ajouté dans Navbar
- [ ] Routes protégées avec useAuth
- [ ] Page de login accessible
- [ ] Redirection après login fonctionne
- [ ] Déconnexion fonctionne
- [ ] Token persisté dans localStorage
- [ ] Design responsive testé
- [ ] Comptes de test fonctionnent

---

**Version:** 1.0.0
**Date:** 2026-05-24
**Status:** ✅ Prêt à intégrer
