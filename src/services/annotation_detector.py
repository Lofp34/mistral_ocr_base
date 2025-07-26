#!/usr/bin/env python3
"""
Service pour détecter et analyser les annotations manuscrites sur les factures
"""

import re
import sys
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

# Ajout du répertoire parent au path pour les imports
sys.path.append(str(Path(__file__).parent.parent))

from config.models import HandwrittenAnnotation

class AnnotationDetector:
    """Détecteur d'annotations manuscrites sur les factures"""
    
    def __init__(self):
        # Patterns pour détecter les types d'annotations
        self.payment_patterns = [
            r'virement\s+le\s+(\d{1,2}/\d{1,2}/\d{2,4})',
            r'payé\s+le\s+(\d{1,2}/\d{1,2}/\d{2,4})',
            r'paiement\s+le\s+(\d{1,2}/\d{1,2}/\d{2,4})',
            r'viré\s+le\s+(\d{1,2}/\d{1,2}/\d{2,4})',
            r'chèque\s+(\d{1,2}/\d{1,2}/\d{2,4})',
            r'prélèvement\s+(\d{1,2}/\d{1,2}/\d{2,4})',
            r'(\d{1,2}/\d{1,2}/\d{2,4})\s*[-\s]*\s*virement',
            r'(\d{1,2}/\d{1,2}/\d{2,4})\s*[-\s]*\s*payé',
        ]
        
        # Patterns pour les objectifs d'achat
        self.purpose_patterns = [
            r'(bourdon|abeille|ruche|apiculture|miel)',
            r'(tracteur|moissonneuse|semoir|outil)',
            r'(engrais|pesticide|semence|plante)',
            r'(irrigation|arrosage|pompe|réservoir)',
            r'(clôture|barrière|enclos|protection)',
            r'(bâtiment|hangar|grange|étable)',
            r'(machinisme|équipement|matériel)',
            r'(formation|conseil|expertise)',
        ]
        
        # Mots-clés pour identifier les annotations (plus spécifiques)
        self.annotation_keywords = [
            'virement', 'payé', 'paiement', 'viré', 'chèque', 'prélèvement',
            'bourdon', 'abeille', 'miel', 'tracteur', 'engrais', 'irrigation',
            'clôture', 'bâtiment', 'formation', 'conseil', 'expertise'
        ]
        
        # Compiler les patterns regex
        self.payment_regex = [re.compile(pattern, re.IGNORECASE) for pattern in self.payment_patterns]
        self.purpose_regex = [re.compile(pattern, re.IGNORECASE) for pattern in self.purpose_patterns]
    
    def detect_annotations(self, raw_text: str) -> List[HandwrittenAnnotation]:
        """
        Détecte les annotations manuscrites dans le texte brut
        
        Args:
            raw_text: Texte brut extrait du PDF
            
        Returns:
            List[HandwrittenAnnotation]: Liste des annotations détectées
        """
        annotations = []
        
        # Diviser le texte en lignes
        lines = raw_text.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue
            
            # Vérifier si la ligne contient des mots-clés d'annotation
            if self._contains_annotation_keywords(line):
                annotation = self._analyze_line(line, line_num)
                if annotation:
                    annotations.append(annotation)
        
        return annotations
    
    def _contains_annotation_keywords(self, line: str) -> bool:
        """Vérifie si une ligne contient des mots-clés d'annotation"""
        line_lower = line.lower()
        
        # Ignorer les lignes qui ressemblent à des lignes de facturation
        if '|' in line or 'UN' in line or any(char.isdigit() for char in line[:10]):
            return False
        
        # Ignorer les lignes trop longues (probablement des conditions légales)
        if len(line) > 200:
            return False
            
        # Ignorer les lignes avec des références légales
        legal_keywords = ['tribunal', 'article', 'code', 'clause', 'pénalités', 'indemnité', 'iban', 'bic']
        if any(keyword in line_lower for keyword in legal_keywords):
            return False
            
        return any(keyword in line_lower for keyword in self.annotation_keywords)
    
    def _analyze_line(self, line: str, line_num: int) -> HandwrittenAnnotation:
        """Analyse une ligne pour extraire les informations d'annotation"""
        
        # Détecter le type d'annotation
        annotation_type = self._detect_annotation_type(line)
        
        # Extraire la date de paiement si présente
        payment_date = self._extract_payment_date(line)
        
        # Extraire l'objectif d'achat si présent
        purchase_purpose = self._extract_purchase_purpose(line)
        
        # Calculer le niveau de confiance
        confidence = self._calculate_confidence(line, annotation_type, payment_date, purchase_purpose)
        
        # Déterminer l'emplacement
        location = self._determine_location(line_num, line)
        
        return HandwrittenAnnotation(
            text=line,
            annotation_type=annotation_type,
            confidence=confidence,
            location=location,
            payment_date=payment_date,
            purchase_purpose=purchase_purpose
        )
    
    def _detect_annotation_type(self, line: str) -> str:
        """Détecte le type d'annotation"""
        line_lower = line.lower()
        
        # Vérifier les patterns de paiement
        for pattern in self.payment_regex:
            if pattern.search(line):
                return 'payment_info'
        
        # Vérifier les patterns d'objectif d'achat
        for pattern in self.purpose_regex:
            if pattern.search(line):
                return 'purchase_purpose'
        
        # Si la ligne contient des mots-clés mais ne correspond à aucun pattern spécifique
        if any(keyword in line_lower for keyword in self.annotation_keywords):
            return 'note'
        
        return 'other'
    
    def _extract_payment_date(self, line: str) -> str:
        """Extrait la date de paiement de la ligne"""
        for pattern in self.payment_regex:
            match = pattern.search(line)
            if match:
                # Extraire la date du groupe capturé
                if len(match.groups()) > 0:
                    return match.group(1)
                # Si pas de groupe, chercher une date dans la ligne
                date_match = re.search(r'(\d{1,2}/\d{1,2}/\d{2,4})', line)
                if date_match:
                    return date_match.group(1)
        return None
    
    def _extract_purchase_purpose(self, line: str) -> str:
        """Extrait l'objectif d'achat de la ligne"""
        line_lower = line.lower()
        
        # Chercher des mots-clés spécifiques
        purposes = []
        for pattern in self.purpose_regex:
            match = pattern.search(line_lower)
            if match:
                purposes.append(match.group(1))
        
        if purposes:
            return ', '.join(purposes)
        
        return None
    
    def _calculate_confidence(self, line: str, annotation_type: str, 
                            payment_date: str, purchase_purpose: str) -> float:
        """Calcule le niveau de confiance de la détection"""
        confidence = 0.5  # Base
        
        # Bonus pour la présence de mots-clés
        keyword_count = sum(1 for keyword in self.annotation_keywords if keyword in line.lower())
        confidence += min(keyword_count * 0.1, 0.3)
        
        # Bonus pour la détection de type spécifique
        if annotation_type in ['payment_info', 'purchase_purpose']:
            confidence += 0.2
        
        # Bonus pour la présence de date de paiement
        if payment_date:
            confidence += 0.15
        
        # Bonus pour la présence d'objectif d'achat
        if purchase_purpose:
            confidence += 0.15
        
        # Bonus pour la longueur appropriée (pas trop courte, pas trop longue)
        if 5 <= len(line) <= 100:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _determine_location(self, line_num: int, line: str) -> str:
        """Détermine l'emplacement approximatif de l'annotation"""
        if line_num <= 10:
            return "en-tête"
        elif line_num <= 30:
            return "corps principal"
        else:
            return "pied de page"
    
    def filter_annotations(self, annotations: List[HandwrittenAnnotation], 
                          min_confidence: float = 0.6) -> List[HandwrittenAnnotation]:
        """Filtre les annotations par niveau de confiance"""
        return [ann for ann in annotations if ann.confidence >= min_confidence]
    
    def group_annotations_by_type(self, annotations: List[HandwrittenAnnotation]) -> Dict[str, List[HandwrittenAnnotation]]:
        """Groupe les annotations par type"""
        grouped = {
            'payment_info': [],
            'purchase_purpose': [],
            'note': [],
            'other': []
        }
        
        for annotation in annotations:
            grouped[annotation.annotation_type].append(annotation)
        
        return grouped 