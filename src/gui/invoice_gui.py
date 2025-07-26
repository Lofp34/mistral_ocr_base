#!/usr/bin/env python3
"""
Interface graphique pour l'extracteur de factures Mistral OCR
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import json
import sys
from pathlib import Path
import os

# Ajout du répertoire parent au path pour les imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from services.invoice_extractor import InvoiceExtractor
from utils.file_utils import validate_file_path, validate_file_format

class InvoiceExtractorGUI:
    """Interface graphique pour l'extracteur de factures"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Extracteur de Factures - Mistral OCR")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')
        
        # Variables
        self.pdf_path = tk.StringVar()
        self.output_dir = tk.StringVar(value="data/output")
        self.extractor = None
        self.processing = False
        
        # Configuration du style
        self.setup_styles()
        
        # Création de l'interface
        self.create_widgets()
        
        # Initialisation de l'extracteur
        self.initialize_extractor()
    
    def setup_styles(self):
        """Configure les styles de l'interface"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configuration des couleurs
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'), foreground='#2c3e50')
        style.configure('Header.TLabel', font=('Arial', 12, 'bold'), foreground='#34495e')
        style.configure('Success.TLabel', foreground='#27ae60')
        style.configure('Error.TLabel', foreground='#e74c3c')
        style.configure('Info.TLabel', foreground='#3498db')
    
    def create_widgets(self):
        """Crée les widgets de l'interface"""
        
        # Titre principal
        title_frame = tk.Frame(self.root, bg='#f0f0f0')
        title_frame.pack(fill='x', padx=20, pady=10)
        
        title_label = ttk.Label(title_frame, text="🚀 Extracteur de Factures - Mistral OCR", style='Title.TLabel')
        title_label.pack()
        
        # Section de sélection de fichier
        self.create_file_section()
        
        # Section des actions
        self.create_actions_section()
        
        # Section de statut
        self.create_status_section()
        
        # Section de résultats
        self.create_results_section()
    
    def create_file_section(self):
        """Crée la section de sélection de fichier"""
        file_frame = ttk.LabelFrame(self.root, text="📁 Sélection du fichier PDF", padding=10)
        file_frame.pack(fill='x', padx=20, pady=10)
        
        # Sélection de fichier
        file_select_frame = tk.Frame(file_frame)
        file_select_frame.pack(fill='x', pady=5)
        
        ttk.Label(file_select_frame, text="Fichier PDF:").pack(side='left')
        ttk.Entry(file_select_frame, textvariable=self.pdf_path, width=50).pack(side='left', padx=5)
        ttk.Button(file_select_frame, text="Parcourir", command=self.browse_file).pack(side='left', padx=5)
        
        # Répertoire de sortie
        output_frame = tk.Frame(file_frame)
        output_frame.pack(fill='x', pady=5)
        
        ttk.Label(output_frame, text="Sortie:").pack(side='left')
        ttk.Entry(output_frame, textvariable=self.output_dir, width=50).pack(side='left', padx=5)
        ttk.Button(output_frame, text="Parcourir", command=self.browse_output_dir).pack(side='left', padx=5)
    
    def create_actions_section(self):
        """Crée la section des actions"""
        actions_frame = ttk.LabelFrame(self.root, text="⚡ Actions disponibles", padding=10)
        actions_frame.pack(fill='x', padx=20, pady=10)
        
        # Boutons d'action
        buttons_frame = tk.Frame(actions_frame)
        buttons_frame.pack(fill='x', pady=5)
        
        # Première ligne
        row1 = tk.Frame(buttons_frame)
        row1.pack(fill='x', pady=5)
        
        self.extract_btn = ttk.Button(row1, text="📋 Extraction complète", 
                                     command=lambda: self.run_action("extract"))
        self.extract_btn.pack(side='left', padx=5)
        
        self.analyze_btn = ttk.Button(row1, text="🔍 Analyse structure", 
                                     command=lambda: self.run_action("analyze"))
        self.analyze_btn.pack(side='left', padx=5)
        
        # Deuxième ligne
        row2 = tk.Frame(buttons_frame)
        row2.pack(fill='x', pady=5)
        
        self.text_btn = ttk.Button(row2, text="📄 Texte brut", 
                                  command=lambda: self.run_action("raw_text"))
        self.text_btn.pack(side='left', padx=5)
        
        self.annotations_btn = ttk.Button(row2, text="✍️ Détection annotations", 
                                         command=lambda: self.run_action("annotations"))
        self.annotations_btn.pack(side='left', padx=5)
        
        # Bouton pour tout faire
        self.all_btn = ttk.Button(buttons_frame, text="🔄 Tout traiter", 
                                 command=self.run_all_actions)
        self.all_btn.pack(pady=10)
    
    def create_status_section(self):
        """Crée la section de statut"""
        status_frame = ttk.LabelFrame(self.root, text="📊 Statut", padding=10)
        status_frame.pack(fill='x', padx=20, pady=10)
        
        # Barre de progression
        self.progress = ttk.Progressbar(status_frame, mode='indeterminate')
        self.progress.pack(fill='x', pady=5)
        
        # Label de statut
        self.status_label = ttk.Label(status_frame, text="Prêt", style='Info.TLabel')
        self.status_label.pack(pady=5)
    
    def create_results_section(self):
        """Crée la section de résultats"""
        results_frame = ttk.LabelFrame(self.root, text="📋 Résultats", padding=10)
        results_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Zone de texte pour les résultats
        self.results_text = scrolledtext.ScrolledText(results_frame, height=15, wrap='word')
        self.results_text.pack(fill='both', expand=True)
        
        # Boutons pour les résultats
        results_buttons = tk.Frame(results_frame)
        results_buttons.pack(fill='x', pady=5)
        
        ttk.Button(results_buttons, text="📁 Ouvrir dossier sortie", 
                  command=self.open_output_folder).pack(side='left', padx=5)
        ttk.Button(results_buttons, text="🗑️ Effacer résultats", 
                  command=self.clear_results).pack(side='left', padx=5)
    
    def initialize_extractor(self):
        """Initialise l'extracteur"""
        try:
            self.extractor = InvoiceExtractor()
            self.update_status("✅ Extracteur initialisé avec succès", "success")
        except Exception as e:
            self.update_status(f"❌ Erreur d'initialisation: {e}", "error")
    
    def browse_file(self):
        """Ouvre le dialogue de sélection de fichier"""
        filename = filedialog.askopenfilename(
            title="Sélectionner un fichier PDF",
            filetypes=[("Fichiers PDF", "*.pdf"), ("Tous les fichiers", "*.*")]
        )
        if filename:
            self.pdf_path.set(filename)
            self.validate_file()
    
    def browse_output_dir(self):
        """Ouvre le dialogue de sélection de répertoire de sortie"""
        directory = filedialog.askdirectory(title="Sélectionner le répertoire de sortie")
        if directory:
            self.output_dir.set(directory)
    
    def validate_file(self):
        """Valide le fichier sélectionné"""
        file_path = self.pdf_path.get()
        if not file_path:
            return
        
        try:
            validate_file_path(file_path)
            validate_file_format(file_path, ['.pdf'])
            
            # Afficher les informations du fichier
            file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
            self.update_status(f"✅ Fichier valide: {Path(file_path).name} ({file_size:.2f} MB)", "success")
            
        except Exception as e:
            self.update_status(f"❌ Fichier invalide: {e}", "error")
    
    def run_action(self, action_type):
        """Exécute une action spécifique"""
        if self.processing:
            messagebox.showwarning("Traitement en cours", "Veuillez attendre la fin du traitement en cours.")
            return
        
        if not self.pdf_path.get():
            messagebox.showerror("Erreur", "Veuillez sélectionner un fichier PDF.")
            return
        
        # Démarrer le traitement dans un thread séparé
        thread = threading.Thread(target=self._process_action, args=(action_type,))
        thread.daemon = True
        thread.start()
    
    def run_all_actions(self):
        """Exécute toutes les actions"""
        if self.processing:
            messagebox.showwarning("Traitement en cours", "Veuillez attendre la fin du traitement en cours.")
            return
        
        if not self.pdf_path.get():
            messagebox.showerror("Erreur", "Veuillez sélectionner un fichier PDF.")
            return
        
        # Démarrer le traitement dans un thread séparé
        thread = threading.Thread(target=self._process_all_actions)
        thread.daemon = True
        thread.start()
    
    def _process_action(self, action_type):
        """Traite une action spécifique"""
        self.processing = True
        self.update_status("🔄 Traitement en cours...", "info")
        self.progress.start()
        self.disable_buttons()
        
        try:
            pdf_path = self.pdf_path.get()
            output_dir = self.output_dir.get()
            
            # Créer le répertoire de sortie s'il n'existe pas
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            
            if action_type == "extract":
                self._extract_invoice_lines(pdf_path, output_dir)
            elif action_type == "analyze":
                self._analyze_invoice_structure(pdf_path, output_dir)
            elif action_type == "raw_text":
                self._extract_raw_text(pdf_path, output_dir)
            elif action_type == "annotations":
                self._detect_annotations(pdf_path, output_dir)
            
        except Exception as e:
            self.update_status(f"❌ Erreur: {e}", "error")
            messagebox.showerror("Erreur", f"Une erreur s'est produite:\n{e}")
        
        finally:
            self.processing = False
            self.progress.stop()
            self.enable_buttons()
    
    def _process_all_actions(self):
        """Traite toutes les actions"""
        self.processing = True
        self.update_status("🔄 Traitement complet en cours...", "info")
        self.progress.start()
        self.disable_buttons()
        
        try:
            pdf_path = self.pdf_path.get()
            output_dir = self.output_dir.get()
            
            # Créer le répertoire de sortie s'il n'existe pas
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            
            results = []
            
            # Extraction complète
            self.update_status("📋 Extraction des lignes de facturation...", "info")
            result = self.extractor.extract_invoice_lines(pdf_path)
            if result.success:
                output_file = Path(output_dir) / f"{Path(pdf_path).stem}_extraction.json"
                self.extractor.save_extraction_result(result, str(output_file))
                results.append(f"✅ Extraction: {output_file.name}")
            else:
                results.append(f"❌ Extraction: {result.error_message}")
            
            # Analyse de structure
            self.update_status("🔍 Analyse de la structure...", "info")
            result = self.extractor.analyze_invoice_structure(pdf_path)
            if result.success:
                output_file = Path(output_dir) / f"{Path(pdf_path).stem}_analysis.json"
                self.extractor.save_extraction_result(result, str(output_file))
                results.append(f"✅ Analyse: {output_file.name}")
            else:
                results.append(f"❌ Analyse: {result.error_message}")
            
            # Texte brut
            self.update_status("📄 Extraction du texte brut...", "info")
            try:
                raw_text = self.extractor.extract_raw_text(pdf_path)
                output_file = Path(output_dir) / f"{Path(pdf_path).stem}_text.txt"
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(raw_text)
                results.append(f"✅ Texte brut: {output_file.name}")
            except Exception as e:
                results.append(f"❌ Texte brut: {e}")
            
            # Détection d'annotations
            self.update_status("✍️ Détection d'annotations...", "info")
            result = self.extractor.detect_annotations_via_qna(pdf_path)
            if result.success:
                output_file = Path(output_dir) / f"{Path(pdf_path).stem}_annotations_qna.json"
                self.extractor.save_extraction_result(result, str(output_file))
                results.append(f"✅ Annotations: {output_file.name}")
            else:
                results.append(f"❌ Annotations: {result.error_message}")
            
            # Afficher les résultats
            self.update_status("✅ Traitement complet terminé!", "success")
            self.display_results("\n".join(results))
            
        except Exception as e:
            self.update_status(f"❌ Erreur: {e}", "error")
            messagebox.showerror("Erreur", f"Une erreur s'est produite:\n{e}")
        
        finally:
            self.processing = False
            self.progress.stop()
            self.enable_buttons()
    
    def _extract_invoice_lines(self, pdf_path, output_dir):
        """Extrait les lignes de facturation"""
        result = self.extractor.extract_invoice_lines(pdf_path)
        
        if result.success:
            output_file = Path(output_dir) / f"{Path(pdf_path).stem}_extraction.json"
            self.extractor.save_extraction_result(result, str(output_file))
            
            self.update_status(f"✅ Extraction réussie: {output_file.name}", "success")
            self.display_extraction_results(result)
        else:
            self.update_status(f"❌ Erreur d'extraction: {result.error_message}", "error")
    
    def _analyze_invoice_structure(self, pdf_path, output_dir):
        """Analyse la structure de la facture"""
        result = self.extractor.analyze_invoice_structure(pdf_path)
        
        if result.success:
            output_file = Path(output_dir) / f"{Path(pdf_path).stem}_analysis.json"
            self.extractor.save_extraction_result(result, str(output_file))
            
            self.update_status(f"✅ Analyse réussie: {output_file.name}", "success")
            self.display_analysis_results(result)
        else:
            self.update_status(f"❌ Erreur d'analyse: {result.error_message}", "error")
    
    def _extract_raw_text(self, pdf_path, output_dir):
        """Extrait le texte brut"""
        try:
            raw_text = self.extractor.extract_raw_text(pdf_path)
            output_file = Path(output_dir) / f"{Path(pdf_path).stem}_text.txt"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(raw_text)
            
            self.update_status(f"✅ Texte extrait: {output_file.name}", "success")
            self.display_text_results(raw_text, output_file)
        except Exception as e:
            self.update_status(f"❌ Erreur d'extraction: {e}", "error")
    
    def _detect_annotations(self, pdf_path, output_dir):
        """Détecte les annotations manuscrites"""
        result = self.extractor.detect_annotations_via_qna(pdf_path)
        
        if result.success:
            output_file = Path(output_dir) / f"{Path(pdf_path).stem}_annotations_qna.json"
            self.extractor.save_extraction_result(result, str(output_file))
            
            self.update_status(f"✅ Annotations détectées: {output_file.name}", "success")
            self.display_annotation_results(result)
        else:
            self.update_status(f"❌ Erreur de détection: {result.error_message}", "error")
    
    def display_extraction_results(self, result):
        """Affiche les résultats d'extraction"""
        if result.invoice_data and hasattr(result.invoice_data, 'lines'):
            lines = result.invoice_data.lines
            output = f"📋 EXTRACTION DES LIGNES DE FACTURATION\n"
            output += f"{'='*50}\n"
            output += f"✅ Succès: {result.success}\n"
            output += f"⏱️ Temps: {result.processing_time:.2f}s\n"
            output += f"📊 Nombre de lignes: {len(lines)}\n\n"
            
            for i, line in enumerate(lines[:10], 1):  # Afficher les 10 premières lignes
                output += f"{i}. {line.description}\n"
                output += f"   Quantité: {line.quantity} {line.unit or 'unité'}\n"
                output += f"   Prix: {line.unit_price}€\n"
                output += f"   Total: {line.total}€\n\n"
            
            if len(lines) > 10:
                output += f"... et {len(lines) - 10} lignes supplémentaires\n"
            
            self.display_results(output)
    
    def display_analysis_results(self, result):
        """Affiche les résultats d'analyse"""
        if result.invoice_data:
            data = result.invoice_data
            output = f"🔍 ANALYSE DE STRUCTURE\n"
            output += f"{'='*50}\n"
            output += f"✅ Succès: {result.success}\n"
            output += f"⏱️ Temps: {result.processing_time:.2f}s\n"
            output += f"📄 Type: {data.document_type}\n"
            output += f"🏢 Vendeur: {data.vendor_name}\n"
            output += f"📅 Date: {data.invoice_date}\n"
            output += f"💰 Montant total: {data.total_amount} {data.currency}\n"
            output += f"📊 Colonnes identifiées: {', '.join(data.columns_identified)}\n"
            output += f"📋 Exemples de lignes: {len(data.sample_lines)}\n\n"
            
            for i, sample in enumerate(data.sample_lines[:5], 1):
                output += f"{i}. {sample}\n"
            
            self.display_results(output)
    
    def display_text_results(self, text, output_file):
        """Affiche les résultats d'extraction de texte"""
        output = f"📄 TEXTE BRUT EXTRAIT\n"
        output += f"{'='*50}\n"
        output += f"📁 Fichier: {output_file.name}\n"
        output += f"📏 Longueur: {len(text)} caractères\n\n"
        output += f"📋 APERÇU:\n"
        output += f"{'-'*30}\n"
        output += text[:500] + "..." if len(text) > 500 else text
        output += f"\n{'-'*30}\n"
        
        self.display_results(output)
    
    def display_annotation_results(self, result):
        """Affiche les résultats de détection d'annotations"""
        if result.invoice_data:
            data = result.invoice_data
            output = f"✍️ DÉTECTION D'ANNOTATIONS MANUSCRITES\n"
            output += f"{'='*50}\n"
            output += f"✅ Succès: {result.success}\n"
            output += f"⏱️ Temps: {result.processing_time:.2f}s\n"
            output += f"🔍 Méthode: {data.detection_method}\n"
            output += f"📊 Annotations détectées: {data.annotations_detected}\n\n"
            
            if data.handwritten_annotations:
                output += f"✍️ ANNOTATIONS DÉTECTÉES:\n"
                for i, annotation in enumerate(data.handwritten_annotations, 1):
                    output += f"{i}. [{annotation.annotation_type.upper()}] {annotation.text}\n"
                    if annotation.payment_date:
                        output += f"   📅 Date de paiement: {annotation.payment_date}\n"
                    if annotation.purchase_purpose:
                        output += f"   🎯 Objectif: {annotation.purchase_purpose}\n"
                    output += f"   🎯 Confiance: {annotation.confidence:.1%}\n\n"
            else:
                output += f"✍️ Aucune annotation manuscrite détectée\n\n"
            
            output += f"❓ QUESTIONS POSÉES:\n"
            for i, question in enumerate(data.questions_asked, 1):
                output += f"{i}. {question}\n"
            
            self.display_results(output)
    
    def display_results(self, text):
        """Affiche du texte dans la zone de résultats"""
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(1.0, text)
    
    def update_status(self, message, status_type="info"):
        """Met à jour le statut"""
        style_map = {
            "success": "Success.TLabel",
            "error": "Error.TLabel",
            "info": "Info.TLabel"
        }
        
        self.status_label.configure(text=message, style=style_map.get(status_type, "Info.TLabel"))
        self.root.update_idletasks()
    
    def disable_buttons(self):
        """Désactive les boutons pendant le traitement"""
        self.extract_btn.configure(state='disabled')
        self.analyze_btn.configure(state='disabled')
        self.text_btn.configure(state='disabled')
        self.annotations_btn.configure(state='disabled')
        self.all_btn.configure(state='disabled')
    
    def enable_buttons(self):
        """Réactive les boutons après le traitement"""
        self.extract_btn.configure(state='normal')
        self.analyze_btn.configure(state='normal')
        self.text_btn.configure(state='normal')
        self.annotations_btn.configure(state='normal')
        self.all_btn.configure(state='normal')
    
    def open_output_folder(self):
        """Ouvre le dossier de sortie"""
        output_dir = self.output_dir.get()
        if output_dir and Path(output_dir).exists():
            os.system(f'open "{output_dir}"')  # macOS
        else:
            messagebox.showwarning("Dossier introuvable", "Le dossier de sortie n'existe pas.")
    
    def clear_results(self):
        """Efface les résultats"""
        self.results_text.delete(1.0, tk.END)
        self.update_status("Prêt", "info")

def main():
    """Fonction principale"""
    root = tk.Tk()
    app = InvoiceExtractorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 