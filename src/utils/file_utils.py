import os
import base64
from pathlib import Path
from typing import List

def encode_pdf_to_base64(pdf_path: str) -> str:
    """Encode un fichier PDF en base64"""
    with open(pdf_path, "rb") as pdf_file:
        return base64.b64encode(pdf_file.read()).decode('utf-8')

def validate_file_path(file_path: str) -> bool:
    """Vérifie l'existence d'un fichier"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Le fichier {file_path} n'existe pas")
    return True

def validate_file_format(file_path: str, allowed_extensions: List[str]) -> bool:
    """Vérifie le format d'un fichier"""
    file_extension = os.path.splitext(file_path)[1].lower()
    if file_extension not in allowed_extensions:
        raise ValueError(f"Format non supporté: {file_extension}")
    return True

def validate_file_size(file_path: str, max_size_mb: int = 50) -> bool:
    """Vérifie la taille d'un fichier"""
    file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
    if file_size > max_size_mb:
        raise ValueError(f"Fichier trop volumineux: {file_size:.2f}MB")
    return True

def create_output_directory(output_dir: str) -> str:
    """Crée un répertoire de sortie s'il n'existe pas"""
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    return output_dir

def get_file_info(file_path: str) -> dict:
    """Récupère les informations d'un fichier"""
    stat = os.stat(file_path)
    return {
        "name": os.path.basename(file_path),
        "size": stat.st_size,
        "size_mb": stat.st_size / (1024 * 1024),
        "extension": os.path.splitext(file_path)[1].lower(),
        "modified": stat.st_mtime
    }

def list_pdf_files(directory: str) -> List[str]:
    """Liste tous les fichiers PDF dans un répertoire"""
    pdf_files = []
    for file in os.listdir(directory):
        if file.lower().endswith('.pdf'):
            pdf_files.append(os.path.join(directory, file))
    return pdf_files 