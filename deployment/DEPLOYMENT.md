# 🚀 Guide de Déploiement - Extracteur de Factures

## 📋 Vue d'ensemble

Ce guide vous explique comment déployer votre application d'extraction de factures sur internet en utilisant **Vercel** et **Supabase**.

## 🏗️ Architecture Recommandée

### Option 1 : Vercel Full-Stack (Recommandée)
```
Frontend (Vercel) + Backend (Vercel Functions) + Base de données (Supabase)
```

### Option 2 : Vercel + Supabase Edge Functions
```
Frontend (Vercel) + Backend (Supabase Edge Functions) + Base de données (Supabase)
```

## 🎯 Option 1 : Déploiement Vercel Full-Stack

### 1. Préparation du projet

```bash
# Cloner votre repository
git clone https://github.com/Lofp34/Analyse_Factures.git
cd Analyse_Factures

# Copier les fichiers de déploiement
cp -r deployment/vercel-frontend/* .
```

### 2. Configuration Vercel

1. **Installer Vercel CLI :**
```bash
npm i -g vercel
```

2. **Se connecter à Vercel :**
```bash
vercel login
```

3. **Configurer les variables d'environnement :**
```bash
vercel env add MISTRAL_API_KEY
# Entrez votre clé API Mistral
```

### 3. Déploiement

```bash
# Déployer
vercel --prod

# Ou pour un déploiement automatique
vercel
```

### 4. Configuration du domaine

- Allez sur [vercel.com](https://vercel.com)
- Sélectionnez votre projet
- Configurez votre domaine personnalisé

## 🎯 Option 2 : Vercel + Supabase Edge Functions

### 1. Configuration Supabase

1. **Créer un projet Supabase :**
   - Allez sur [supabase.com](https://supabase.com)
   - Créez un nouveau projet
   - Notez l'URL et les clés API

2. **Créer la table de base de données :**
```sql
-- Table pour stocker les analyses
CREATE TABLE invoice_analyses (
  id SERIAL PRIMARY KEY,
  file_name TEXT NOT NULL,
  action_type TEXT NOT NULL,
  result JSONB NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Politique RLS (Row Level Security)
ALTER TABLE invoice_analyses ENABLE ROW LEVEL SECURITY;

-- Permettre l'insertion pour les utilisateurs authentifiés
CREATE POLICY "Users can insert their own analyses" ON invoice_analyses
  FOR INSERT WITH CHECK (auth.uid() IS NOT NULL);

-- Permettre la lecture pour les utilisateurs authentifiés
CREATE POLICY "Users can view their own analyses" ON invoice_analyses
  FOR SELECT USING (auth.uid() IS NOT NULL);
```

3. **Déployer les Edge Functions :**
```bash
# Installer Supabase CLI
npm install -g supabase

# Se connecter
supabase login

# Lier le projet
supabase link --project-ref YOUR_PROJECT_REF

# Déployer les fonctions
supabase functions deploy process_invoice
supabase functions deploy get_analysis_history
```

### 2. Configuration Frontend Vercel

1. **Modifier l'API endpoint dans le frontend :**
```javascript
// Dans index.html, changer l'URL de l'API
const response = await fetch('https://YOUR_SUPABASE_URL.functions.supabase.co/process_invoice', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${SUPABASE_ANON_KEY}`
  },
  body: JSON.stringify({
    file_data: base64Data,
    file_name: fileName,
    action_type: selectedAction
  })
});
```

2. **Configurer les variables d'environnement Vercel :**
```bash
vercel env add SUPABASE_URL
vercel env add SUPABASE_ANON_KEY
vercel env add MISTRAL_API_KEY
```

## 🔧 Configuration Avancée

### Variables d'environnement requises

```bash
# Mistral AI
MISTRAL_API_KEY=your_mistral_api_key

# Supabase (si utilisé)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key

# Vercel (optionnel)
VERCEL_PROJECT_ID=your_project_id
VERCEL_TEAM_ID=your_team_id
```

### Optimisations de performance

1. **Limiter la taille des fichiers :**
```python
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB
```

2. **Timeout des fonctions :**
```json
{
  "functions": {
    "app.py": {
      "maxDuration": 60
    }
  }
}
```

3. **Mise en cache :**
```python
# Ajouter des headers de cache
@app.after_request
def add_cache_headers(response):
    response.headers['Cache-Control'] = 'public, max-age=300'
    return response
```

## 🛡️ Sécurité

### Protection des données

1. **Validation des fichiers :**
```python
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
```

2. **Nettoyage des fichiers temporaires :**
```python
try:
    # Traitement
    pass
finally:
    if os.path.exists(temp_path):
        os.unlink(temp_path)
```

3. **Rate limiting :**
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
```

### Authentification (optionnel)

1. **Supabase Auth :**
```javascript
// Dans le frontend
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY)

// Authentification
const { user, error } = await supabase.auth.signIn({
  email: 'user@example.com',
  password: 'password'
})
```

## 📊 Monitoring et Analytics

### Vercel Analytics

```bash
# Installer Vercel Analytics
npm install @vercel/analytics

# Dans votre app
import { Analytics } from '@vercel/analytics/react'

function App() {
  return (
    <>
      <YourApp />
      <Analytics />
    </>
  )
}
```

### Logs et Debugging

1. **Vercel Logs :**
```bash
vercel logs your-project-name
```

2. **Supabase Logs :**
```bash
supabase logs --project-ref YOUR_PROJECT_REF
```

## 🚀 Déploiement Automatique

### GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy to Vercel

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v20
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.ORG_ID }}
          vercel-project-id: ${{ secrets.PROJECT_ID }}
          vercel-args: '--prod'
```

## 💰 Coûts Estimés

### Vercel
- **Hobby** : Gratuit (100GB bandwidth/mois)
- **Pro** : $20/mois (1TB bandwidth/mois)
- **Enterprise** : Sur mesure

### Supabase
- **Free** : Gratuit (500MB base de données)
- **Pro** : $25/mois (8GB base de données)
- **Team** : $599/mois

### Mistral AI
- **OCR** : ~$0.01-0.05 par document
- **API calls** : Variables selon l'usage

## 🆘 Dépannage

### Erreurs courantes

1. **Timeout des fonctions :**
   - Augmenter `maxDuration` dans `vercel.json`
   - Optimiser le code de traitement

2. **Erreur de mémoire :**
   - Réduire la taille des fichiers
   - Optimiser les algorithmes

3. **Erreur d'authentification :**
   - Vérifier les variables d'environnement
   - Contrôler les clés API

### Support

- **Vercel** : [vercel.com/support](https://vercel.com/support)
- **Supabase** : [supabase.com/support](https://supabase.com/support)
- **Mistral AI** : [mistral.ai/support](https://mistral.ai/support)

---

**🎉 Votre application est maintenant prête pour le déploiement !** 