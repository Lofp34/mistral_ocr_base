#!/usr/bin/env python3
"""
Script simple pour extraire le texte de la facture
"""

import os
import base64
from mistralai import Mistral, DocumentURLChunk

# Configuration du client Mistral
api_key = os.environ["MISTRAL_API_KEY"]
client = Mistral(api_key=api_key)

def encode_pdf_to_base64(pdf_path: str) -> str:
    """Encode un fichier PDF en base64"""
    with open(pdf_path, "rb") as pdf_file:
        return base64.b64encode(pdf_file.read()).decode('utf-8')

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extrait le texte d'un PDF avec OCR Mistral"""
    
    print("📄 Extraction du texte de la facture...")
    
    # Encodage du PDF en base64
    base64_pdf = encode_pdf_to_base64(pdf_path)
    
    # Appel OCR simple
    response = client.ocr.process(
        model="mistral-ocr-latest",
        document=DocumentURLChunk(
            document_url=f"data:application/pdf;base64,{base64_pdf}"
        )
    )
    
    # Concaténer le texte de toutes les pages
    full_text = ""
    for page in response.pages:
        if hasattr(page, 'text'):
            full_text += page.text + "\n"
    
    return full_text

if __name__ == "__main__":
    pdf_path = "document.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"❌ Erreur: Le fichier {pdf_path} n'existe pas")
        exit(1)
    
    print("🚀 Démarrage de l'extraction de texte...")
    print(f"📁 Fichier analysé: {pdf_path}")
    print(f"🔑 API Key: {'Définie' if api_key else 'Non définie'}")
    
    try:
        # Extraction du texte
        raw_text = extract_text_from_pdf(pdf_path)
        
        # Sauvegarder le texte
        with open("invoice_text.txt", "w", encoding="utf-8") as f:
            f.write(raw_text)
        
        print(f"\n✅ Texte extrait et sauvegardé dans 'invoice_text.txt'")
        print(f"📏 Longueur du texte: {len(raw_text)} caractères")
        
        # Afficher un aperçu du texte
        print("\n📋 Aperçu du texte extrait:")
        print("=" * 50)
        print(raw_text[:2000] + "..." if len(raw_text) > 2000 else raw_text)
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Erreur lors de l'extraction: {e}")
        import traceback
        traceback.print_exc() 