import time
import base64
import json
import sys
from pathlib import Path
from typing import Optional
from mistralai import DocumentURLChunk
from mistralai.extra import response_format_from_pydantic_model

# Ajout du répertoire src au path pour les imports
sys.path.append(str(Path(__file__).parent.parent))

from core.client import mistral_client
from core.security import validate_file_security
from config.models import InvoiceData, InvoiceAnalysis, ExtractionResult, HandwrittenAnnotation, AnnotationDetectionResult
from utils.file_utils import encode_pdf_to_base64
from services.annotation_detector import AnnotationDetector
from services.annotation_qna import AnnotationQnADetector

class InvoiceExtractor:
    """Service d'extraction de données de factures avec OCR Mistral"""
    
    def __init__(self):
        self.client = mistral_client.get_client()
        self.model = mistral_client.get_model()
        self.annotation_detector = AnnotationDetector()
        self.annotation_qna_detector = AnnotationQnADetector(self.client)
    
    def extract_invoice_lines(self, pdf_path: str) -> ExtractionResult:
        """
        Extrait les lignes de facturation d'un PDF
        
        Args:
            pdf_path: Chemin vers le fichier PDF
            
        Returns:
            ExtractionResult: Résultat de l'extraction
        """
        start_time = time.time()
        
        try:
            # Validation de sécurité
            validate_file_security(pdf_path)
            
            # Encodage du PDF
            base64_pdf = encode_pdf_to_base64(pdf_path)
            
            # Création du format de réponse
            response_format = response_format_from_pydantic_model(InvoiceData)
            
            # Appel OCR avec annotations
            response = self.client.ocr.process(
                model=self.model,
                document=DocumentURLChunk(
                    document_url=f"data:application/pdf;base64,{base64_pdf}"
                ),
                document_annotation_format=response_format
            )
            
            processing_time = time.time() - start_time
            
            # Parser la réponse JSON si c'est une chaîne
            invoice_data = response.document_annotation
            if isinstance(invoice_data, str):
                invoice_data = json.loads(invoice_data)
            
            # Détecter les annotations manuscrites
            raw_text = self.extract_raw_text(pdf_path)
            annotations = self.annotation_detector.detect_annotations(raw_text)
            filtered_annotations = self.annotation_detector.filter_annotations(annotations, min_confidence=0.6)
            
            # Ajouter les annotations aux données de facture
            if filtered_annotations:
                invoice_data['handwritten_annotations'] = [ann.model_dump() for ann in filtered_annotations]
            
            return ExtractionResult(
                success=True,
                invoice_data=invoice_data,
                processing_time=processing_time,
                confidence_score=0.95  # Score de confiance estimé
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
        Analyse la structure d'une facture pour comprendre son format
        
        Args:
            pdf_path: Chemin vers le fichier PDF
            
        Returns:
            ExtractionResult: Résultat de l'analyse
        """
        start_time = time.time()
        
        try:
            # Validation de sécurité
            validate_file_security(pdf_path)
            
            # Encodage du PDF
            base64_pdf = encode_pdf_to_base64(pdf_path)
            
            # Création du format de réponse pour l'analyse
            response_format = response_format_from_pydantic_model(InvoiceAnalysis)
            
            # Appel OCR avec annotations d'analyse
            response = self.client.ocr.process(
                model=self.model,
                document=DocumentURLChunk(
                    document_url=f"data:application/pdf;base64,{base64_pdf}"
                ),
                document_annotation_format=response_format
            )
            
            processing_time = time.time() - start_time
            
            # Parser la réponse JSON si c'est une chaîne
            invoice_data = response.document_annotation
            if isinstance(invoice_data, str):
                invoice_data = json.loads(invoice_data)
            
            # Détecter les annotations manuscrites pour l'analyse
            raw_text = self.extract_raw_text(pdf_path)
            annotations = self.annotation_detector.detect_annotations(raw_text)
            filtered_annotations = self.annotation_detector.filter_annotations(annotations, min_confidence=0.6)
            
            # Ajouter les informations d'annotations à l'analyse
            invoice_data['has_handwritten_annotations'] = len(filtered_annotations) > 0
            if filtered_annotations:
                grouped_annotations = self.annotation_detector.group_annotations_by_type(filtered_annotations)
                invoice_data['annotation_types_detected'] = [key for key, value in grouped_annotations.items() if value]
            else:
                invoice_data['annotation_types_detected'] = []
            
            return ExtractionResult(
                success=True,
                invoice_data=invoice_data,
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
        Extrait le texte brut d'un PDF pour analyse manuelle
        
        Args:
            pdf_path: Chemin vers le fichier PDF
            
        Returns:
            str: Texte extrait
        """
        # Validation de sécurité
        validate_file_security(pdf_path)
        
        # Encodage du PDF
        base64_pdf = encode_pdf_to_base64(pdf_path)
        
        # Appel OCR simple
        response = self.client.ocr.process(
            model=self.model,
            document=DocumentURLChunk(
                document_url=f"data:application/pdf;base64,{base64_pdf}"
            )
        )
        
        # Concaténer le texte de toutes les pages
        full_text = ""
        for page in response.pages:
            if hasattr(page, 'markdown') and page.markdown:
                full_text += page.markdown + "\n"
            elif hasattr(page, 'text') and page.text:
                full_text += page.text + "\n"
            elif hasattr(page, 'content') and page.content:
                full_text += page.content + "\n"
        
        return full_text
    
    def detect_annotations_via_qna(self, pdf_path: str) -> ExtractionResult:
        """
        Détecte les annotations manuscrites via Document QnA
        
        Args:
            pdf_path: Chemin vers le fichier PDF
            
        Returns:
            ExtractionResult: Résultat de la détection
        """
        start_time = time.time()
        
        try:
            # Détection des annotations via QnA
            annotations = self.annotation_qna_detector.detect_annotations_via_qna(pdf_path)
            
            processing_time = time.time() - start_time
            
            # Créer un résultat avec les annotations
            result_data = AnnotationDetectionResult(
                annotations_detected=len(annotations),
                handwritten_annotations=annotations,
                detection_method="Document QnA",
                questions_asked=[
                    "Y a-t-il des annotations manuscrites sur cette facture ?",
                    "Quelles sont les dates de paiement mentionnées ?",
                    "Quels sont les objectifs d'achat mentionnés ?"
                ]
            )
            
            return ExtractionResult(
                success=True,
                invoice_data=result_data,
                processing_time=processing_time,
                confidence_score=0.85  # Score de confiance pour QnA
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            
            return ExtractionResult(
                success=False,
                error_message=str(e),
                processing_time=processing_time
            )
    
    def save_extraction_result(self, result: ExtractionResult, output_path: str):
        """
        Sauvegarde le résultat d'extraction en JSON
        
        Args:
            result: Résultat d'extraction
            output_path: Chemin de sauvegarde
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result.model_dump(), f, indent=2, ensure_ascii=False) 