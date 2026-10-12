"""
Módulo de Búsqueda Multifunción y Captura de Evidencias Fotográficas.
Proporciona lógica y simulación para:
1. Búsqueda por Código de Barras / QR (optimizado para lector óptico o teclado).
2. Búsqueda por Foto / Imagen (simulando coincidencia o selección directa).
3. Búsqueda por Audio / Voz (simulando reconocimiento de voz / transcripción).
4. Guardado y organización de evidencias fotográficas en una carpeta dedicada (`evidencias/`).
"""

import os
import shutil
import datetime
from typing import Optional, Tuple, List
from PIL import Image

from inventory_model import InventoryManager, InventoryItem


class SearchAndEvidenceManager:
    """
    Controlador para búsquedas multi-método y gestión de evidencias fotográficas.
    """

    def __init__(self, inventory_mgr: InventoryManager, evidence_dir: str = "evidencias"):
        self.inventory_mgr = inventory_mgr
        self.evidence_dir = evidence_dir
        os.makedirs(self.evidence_dir, exist_ok=True)

    # --- 1. BÚSQUEDA POR CÓDIGO DE BARRAS / QR ---
    def search_by_barcode(self, barcode_input: str) -> Optional[InventoryItem]:
        """
        Procesa la entrada recibida de un lector de código de barras o teclado manual.
        """
        code = str(barcode_input).strip()
        if not code:
            return None
        return self.inventory_mgr.find_by_sku(code)

    # --- 2. BÚSQUEDA POR FOTO / IMAGEN (Simulada / Basada en archivo o nombre) ---
    def search_by_image(self, image_path: str) -> List[InventoryItem]:
        """
        Simula la identificación de un producto mediante una imagen.
        Busca coincidencias basadas en el nombre del archivo o extrae metadatos.
        Si no hay coincidencia directa, realiza una búsqueda parcial.
        """
        if not os.path.exists(image_path):
            return []

        filename = os.path.basename(image_path)
        base_name, _ = os.path.splitext(filename)

        # 1. Búsqueda directa por SKU si el nombre de la imagen coincide con un SKU
        exact_item = self.inventory_mgr.find_by_sku(base_name)
        if exact_item:
            return [exact_item]

        # 2. Búsqueda parcial por nombre de la imagen en las descripciones del inventario
        keywords = base_name.replace("_", " ").replace("-", " ").split()
        results = []
        for kw in keywords:
            if len(kw) > 2: # Ignorar palabras muy cortas
                matches = self.inventory_mgr.search(kw)
                for m in matches:
                    if m not in results:
                        results.append(m)

        return results

    # --- 3. BÚSQUEDA POR AUDIO / COMANDO DE VOZ (Simulada) ---
    def search_by_voice(self, voice_transcription: str) -> List[InventoryItem]:
        """
        Recibe la transcripción de texto simulada o ingresada mediante voz
        y realiza una búsqueda en el catálogo del inventario.
        """
        clean_text = voice_transcription.strip().lower()
        if not clean_text:
            return []

        return self.inventory_mgr.search(clean_text)

    # --- 4. GESTIÓN Y CAPTURA DE EVIDENCIA FOTOGRÁFICA ---
    def save_photo_evidence(self, source_image_path: str, sku: str) -> str:
        """
        Copia y optimiza la imagen de evidencia fotográfica seleccionada/capturada
        guardándola dentro de la carpeta `evidencias/` asociada al SKU.
        """
        if not os.path.exists(source_image_path):
            raise FileNotFoundError(f"No se encontró la imagen especificada: {source_image_path}")

        ext = os.path.splitext(source_image_path)[1].lower() or ".jpg"
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        clean_sku = "".join(c for c in sku if c.isalnum() or c in ('-', '_'))
        dest_filename = f"evidencia_{clean_sku}_{timestamp}{ext}"
        dest_path = os.path.join(self.evidence_dir, dest_filename)

        # Copiar imagen a la carpeta de evidencias
        shutil.copy2(source_image_path, dest_path)

        # Asociar evidencia al producto en el inventario si existe
        item = self.inventory_mgr.find_by_sku(sku)
        if item:
            item.photo_path = dest_path

        return dest_path

    def capture_simulated_camera_photo(self, sku: str) -> str:
        """
        Crea una imagen de evidencia fotográfica simulada en caso de no disponer de cámara web física.
        """
        clean_sku = "".join(c for c in sku if c.isalnum() or c in ('-', '_'))
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        dest_filename = f"evidencia_{clean_sku}_{timestamp}.png"
        dest_path = os.path.join(self.evidence_dir, dest_filename)

        # Crear una imagen simulada con Pillow
        img = Image.new('RGB', (400, 300), color=(50, 70, 100))
        img.save(dest_path)

        item = self.inventory_mgr.find_by_sku(sku)
        if item:
            item.photo_path = dest_path

        return dest_path
