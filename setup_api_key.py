#!/usr/bin/env python3
"""
Script pour configurer la clé API Mistral
"""

import os
from pathlib import Path

def setup_api_key():
    """Configure la clé API Mistral"""
    
    print("🔧 Configuration de la clé API Mistral")
    print("=" * 50)
    
    # Vérifier si la clé est déjà définie
    current_key = os.environ.get('MISTRAL_API_KEY')
    if current_key:
        print(f"⚠️  Clé API actuelle: {current_key[:8]}...")
        print("Cette clé semble invalide (erreur 401).")
    else:
        print("✅ Aucune clé API définie dans l'environnement.")
    
    print("\n📝 Instructions pour configurer la bonne clé API:")
    print("1. Allez sur https://console.mistral.ai/")
    print("2. Connectez-vous à votre compte")
    print("3. Allez dans 'API Keys'")
    print("4. Créez une nouvelle clé API ou copiez une existante")
    print("5. La clé commence généralement par 'mist-'")
    
    print("\n🔑 Entrez votre clé API Mistral (ou appuyez sur Entrée pour passer):")
    api_key = input("Clé API: ").strip()
    
    if api_key:
        # Créer le fichier .env
        env_content = f"""# Configuration Mistral AI OCR
MISTRAL_API_KEY={api_key}

# Configuration de l'application
ENVIRONMENT=development
LOG_LEVEL=INFO
"""
        
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print(f"\n✅ Fichier .env créé avec la clé API")
        print(f"🔑 Clé enregistrée: {api_key[:8]}...")
        
        # Tester la clé
        print("\n🧪 Test de la clé API...")
        os.environ['MISTRAL_API_KEY'] = api_key
        
        # Importer et tester le client Mistral
        try:
            from mistralai import Mistral
            client = Mistral(api_key=api_key)
            print("✅ Client Mistral initialisé avec succès!")
            print("✅ La clé API semble valide!")
        except Exception as e:
            print(f"❌ Erreur lors du test: {e}")
            print("⚠️  Vérifiez que votre clé API est correcte")
    
    else:
        print("\n📋 Pour configurer manuellement:")
        print("1. Créez un fichier .env à la racine du projet")
        print("2. Ajoutez: MISTRAL_API_KEY=votre_clé_ici")
        print("3. Relancez ce script pour tester")

if __name__ == "__main__":
    setup_api_key() 