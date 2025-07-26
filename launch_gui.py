#!/usr/bin/env python3
"""
Script de lancement pour l'interface graphique
"""

import sys
from pathlib import Path

# Ajout du répertoire src au path
sys.path.append(str(Path(__file__).parent / "src"))

def main():
    """Lance l'interface graphique"""
    try:
        from gui.invoice_gui import main as gui_main
        print("🚀 Lancement de l'interface graphique...")
        gui_main()
    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        print("Assurez-vous que toutes les dépendances sont installées.")
        print("Exécutez: pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ Erreur: {e}")
        print("Vérifiez que votre environnement virtuel est activé.")

if __name__ == "__main__":
    main() 