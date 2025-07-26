import os
import sys
from pathlib import Path
from mistralai import Mistral

# Ajout du répertoire src au path pour les imports
sys.path.append(str(Path(__file__).parent.parent))

from core.security import validate_api_key
from config.settings import settings

# Supprimer la clé système pour éviter les conflits
if 'MISTRAL_API_KEY' in os.environ:
    del os.environ['MISTRAL_API_KEY']

# Recharger les settings depuis le .env
try:
    from dotenv import load_dotenv
    load_dotenv(override=True)
except ImportError:
    pass

class MistralClient:
    """Client Mistral configuré avec validation de sécurité"""
    
    def __init__(self):
        # Utiliser uniquement la clé du .env
        self.api_key = os.getenv("MISTRAL_API_KEY", "")
        if not self.api_key:
            raise ValueError("Clé API Mistral non trouvée dans le fichier .env")
        
        validate_api_key(self.api_key)
        self.client = Mistral(api_key=self.api_key)
        self.model = settings.MISTRAL_MODEL
    
    def get_client(self) -> Mistral:
        """Retourne le client Mistral configuré"""
        return self.client
    
    def get_model(self) -> str:
        """Retourne le modèle OCR configuré"""
        return self.model
    
    def is_configured(self) -> bool:
        """Vérifie si le client est correctement configuré"""
        return bool(self.api_key and len(self.api_key) > 10)

# Instance globale du client
mistral_client = MistralClient() 