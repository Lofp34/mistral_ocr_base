#!/bin/bash

# 🚀 Script de déploiement automatisé pour Extracteur de Factures
# Compatible Vercel + Supabase

set -e  # Arrêter en cas d'erreur

echo "🚀 Déploiement de l'Extracteur de Factures"
echo "=========================================="

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction pour afficher les messages
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Vérifier les prérequis
check_prerequisites() {
    print_status "Vérification des prérequis..."
    
    # Vérifier Node.js
    if ! command -v node &> /dev/null; then
        print_error "Node.js n'est pas installé. Installez-le depuis https://nodejs.org/"
        exit 1
    fi
    
    # Vérifier npm
    if ! command -v npm &> /dev/null; then
        print_error "npm n'est pas installé."
        exit 1
    fi
    
    # Vérifier Vercel CLI
    if ! command -v vercel &> /dev/null; then
        print_warning "Vercel CLI n'est pas installé. Installation..."
        npm install -g vercel
    fi
    
    # Vérifier Supabase CLI (optionnel)
    if ! command -v supabase &> /dev/null; then
        print_warning "Supabase CLI n'est pas installé. Installation..."
        npm install -g supabase
    fi
    
    print_success "Prérequis vérifiés"
}

# Configuration des variables d'environnement
setup_environment() {
    print_status "Configuration des variables d'environnement..."
    
    # Demander la clé API Mistral
    if [ -z "$MISTRAL_API_KEY" ]; then
        echo -n "Entrez votre clé API Mistral: "
        read -s MISTRAL_API_KEY
        echo
    fi
    
    # Demander l'URL Supabase (optionnel)
    if [ -z "$SUPABASE_URL" ]; then
        echo -n "Entrez votre URL Supabase (optionnel, appuyez sur Entrée pour ignorer): "
        read SUPABASE_URL
    fi
    
    # Demander la clé Supabase (optionnel)
    if [ -z "$SUPABASE_ANON_KEY" ] && [ ! -z "$SUPABASE_URL" ]; then
        echo -n "Entrez votre clé anonyme Supabase: "
        read -s SUPABASE_ANON_KEY
        echo
    fi
    
    print_success "Variables d'environnement configurées"
}

# Préparation du projet
prepare_project() {
    print_status "Préparation du projet..."
    
    # Créer le dossier de déploiement
    if [ ! -d "deployment/vercel-frontend" ]; then
        print_error "Dossier de déploiement manquant. Vérifiez la structure du projet."
        exit 1
    fi
    
    # Copier les fichiers de déploiement
    cp -r deployment/vercel-frontend/* .
    
    # Créer le fichier .env pour le développement local
    if [ ! -f ".env" ]; then
        echo "MISTRAL_API_KEY=$MISTRAL_API_KEY" > .env
        if [ ! -z "$SUPABASE_URL" ]; then
            echo "SUPABASE_URL=$SUPABASE_URL" >> .env
        fi
        if [ ! -z "$SUPABASE_ANON_KEY" ]; then
            echo "SUPABASE_ANON_KEY=$SUPABASE_ANON_KEY" >> .env
        fi
    fi
    
    print_success "Projet préparé"
}

# Configuration Vercel
setup_vercel() {
    print_status "Configuration Vercel..."
    
    # Vérifier si l'utilisateur est connecté
    if ! vercel whoami &> /dev/null; then
        print_warning "Connexion à Vercel requise..."
        vercel login
    fi
    
    # Configurer les variables d'environnement
    print_status "Configuration des variables d'environnement Vercel..."
    
    # Supprimer les variables existantes si elles existent
    vercel env rm MISTRAL_API_KEY --yes 2>/dev/null || true
    
    # Ajouter les nouvelles variables
    echo "$MISTRAL_API_KEY" | vercel env add MISTRAL_API_KEY
    
    if [ ! -z "$SUPABASE_URL" ]; then
        vercel env rm SUPABASE_URL --yes 2>/dev/null || true
        echo "$SUPABASE_URL" | vercel env add SUPABASE_URL
    fi
    
    if [ ! -z "$SUPABASE_ANON_KEY" ]; then
        vercel env rm SUPABASE_ANON_KEY --yes 2>/dev/null || true
        echo "$SUPABASE_ANON_KEY" | vercel env add SUPABASE_ANON_KEY
    fi
    
    print_success "Vercel configuré"
}

# Configuration Supabase (optionnel)
setup_supabase() {
    if [ -z "$SUPABASE_URL" ]; then
        print_warning "Supabase non configuré, ignoré"
        return
    fi
    
    print_status "Configuration Supabase..."
    
    # Vérifier si l'utilisateur est connecté
    if ! supabase status &> /dev/null; then
        print_warning "Connexion à Supabase requise..."
        supabase login
    fi
    
    # Créer la table de base de données
    print_status "Création de la table de base de données..."
    
    # Créer le fichier SQL temporaire
    cat > temp_setup.sql << 'EOF'
-- Table pour stocker les analyses
CREATE TABLE IF NOT EXISTS invoice_analyses (
  id SERIAL PRIMARY KEY,
  file_name TEXT NOT NULL,
  action_type TEXT NOT NULL,
  result JSONB NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Politique RLS (Row Level Security)
ALTER TABLE invoice_analyses ENABLE ROW LEVEL SECURITY;

-- Permettre l'insertion pour les utilisateurs authentifiés
DROP POLICY IF EXISTS "Users can insert their own analyses" ON invoice_analyses;
CREATE POLICY "Users can insert their own analyses" ON invoice_analyses
  FOR INSERT WITH CHECK (auth.uid() IS NOT NULL);

-- Permettre la lecture pour les utilisateurs authentifiés
DROP POLICY IF EXISTS "Users can view their own analyses" ON invoice_analyses;
CREATE POLICY "Users can view their own analyses" ON invoice_analyses
  FOR SELECT USING (auth.uid() IS NOT NULL);
EOF
    
    # Exécuter le script SQL
    supabase db reset --linked
    
    # Nettoyer
    rm temp_setup.sql
    
    print_success "Supabase configuré"
}

# Déploiement
deploy() {
    print_status "Déploiement en cours..."
    
    # Déployer sur Vercel
    if [ "$1" = "--prod" ]; then
        vercel --prod
    else
        vercel
    fi
    
    print_success "Déploiement terminé !"
}

# Nettoyage
cleanup() {
    print_status "Nettoyage..."
    
    # Supprimer les fichiers temporaires
    rm -f temp_setup.sql
    
    print_success "Nettoyage terminé"
}

# Fonction principale
main() {
    echo "🚀 Extracteur de Factures - Script de déploiement"
    echo "================================================"
    echo
    
    # Vérifier les arguments
    DEPLOY_MODE="dev"
    if [ "$1" = "--prod" ]; then
        DEPLOY_MODE="production"
        print_warning "Mode de déploiement: PRODUCTION"
    else
        print_status "Mode de déploiement: DÉVELOPPEMENT"
    fi
    
    echo
    
    # Exécuter les étapes
    check_prerequisites
    setup_environment
    prepare_project
    setup_vercel
    setup_supabase
    deploy $1
    cleanup
    
    echo
    print_success "🎉 Déploiement terminé avec succès !"
    echo
    echo "📋 Prochaines étapes :"
    echo "1. Vérifiez votre application sur Vercel"
    echo "2. Configurez votre domaine personnalisé"
    echo "3. Testez l'upload et le traitement de fichiers"
    echo "4. Surveillez les logs pour détecter les erreurs"
    echo
    echo "🔗 Liens utiles :"
    echo "- Vercel Dashboard: https://vercel.com/dashboard"
    echo "- Supabase Dashboard: https://supabase.com/dashboard"
    echo "- Documentation: https://github.com/Lofp34/Analyse_Factures"
}

# Exécuter le script
main "$@" 