#!/usr/bin/env python3
"""
Application principale pour l'extraction de lignes de facturation
"""

import sys
import json
import argparse
from pathlib import Path

# Ajout du répertoire src au path
sys.path.append(str(Path(__file__).parent))

from services.invoice_extractor import InvoiceExtractor
from utils.file_utils import create_output_directory, get_file_info
from config.settings import settings

def main():
    """Fonction principale de l'application"""
    
    parser = argparse.ArgumentParser(description="Extracteur de lignes de facturation avec OCR Mistral")
    parser.add_argument("pdf_path", help="Chemin vers le fichier PDF de facture")
    parser.add_argument("--output", "-o", default="data/output", help="Répertoire de sortie")
    parser.add_argument("--analyze", "-a", action="store_true", help="Analyser la structure de la facture")
    parser.add_argument("--raw-text", "-r", action="store_true", help="Extraire le texte brut")
    parser.add_argument("--annotations", "-n", action="store_true", help="Détecter les annotations manuscrites avec QnA")
    
    args = parser.parse_args()
    
    print("🚀 Extracteur de Lignes de Facturation - Mistral OCR")
    print("=" * 60)
    
    # Vérification du fichier
    if not Path(args.pdf_path).exists():
        print(f"❌ Erreur: Le fichier {args.pdf_path} n'existe pas")
        sys.exit(1)
    
    # Informations sur le fichier
    file_info = get_file_info(args.pdf_path)
    print(f"📁 Fichier: {file_info['name']}")
    print(f"📏 Taille: {file_info['size_mb']:.2f} MB")
    print(f"📄 Format: {file_info['extension']}")
    
    # Création du répertoire de sortie
    output_dir = create_output_directory(args.output)
    print(f"📂 Sortie: {output_dir}")
    
    # Initialisation de l'extracteur
    try:
        extractor = InvoiceExtractor()
        print("✅ Extracteur initialisé avec succès")
    except Exception as e:
        print(f"❌ Erreur d'initialisation: {e}")
        sys.exit(1)
    
    # Traitement selon les options
    if args.analyze:
        print("\n🔍 Analyse de la structure de la facture...")
        result = extractor.analyze_invoice_structure(args.pdf_path)
        
        if result.success:
            print("✅ Analyse réussie!")
            output_file = Path(output_dir) / f"{Path(args.pdf_path).stem}_analysis.json"
            extractor.save_extraction_result(result, str(output_file))
            print(f"📄 Résultats sauvegardés dans: {output_file}")
            
            # Affichage des résultats
            print("\n📊 Résultats de l'analyse:")
            print(json.dumps(result.model_dump(), indent=2, ensure_ascii=False))
        else:
            print(f"❌ Erreur d'analyse: {result.error_message}")
    
    elif args.raw_text:
        print("\n📄 Extraction du texte brut...")
        try:
            raw_text = extractor.extract_raw_text(args.pdf_path)
            output_file = Path(output_dir) / f"{Path(args.pdf_path).stem}_text.txt"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(raw_text)
            
            print(f"✅ Texte extrait et sauvegardé dans: {output_file}")
            print(f"📏 Longueur: {len(raw_text)} caractères")
            
            # Aperçu du texte
            print("\n📋 Aperçu du texte:")
            print("-" * 40)
            print(raw_text[:500] + "..." if len(raw_text) > 500 else raw_text)
            print("-" * 40)
            
        except Exception as e:
            print(f"❌ Erreur d'extraction: {e}")
    
    elif args.annotations:
        print("\n🤖 Détection d'annotations manuscrites via Document QnA...")
        result = extractor.detect_annotations_via_qna(args.pdf_path)
        
        if result.success:
            print("✅ Détection QnA réussie!")
            output_file = Path(output_dir) / f"{Path(args.pdf_path).stem}_annotations_qna.json"
            extractor.save_extraction_result(result, str(output_file))
            print(f"📄 Résultats sauvegardés dans: {output_file}")
            
            # Affichage des résultats
            print("\n📊 Résultats de la détection QnA:")
            print(f"⏱️  Temps de traitement: {result.processing_time:.2f}s")
            print(f"🎯 Score de confiance: {result.confidence_score:.2%}")
            print(f"🔍 Méthode: {result.invoice_data.detection_method}")
            print(f"✍️  Annotations détectées: {result.invoice_data.annotations_detected}")
            
            if result.invoice_data.handwritten_annotations:
                print("\n✍️  Annotations manuscrites détectées:")
                for i, annotation in enumerate(result.invoice_data.handwritten_annotations, 1):
                    print(f"  {i}. [{annotation.annotation_type.upper()}] {annotation.text}")
                    if annotation.payment_date:
                        print(f"     📅 Date de paiement: {annotation.payment_date}")
                    if annotation.purchase_purpose:
                        print(f"     🎯 Objectif: {annotation.purchase_purpose}")
                    print(f"     🎯 Confiance: {annotation.confidence:.1%}")
            else:
                print("\n✍️  Aucune annotation manuscrite détectée")
            
            print(f"\n❓ Questions posées:")
            for i, question in enumerate(result.invoice_data.questions_asked, 1):
                print(f"  {i}. {question}")
        else:
            print(f"❌ Erreur de détection QnA: {result.error_message}")
    
    else:
        # Extraction complète des lignes de facturation
        print("\n🔄 Extraction des lignes de facturation...")
        result = extractor.extract_invoice_lines(args.pdf_path)
        
        if result.success:
            print("✅ Extraction réussie!")
            output_file = Path(output_dir) / f"{Path(args.pdf_path).stem}_extraction.json"
            extractor.save_extraction_result(result, str(output_file))
            print(f"📄 Résultats sauvegardés dans: {output_file}")
            
            # Affichage des résultats
            print("\n📊 Résultats de l'extraction:")
            print(f"⏱️  Temps de traitement: {result.processing_time:.2f}s")
            print(f"🎯 Score de confiance: {result.confidence_score:.2%}")
            
            if result.invoice_data:
                invoice = result.invoice_data
                print(f"📄 Numéro de facture: {invoice.invoice_number}")
                print(f"🏢 Fournisseur: {invoice.vendor_name}")
                print(f"👤 Client: {invoice.customer_name}")
                print(f"💰 Montant total: {invoice.total_amount} {invoice.currency}")
                print(f"📋 Nombre de lignes: {len(invoice.lines)}")
                
                # Affichage des annotations manuscrites
                if hasattr(invoice, 'handwritten_annotations') and invoice.handwritten_annotations:
                    print(f"\n✍️  Annotations manuscrites détectées ({len(invoice.handwritten_annotations)}):")
                    for i, annotation in enumerate(invoice.handwritten_annotations, 1):
                        print(f"  {i}. [{annotation.annotation_type.upper()}] {annotation.text}")
                        if annotation.payment_date:
                            print(f"     📅 Date de paiement: {annotation.payment_date}")
                        if annotation.purchase_purpose:
                            print(f"     🎯 Objectif: {annotation.purchase_purpose}")
                        print(f"     🎯 Confiance: {annotation.confidence:.1%}")
                else:
                    print("\n✍️  Aucune annotation manuscrite détectée")
                
                # Affichage des lignes
                print("\n📋 Lignes de facturation:")
                for i, line in enumerate(invoice.lines, 1):
                    print(f"  {i}. {line.description}")
                    print(f"     Quantité: {line.quantity} | Prix unitaire: {line.unit_price} | Total: {line.total}")
            
        else:
            print(f"❌ Erreur d'extraction: {result.error_message}")
            print(f"⏱️  Temps de traitement: {result.processing_time:.2f}s")
    
    print("\n✅ Traitement terminé!")

if __name__ == "__main__":
    main() 