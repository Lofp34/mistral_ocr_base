import os
import re
from urllib.parse import urlparse
from typing import List

def validate_api_key(api_key: str) -> bool:
    """Valide une API key Mistral"""
    if not api_key or len(api_key) < 10:
        raise ValueError("API key invalide - doit contenir au moins 10 caractères")
    return True

def validate_document_url(url: str) -> bool:
    """Valide une URL de document"""
    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError("URL invalide")
        
        # Vérifier les domaines autorisés si nécessaire
        allowed_domains = ["example.com", "trusted-domain.com"]
        if parsed.netloc not in allowed_domains:
            raise ValueError(f"Domaine non autorisé: {parsed.netloc}")
            
        return True
    except Exception as e:
        raise ValueError(f"Erreur de validation URL: {e}")

def validate_file_security(file_path: str, max_size_mb: int = 50) -> bool:
    """Valide la sécurité d'un fichier"""
    # Vérifier l'existence
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Fichier non trouvé: {file_path}")
    
    # Vérifier la taille
    file_size = os.path.getsize(file_path)
    if file_size > max_size_mb * 1024 * 1024:
        raise ValueError(f"Fichier trop volumineux: {file_size / (1024*1024):.2f}MB")
    
    # Vérifier l'extension
    allowed_extensions = ['.pdf', '.docx', '.pptx', '.png', '.jpg', '.jpeg', '.avif']
    file_extension = os.path.splitext(file_path)[1].lower()
    if file_extension not in allowed_extensions:
        raise ValueError(f"Format de fichier non autorisé: {file_extension}")
    
    return True

def sanitize_response_data(response_data: dict) -> dict:
    """Nettoie les données de réponse des informations sensibles"""
    if isinstance(response_data, dict):
        sanitized = {}
        for key, value in response_data.items():
            if key.lower() in ['api_key', 'token', 'password', 'secret']:
                sanitized[key] = '***REDACTED***'
            elif isinstance(value, (dict, list)):
                sanitized[key] = sanitize_response_data(value)
            else:
                sanitized[key] = value
        return sanitized
    elif isinstance(response_data, list):
        return [sanitize_response_data(item) for item in response_data]
    else:
        return response_data 