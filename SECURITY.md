# 🔒 Guide de Sécurité

## ⚠️ IMPORTANT : Protection des Données Sensibles

### 🚨 Fichiers à NE JAMAIS commiter

- **`.env`** - Contient votre clé API Mistral
- **`*.pdf`** - Documents clients (données personnelles)
- **`*.docx`, `*.pptx`** - Documents sensibles
- **`api_keys.txt`** - Clés API
- **`secrets.json`** - Fichiers de secrets
- **`config.json`** - Configuration avec secrets

### ✅ Configuration Sécurisée

1. **Créer votre fichier `.env` :**
   ```bash
   cp env_template.txt .env
   ```

2. **Ajouter votre clé API :**
   ```bash
   echo "MISTRAL_API_KEY=votre_clé_api_ici" >> .env
   ```

3. **Vérifier que `.env` est ignoré :**
   ```bash
   git status
   # Le fichier .env ne doit PAS apparaître
   ```

### 🛡️ Bonnes Pratiques

- ✅ Utilisez toujours des variables d'environnement pour les secrets
- ✅ Vérifiez le `.gitignore` avant chaque commit
- ✅ Testez avec `git status` pour voir ce qui sera commité
- ✅ Utilisez `git add .` avec précaution
- ✅ Vérifiez l'historique Git : `git log --oneline`

### 🔍 Vérification de Sécurité

```bash
# Vérifier ce qui sera commité
git status

# Vérifier l'historique pour les secrets
git log --oneline

# Vérifier le .gitignore
cat .gitignore
```

### 🚨 En Cas d'Exposition

Si une clé API a été exposée :

1. **Révoquer immédiatement la clé** sur le dashboard Mistral
2. **Générer une nouvelle clé**
3. **Mettre à jour le fichier `.env` local**
4. **Vérifier l'historique Git** pour d'autres expositions

### 📋 Checklist de Sécurité

- [ ] `.env` est dans `.gitignore`
- [ ] Aucun fichier PDF dans le repository
- [ ] Aucune clé API dans le code
- [ ] `git status` ne montre pas de fichiers sensibles
- [ ] Le `.gitignore` est à jour

---

**⚠️ RÈGLE D'OR : Si vous avez un doute, ne commitez pas !** 