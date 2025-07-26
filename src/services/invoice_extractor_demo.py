import time
import json
import sys
from pathlib import Path
from typing import Optional

# Ajout du répertoire src au path pour les imports
sys.path.append(str(Path(__file__).parent.parent))

from config.models import InvoiceData, InvoiceAnalysis, ExtractionResult, InvoiceLine
from utils.file_utils import encode_pdf_to_base64, validate_file_security

class InvoiceExtractorDemo:
    """Service de démonstration d'extraction de données de factures"""
    
    def __init__(self):
        self.model = "mistral-ocr-latest"
    
    def extract_invoice_lines(self, pdf_path: str) -> ExtractionResult:
        """
        Simule l'extraction des lignes de facturation d'un PDF
        
        Args:
            pdf_path: Chemin vers le fichier PDF
            
        Returns:
            ExtractionResult: Résultat de l'extraction simulée
        """
        start_time = time.time()
        
        try:
            # Validation de sécurité
            validate_file_security(pdf_path)
            
            # Simulation du temps de traitement OCR
            time.sleep(2)
            
            # Données de démonstration basées sur une facture typique
            demo_invoice = InvoiceData(
                invoice_number="FAC-2024-001",
                invoice_date="2024-01-15",
                vendor_name="Tech Solutions SARL",
                vendor_address="123 Rue de l'Innovation, 75001 Paris",
                customer_name="Entreprise Client",
                customer_address="456 Avenue des Affaires, 69000 Lyon",
                subtotal=1500.00,
                tax_amount=300.00,
                total_amount=1800.00,
                currency="EUR",
                payment_terms="Paiement à 30 jours",
                due_date="2024-02-14",
                lines=[
                    InvoiceLine(
                        description="Développement application web",
                        quantity=40.0,
                        unit_price=25.00,
                        total=1000.00,
                        tax_rate=20.0,
                        tax_amount=200.00,
                        unit="heures",
                        reference="DEV-WEB-001"
                    ),
                    InvoiceLine(
                        description="Maintenance serveur",
                        quantity=1.0,
                        unit_price=500.00,
                        total=500.00,
                        tax_rate=20.0,
                        tax_amount=100.00,
                        unit="mois",
                        reference="MAINT-SRV-001"
                    )
                ],
                notes="Facture émise pour services de développement et maintenance"
            )
            
            processing_time = time.time() - start_time
            
            return ExtractionResult(
                success=True,
                invoice_data=demo_invoice,
                processing_time=processing_time,
                confidence_score=0.95
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            
            return ExtractionResult(
                success=False,
                error_message=str(e),
                processing_time=processing_time
            )
    
    def analyze_invoice_structure(self, pdf_path: str) -> ExtractionResult:
        """
        Simule l'analyse de la structure d'une facture
        
        Args:
            pdf_path: Chemin vers le fichier PDF
            
        Returns:
            ExtractionResult: Résultat de l'analyse simulée
        """
        start_time = time.time()
        
        try:
            # Validation de sécurité
            validate_file_security(pdf_path)
            
            # Simulation du temps de traitement
            time.sleep(1.5)
            
            # Analyse de démonstration
            demo_analysis = InvoiceAnalysis(
                document_type="Facture",
                vendor_name="Tech Solutions SARL",
                invoice_number="FAC-2024-001",
                invoice_date="2024-01-15",
                customer_name="Entreprise Client",
                total_amount=1800.00,
                currency="EUR",
                table_structure="Tableau avec colonnes: Description, Quantité, Prix unitaire, Total",
                columns_identified=["Description", "Quantité", "Prix unitaire", "Total", "TVA"],
                sample_lines=[
                    "Développement application web | 40h | 25€ | 1000€",
                    "Maintenance serveur | 1 mois | 500€ | 500€"
                ]
            )
            
            processing_time = time.time() - start_time
            
            return ExtractionResult(
                success=True,
                invoice_data=demo_analysis,
                processing_time=processing_time,
                confidence_score=0.90
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            
            return ExtractionResult(
                success=False,
                error_message=str(e),
                processing_time=processing_time
            )
    
    def extract_raw_text(self, pdf_path: str) -> str:
        """
        Simule l'extraction du texte brut d'un PDF
        
        Args:
            pdf_path: Chemin vers le fichier PDF
            
        Returns:
            str: Texte simulé extrait
        """
        # Validation de sécurité
        validate_file_security(pdf_path)
        
        # Simulation du temps de traitement
        time.sleep(1)
        
        # Texte de démonstration basé sur une facture typique
        demo_text = """
FACTURE

Tech Solutions SARL
123 Rue de l'Innovation
75001 Paris, France
Tél: +33 1 23 45 67 89
Email: contact@techsolutions.fr

FACTURE N° FAC-2024-001
Date: 15/01/2024
Échéance: 14/02/2024

CLIENT:
Entreprise Client
456 Avenue des Affaires
69000 Lyon, France

DÉTAIL DES PRESTATIONS:

Description                    Quantité    Prix unitaire    Total HT
Développement application web    40h          25,00 €        1000,00 €
Maintenance serveur              1 mois       500,00 €        500,00 €

SOUS-TOTAL HT:                                                   1500,00 €
TVA 20%:                                                         300,00 €
TOTAL TTC:                                                       1800,00 €

Conditions de paiement: Paiement à 30 jours
Notes: Facture émise pour services de développement et maintenance

Merci de votre confiance !
        """
        
        return demo_text.strip()
    
    def save_extraction_result(self, result: ExtractionResult, output_path: str):
        """
        Sauvegarde le résultat d'extraction en JSON
        
        Args:
            result: Résultat d'extraction
            output_path: Chemin de sauvegarde
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result.dict(), f, indent=2, ensure_ascii=False) 