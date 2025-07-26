from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Union
from datetime import datetime

class InvoiceLine(BaseModel):
    """Modèle pour une ligne de facturation"""
    description: str = Field(..., description="Description de l'article ou service")
    quantity: float = Field(..., description="Quantité")
    unit_price: float = Field(..., description="Prix unitaire")
    total: float = Field(..., description="Montant total de la ligne")
    tax_rate: Optional[float] = Field(None, description="Taux de taxe appliqué")
    tax_amount: Optional[float] = Field(None, description="Montant de la taxe")
    unit: Optional[str] = Field(None, description="Unité de mesure (pièce, heure, etc.)")
    reference: Optional[str] = Field(None, description="Référence ou code article")

class HandwrittenAnnotation(BaseModel):
    """Modèle pour les annotations manuscrites des clients"""
    text: str = Field(..., description="Texte de l'annotation manuscrite")
    annotation_type: str = Field(..., description="Type d'annotation: 'payment_info', 'purchase_purpose', 'note', 'other'")
    confidence: float = Field(..., description="Niveau de confiance de la détection (0-1)")
    location: Optional[str] = Field(None, description="Emplacement approximatif sur le document")
    payment_date: Optional[str] = Field(None, description="Date de paiement extraite si présente")
    purchase_purpose: Optional[str] = Field(None, description="Objectif d'achat identifié")

class InvoiceData(BaseModel):
    """Modèle pour les données complètes d'une facture"""
    invoice_number: str = Field(..., description="Numéro de facture")
    invoice_date: str = Field(..., description="Date de facturation")
    vendor_name: str = Field(..., description="Nom du vendeur/fournisseur")
    vendor_address: Optional[str] = Field(None, description="Adresse du vendeur")
    customer_name: str = Field(..., description="Nom du client")
    customer_address: Optional[str] = Field(None, description="Adresse du client")
    subtotal: float = Field(..., description="Montant hors taxes")
    tax_amount: float = Field(..., description="Montant total des taxes")
    total_amount: float = Field(..., description="Montant total TTC")
    currency: str = Field(..., description="Devise utilisée")
    payment_terms: Optional[str] = Field(None, description="Conditions de paiement")
    due_date: Optional[str] = Field(None, description="Date d'échéance")
    lines: List[InvoiceLine] = Field(..., description="Lignes de facturation")
    notes: Optional[str] = Field(None, description="Notes ou commentaires")
    handwritten_annotations: Optional[List[HandwrittenAnnotation]] = Field(None, description="Annotations manuscrites des clients")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class InvoiceAnalysis(BaseModel):
    """Modèle pour l'analyse de structure d'une facture"""
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
    has_handwritten_annotations: bool = Field(..., description="Présence d'annotations manuscrites")
    annotation_types_detected: List[str] = Field(..., description="Types d'annotations détectées")

class AnnotationDetectionResult(BaseModel):
    """Modèle pour le résultat de détection d'annotations"""
    annotations_detected: int = Field(..., description="Nombre d'annotations détectées")
    handwritten_annotations: List[HandwrittenAnnotation] = Field(..., description="Liste des annotations détectées")
    detection_method: str = Field(..., description="Méthode de détection utilisée")
    questions_asked: List[str] = Field(..., description="Questions posées pour la détection")

class ExtractionResult(BaseModel):
    """Modèle pour le résultat d'extraction"""
    success: bool = Field(..., description="Indique si l'extraction a réussi")
    invoice_data: Optional[Union[InvoiceData, InvoiceAnalysis, AnnotationDetectionResult]] = Field(None, description="Données de facture, d'analyse ou de détection d'annotations")
    raw_text: Optional[str] = Field(None, description="Texte brut extrait")
    error_message: Optional[str] = Field(None, description="Message d'erreur si échec")
    processing_time: float = Field(..., description="Temps de traitement en secondes")
    confidence_score: Optional[float] = Field(None, description="Score de confiance de l'extraction") 