#!/usr/bin/env python3
"""
Application Flask pour déploiement Vercel
Interface web pour l'extraction de factures
"""

import os
import json
import base64
from flask import Flask, request, jsonify, render_template, send_file
from werkzeug.utils import secure_filename
import tempfile
from pathlib import Path
import sys

# Ajout du répertoire parent au path pour les imports
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))

from services.invoice_extractor import InvoiceExtractor
from utils.file_utils import validate_file_format

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max

# Configuration
UPLOAD_FOLDER = '/tmp'
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'pptx'}

def allowed_file(filename):
    """Vérifie si le fichier est autorisé"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Page d'accueil"""
    return render_template('index.html')

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """API pour upload et traitement de fichiers"""
    try:
        # Vérifier si un fichier a été envoyé
        if 'file' not in request.files:
            return jsonify({'error': 'Aucun fichier sélectionné'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Aucun fichier sélectionné'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Format de fichier non supporté'}), 400
        
        # Récupérer les options de traitement
        action_type = request.form.get('action_type', 'extract')
        
        # Sauvegarder le fichier temporairement
        filename = secure_filename(file.filename)
        temp_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(temp_path)
        
        try:
            # Initialiser l'extracteur
            extractor = InvoiceExtractor()
            
            # Traiter selon l'action demandée
            if action_type == 'extract':
                result = extractor.extract_invoice_lines(temp_path)
            elif action_type == 'analyze':
                result = extractor.analyze_invoice_structure(temp_path)
            elif action_type == 'raw_text':
                raw_text = extractor.extract_raw_text(temp_path)
                result = {
                    'success': True,
                    'raw_text': raw_text,
                    'processing_time': 0,
                    'confidence_score': 0.9
                }
            elif action_type == 'annotations':
                result = extractor.detect_annotations_via_qna(temp_path)
            else:
                return jsonify({'error': 'Type d\'action non reconnu'}), 400
            
            # Nettoyer le fichier temporaire
            os.unlink(temp_path)
            
            # Retourner le résultat
            if result.success:
                return jsonify({
                    'success': True,
                    'data': result.model_dump() if hasattr(result, 'model_dump') else result.dict(),
                    'action_type': action_type
                })
            else:
                return jsonify({
                    'success': False,
                    'error': result.error_message
                }), 400
                
        except Exception as e:
            # Nettoyer en cas d'erreur
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            raise e
            
    except Exception as e:
        return jsonify({'error': f'Erreur lors du traitement: {str(e)}'}), 500

@app.route('/api/health')
def health_check():
    """Vérification de santé de l'API"""
    return jsonify({
        'status': 'healthy',
        'service': 'Invoice Extractor API',
        'version': '1.0.0'
    })

@app.errorhandler(413)
def too_large(e):
    """Gestion des fichiers trop volumineux"""
    return jsonify({'error': 'Fichier trop volumineux (max 50MB)'}), 413

@app.errorhandler(500)
def internal_error(e):
    """Gestion des erreurs internes"""
    return jsonify({'error': 'Erreur interne du serveur'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080))) 