#!/usr/bin/env python3
"""
Script d'analyse de facture pour comprendre la structure
et identifier les lignes de facturation
"""

import os
import base64
from mistralai import Mistral, DocumentURLChunk
from mistralai.extra import response_format_from_pydantic_model
from pydantic import BaseModel, Field
from typing import List, Optional
import json

# Configuration du client Mistral
api_key = os.environ["MISTRAL_API_KEY"]
client = Mistral(api_key=api_key)

# Modèle Pydantic pour l'analyse de facture
class InvoiceAnalysis(BaseModel):
    """Modèle pour analyser la structure d'une facture"""
    document_type: str = Field(..., description="Type de document (facture, devis, etc.)")
    vendor_name: str = Field(..., description="Nom du vendeur/fournisseur")
    invoice_number: str = Field(..., description="Numéro de facture")
    invoice_date: str = Field(..., description="Date de facturation")
    customer_name: str = Field(..., description="Nom du client")
    total_amount: float = Field(..., description="Montant total de la facture")
    currency: str = Field(..., description="Devise utilisée")
    table_structure: str = Field(..., description="Description de la structure du tableau des lignes")
    columns_identified: List[str] = Field(..., description="Colonnes identifiées dans le tableau")
    sample_lines: List[str] = Field(..., description="Exemples de lignes de facturation trouvées")

def encode_pdf_to_base64(pdf_path: str) -> str:
    """Encode un fichier PDF en base64"""
    with open(pdf_path, "rb") as pdf_file:
        return base64.b64encode(pdf_file.read()).decode('utf-8')

def analyze_invoice_structure(pdf_path: str) -> dict:
    """Analyse la structure d'une facture avec OCR Mistral"""
    
    print("🔍 Analyse de la structure de la facture...")
    
    # Encodage du PDF en base64
    base64_pdf = encode_pdf_to_base64(pdf_path)
    
    # Création du format de réponse
    response_format = response_format_from_pydantic_model(InvoiceAnalysis)
    
    # Appel OCR avec annotations
    response = client.ocr.process(
        model="mistral-ocr-latest",
        document=DocumentURLChunk(
            document_url=f"data:application/pdf;base64,{base64_pdf}"
        ),
        document_annotation_format=response_format
    )
    
    return response.document_annotation

def extract_raw_text(pdf_path: str) -> str:
    """Extrait le texte brut de la facture pour analyse manuelle"""
    
    print("📄 Extraction du texte brut...")
    
    # Encodage du PDF en base64
    base64_pdf = encode_pdf_to_base64(pdf_path)
    
    # Appel OCR simple pour obtenir le texte
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
    
    print("🚀 Démarrage de l'analyse de facture...")
    print(f"📁 Fichier analysé: {pdf_path}")
    
    try:
        # Analyse structurée
        print("\n1️⃣ Analyse structurée avec annotations...")
        analysis = analyze_invoice_structure(pdf_path)
        
        print("\n📊 Résultats de l'analyse structurée:")
        print(json.dumps(analysis.dict(), indent=2, ensure_ascii=False))
        
        # Extraction du texte brut
        print("\n2️⃣ Extraction du texte brut...")
        raw_text = extract_raw_text(pdf_path)
        
        # Sauvegarder le texte brut pour analyse
        with open("invoice_text.txt", "w", encoding="utf-8") as f:
            f.write(raw_text)
        
        print(f"\n✅ Texte brut sauvegardé dans 'invoice_text.txt'")
        print(f"📏 Longueur du texte: {len(raw_text)} caractères")
        
        # Afficher un aperçu du texte
        print("\n📋 Aperçu du texte extrait:")
        print("=" * 50)
        print(raw_text[:1000] + "..." if len(raw_text) > 1000 else raw_text)
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Erreur lors de l'analyse: {e}")
        import traceback
        traceback.print_exc() 