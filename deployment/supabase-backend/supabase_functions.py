#!/usr/bin/env python3
"""
Supabase Edge Functions pour l'extraction de factures
Alternative au backend Vercel pour plus de contrôle
"""

import os
import json
import base64
from typing import Dict, Any
from supabase import create_client, Client
from mistralai import Mistral
from mistralai.models.chat_completion import ChatMessage
import tempfile
from pathlib import Path

# Configuration Supabase
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_ANON_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

# Configuration Mistral
mistral_client = Mistral(api_key=os.environ.get("MISTRAL_API_KEY"))

def process_invoice(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fonction Edge pour traiter une facture
    """
    try:
        # Récupérer les données de la requête
        body = event.get('body', {})
        if isinstance(body, str):
            body = json.loads(body)
        
        file_data = body.get('file_data')  # Base64
        file_name = body.get('file_name')
        action_type = body.get('action_type', 'extract')
        
        if not file_data or not file_name:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Données de fichier manquantes'})
            }
        
        # Décoder le fichier
        file_bytes = base64.b64decode(file_data)
        
        # Sauvegarder temporairement
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            temp_file.write(file_bytes)
            temp_path = temp_file.name
        
        try:
            # Traiter selon l'action
            if action_type == 'extract':
                result = extract_invoice_lines(temp_path)
            elif action_type == 'analyze':
                result = analyze_invoice_structure(temp_path)
            elif action_type == 'raw_text':
                result = extract_raw_text(temp_path)
            elif action_type == 'annotations':
                result = detect_annotations(temp_path)
            else:
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': 'Type d\'action non reconnu'})
                }
            
            # Sauvegarder dans Supabase
            save_to_database(result, file_name, action_type)
            
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'success': True,
                    'data': result,
                    'action_type': action_type
                })
            }
            
        finally:
            # Nettoyer le fichier temporaire
            if os.path.exists(temp_path):
                os.unlink(temp_path)
                
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def extract_invoice_lines(file_path: str) -> Dict[str, Any]:
    """Extrait les lignes de facturation"""
    # Implémentation de l'extraction
    # Utilise le même code que votre application locale
    pass

def analyze_invoice_structure(file_path: str) -> Dict[str, Any]:
    """Analyse la structure de la facture"""
    # Implémentation de l'analyse
    pass

def extract_raw_text(file_path: str) -> Dict[str, Any]:
    """Extrait le texte brut"""
    # Implémentation de l'extraction de texte
    pass

def detect_annotations(file_path: str) -> Dict[str, Any]:
    """Détecte les annotations manuscrites"""
    # Implémentation de la détection d'annotations
    pass

def save_to_database(result: Dict[str, Any], file_name: str, action_type: str):
    """Sauvegarde le résultat dans Supabase"""
    try:
        data = {
            'file_name': file_name,
            'action_type': action_type,
            'result': json.dumps(result),
            'created_at': 'now()'
        }
        
        supabase.table('invoice_analyses').insert(data).execute()
        
    except Exception as e:
        print(f"Erreur lors de la sauvegarde: {e}")

def get_analysis_history(event: Dict[str, Any]) -> Dict[str, Any]:
    """Récupère l'historique des analyses"""
    try:
        # Récupérer les analyses récentes
        response = supabase.table('invoice_analyses').select('*').order('created_at', desc=True).limit(10).execute()
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'success': True,
                'data': response.data
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        } 