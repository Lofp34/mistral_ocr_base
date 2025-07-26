#!/usr/bin/env python3
"""
Service pour détecter les annotations manuscrites via Document QnA
"""

import sys
import json
import time
from pathlib import Path
from typing import List, Dict, Any

# Ajout du répertoire parent au path pour les imports
sys.path.append(str(Path(__file__).parent.parent))

from mistralai import DocumentURLChunk
from config.models import HandwrittenAnnotation

class AnnotationQnADetector:
    """Détecteur d'annotations manuscrites via Document QnA"""
    
    def __init__(self, client):
        self.client = client
        self.model = "mistral-small-latest"
        
        # Questions ciblées pour détecter les annotations
        self.annotation_questions = [
            "Y a-t-il des annotations manuscrites sur cette facture ? Si oui, listez-les toutes.",
            "Quelqu'un a-t-il écrit des notes à la main sur ce document ? Décrivez-les.",
            "Y a-t-il des informations de paiement écrites à la main (dates, modes de paiement) ?",
            "Quelqu'un a-t-il noté l'objectif ou la raison de cet achat ?",
            "Y a-t-il des commentaires manuscrits sur cette facture ?"
        ]
        
        # Questions spécifiques pour extraire les détails
        self.detail_questions = [
            "Quelles sont les dates de paiement mentionnées dans les annotations manuscrites ?",
            "Quels sont les objectifs d'achat ou raisons mentionnés dans les annotations ?",
            "Y a-t-il des informations sur le mode de paiement (virement, chèque, etc.) ?"
        ]
    
    def detect_annotations_via_qna(self, pdf_path: str) -> List[HandwrittenAnnotation]:
        """
        Détecte les annotations manuscrites via Document QnA
        
        Args:
            pdf_path: Chemin vers le fichier PDF
            
        Returns:
            List[HandwrittenAnnotation]: Liste des annotations détectées
        """
        from utils.file_utils import encode_pdf_to_base64
        from core.security import validate_file_security
        
        # Validation et encodage du PDF
        validate_file_security(pdf_path)
        base64_pdf = encode_pdf_to_base64(pdf_path)
        
        annotations = []
        
        try:
            # Question principale pour détecter les annotations
            main_question = "Y a-t-il des annotations manuscrites sur cette facture ? Si oui, listez-les toutes avec leur contenu exact."
            
            response = self._ask_question(main_question, base64_pdf)
            
            # Vérifier si des annotations sont détectées
            has_annotations = (
                response and 
                "non" not in response.lower() and 
                "aucune" not in response.lower() and
                ("annotation" in response.lower() or "bourdon" in response.lower() or "virement" in response.lower())
            )
            
            if has_annotations:
                # Si des annotations sont détectées, poser des questions de détail
                annotations = self._extract_detailed_annotations(base64_pdf, response)
            
        except Exception as e:
            print(f"Erreur lors de la détection QnA: {e}")
        
        return annotations
    
    def _ask_question(self, question: str, base64_pdf: str) -> str:
        """Pose une question sur le document"""
        try:
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": question
                        },
                        {
                            "type": "document_url",
                            "document_url": f"data:application/pdf;base64,{base64_pdf}"
                        }
                    ]
                }
            ]
            
            response = self.client.chat.complete(
                model=self.model,
                messages=messages
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Erreur lors de la question QnA: {e}")
            return ""
    
    def _extract_detailed_annotations(self, base64_pdf: str, initial_response: str) -> List[HandwrittenAnnotation]:
        """Extrait les détails des annotations détectées"""
        annotations = []
        
        try:
            # Question pour les dates de paiement
            payment_question = "Quelles sont les dates de paiement mentionnées dans les annotations manuscrites ? Répondez au format: date1, date2, etc. ou 'aucune'."
            payment_response = self._ask_question(payment_question, base64_pdf)
            
            # Question pour les objectifs d'achat
            purpose_question = "Quels sont les objectifs d'achat ou raisons mentionnés dans les annotations manuscrites ? Répondez au format: objectif1, objectif2, etc. ou 'aucun'."
            purpose_response = self._ask_question(purpose_question, base64_pdf)
            
            # Analyser la réponse initiale pour extraire les annotations
            annotation_texts = self._parse_annotation_response(initial_response)
            
            for text in annotation_texts:
                annotation = self._create_annotation_from_text(
                    text, payment_response, purpose_response
                )
                if annotation:
                    annotations.append(annotation)
            
        except Exception as e:
            print(f"Erreur lors de l'extraction détaillée: {e}")
        
        return annotations
    
    def _parse_annotation_response(self, response: str) -> List[str]:
        """Parse la réponse pour extraire les textes d'annotations"""
        annotations = []
        
        # Chercher les annotations entre guillemets
        import re
        quoted_annotations = re.findall(r'"([^"]+)"', response)
        
        for annotation in quoted_annotations:
            if len(annotation) > 2:
                annotations.append(annotation)
        
        # Si pas d'annotations entre guillemets, chercher dans les listes numérotées
        if not annotations:
            lines = response.split('\n')
            for line in lines:
                line = line.strip()
                if line and re.match(r'^\d+\.', line):
                    # Extraire le texte après le numéro
                    clean_line = re.sub(r'^\d+\.\s*', '', line)
                    # Nettoyer les marqueurs
                    clean_line = clean_line.replace('**', '').replace('–', '').strip()
                    
                    # Extraire le texte entre guillemets dans cette ligne
                    quoted_in_line = re.findall(r'"([^"]+)"', clean_line)
                    if quoted_in_line:
                        annotations.extend(quoted_in_line)
                    else:
                        # Prendre le texte avant le premier tiret ou parenthèse
                        clean_line = re.split(r'[–\-\(]', clean_line)[0].strip()
                        if clean_line and len(clean_line) > 3:
                            annotations.append(clean_line)
        
        return annotations
    
    def _create_annotation_from_text(self, text: str, payment_response: str, purpose_response: str) -> HandwrittenAnnotation:
        """Crée une annotation à partir du texte et des réponses détaillées"""
        
        # Déterminer le type d'annotation
        annotation_type = self._detect_annotation_type(text, payment_response, purpose_response)
        
        # Extraire la date de paiement
        payment_date = self._extract_payment_date(text, payment_response)
        
        # Extraire l'objectif d'achat
        purchase_purpose = self._extract_purchase_purpose(text, purpose_response)
        
        # Calculer la confiance
        confidence = self._calculate_confidence(text, annotation_type, payment_date, purchase_purpose)
        
        return HandwrittenAnnotation(
            text=text,
            annotation_type=annotation_type,
            confidence=confidence,
            location="détecté par QnA",
            payment_date=payment_date,
            purchase_purpose=purchase_purpose
        )
    
    def _detect_annotation_type(self, text: str, payment_response: str, purpose_response: str) -> str:
        """Détecte le type d'annotation"""
        text_lower = text.lower()
        
        # Vérifier si c'est une information de paiement
        payment_keywords = ['virement', 'payé', 'paiement', 'viré', 'chèque', 'prélèvement']
        if any(keyword in text_lower for keyword in payment_keywords):
            return 'payment_info'
        
        # Vérifier si c'est un objectif d'achat
        purpose_keywords = ['bourdon', 'abeille', 'miel', 'tracteur', 'engrais', 'irrigation', 'clôture', 'bâtiment']
        if any(keyword in text_lower for keyword in purpose_keywords):
            return 'purchase_purpose'
        
        return 'note'
    
    def _extract_payment_date(self, text: str, payment_response: str) -> str:
        """Extrait la date de paiement"""
        import re
        
        # Chercher dans le texte de l'annotation
        date_match = re.search(r'(\d{1,2}/\d{1,2}/\d{2,4})', text)
        if date_match:
            return date_match.group(1)
        
        # Chercher dans la réponse de paiement
        if payment_response and "aucune" not in payment_response.lower():
            date_match = re.search(r'(\d{1,2}/\d{1,2}/\d{2,4})', payment_response)
            if date_match:
                return date_match.group(1)
        
        return None
    
    def _extract_purchase_purpose(self, text: str, purpose_response: str) -> str:
        """Extrait l'objectif d'achat"""
        text_lower = text.lower()
        
        # Chercher des mots-clés dans le texte
        purposes = []
        purpose_keywords = ['bourdon', 'abeille', 'miel', 'tracteur', 'engrais', 'irrigation', 'clôture', 'bâtiment']
        for keyword in purpose_keywords:
            if keyword in text_lower:
                purposes.append(keyword)
        
        if purposes:
            return ', '.join(purposes)
        
        # Chercher dans la réponse de but
        if purpose_response and "aucun" not in purpose_response.lower():
            return purpose_response.strip()
        
        return None
    
    def _calculate_confidence(self, text: str, annotation_type: str, payment_date: str, purchase_purpose: str) -> float:
        """Calcule le niveau de confiance"""
        confidence = 0.7  # Base plus élevée pour QnA
        
        # Bonus pour la présence de détails
        if payment_date:
            confidence += 0.15
        if purchase_purpose:
            confidence += 0.15
        
        return min(confidence, 1.0) 