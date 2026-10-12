"""
Módulo del Modelo de Inventario y Gestor de Datos.
Administra la lista de productos del inventario mensual, importaciones de Excel/CSV/XML,
conteo físico, actualización de estatus, búsqueda y registro de evidencias fotográficas.
"""

import os
from typing import List, Dict, Any, Optional
import pandas as pd


class InventoryItem:
    """
    Representa un elemento/producto individual dentro del inventario.
    """
    def __init__(
        self,
        sku: str,
        description: str,
        category: str = "General",
        theoretical_stock: float = 0.0,
        physical_stock: float = 0.0,
        status: Optional[str] = None,
        photo_path: str = "",
        is_new_item: bool = False
    ):
        self.sku = str(sku).strip()
        self.description = str(description).strip()
        self.category = str(category).strip() if category else "General"
        self.theoretical_stock = float(theoretical_stock)
        self.physical_stock = float(physical_stock)
        self.photo_path = str(photo_path).strip()
        self.is_new_item = bool(is_new_item)

        # Si el estatus no viene especificado, se calcula automáticamente
        if status:
            self.status = status
        else:
            self.recalculate_status()

    def recalculate_status(self) -> str:
        """
        Calcula el estatus actual del producto según la comparación entre Stock Teórico y Físico.
        - 'Nuevo fuera de catálogo': Si fue agregado como nuevo durante la auditoría.
        - 'En inventario': Conteo coincide o aún no se realiza auditoría si teórico y físico son 0.
        - 'Faltante': El físico es menor al teórico.
        - 'Excedente': El físico es mayor al teórico.
        """
        if self.is_new_item:
            self.status = "Nuevo fuera de catálogo"
        elif self.physical_stock < self.theoretical_stock:
            self.status = "Faltante"
        elif self.physical_stock > self.theoretical_stock:
            self.status = "Excedente"
        else:
            self.status = "En inventario"
        return self.status

    @property
    def difference(self) -> float:
        """Calcula la diferencia entre el conteo físico y el registrado/teórico."""
        return self.physical_stock - self.theoretical_stock

    def to_dict(self) -> Dict[str, Any]:
        """Convierte el objeto en diccionario para exportación y presentación."""
        return {
            "Código/SKU": self.sku,
            "Descripción": self.description,
            "Categoría": self.category,
            "Stock Teórico": self.theoretical_stock,
            "Stock Físico": self.physical_stock,
            "Diferencia": self.difference,
            "Estatus": self.status,
            "Ruta Evidencia": self.photo_path,
            "Nuevo": "Sí" if self.is_new_item else "No"
        }


class InventoryManager:
    """
    Gestor principal de la base de datos interna del inventario.
    """
    def __init__(self):
        self.items: Dict[str, InventoryItem] = {}  # SKU -> InventoryItem

    def clear(self):
        """Limpia todo el inventario actual."""
        self.items.clear()

    def get_all_items(self) -> List[InventoryItem]:
        """Devuelve la lista completa de productos."""
        return list(self.items.values())

    def find_by_sku(self, sku: str) -> Optional[InventoryItem]:
        """Busca un producto por su código/SKU exacto."""
        return self.items.get(str(sku).strip())

    def search(self, query: str) -> List[InventoryItem]:
        """
        Busca productos que coincidan por SKU, descripción o categoría (búsqueda parcial).
        """
        q = str(query).strip().lower()
        if not q:
            return self.get_all_items()

        results = []
        for item in self.items.values():
            if (q in item.sku.lower() or
                q in item.description.lower() or
                q in item.category.lower()):
                results.append(item)
        return results

    def add_or_update_item(
        self,
        sku: str,
        description: str,
        category: str = "General",
        theoretical_stock: float = 0.0,
        physical_stock: float = 0.0,
        photo_path: str = "",
        is_new_item: bool = False
    ) -> InventoryItem:
        """
        Agrega un nuevo producto o actualiza sus valores si el SKU ya existe.
        """
        sku_clean = str(sku).strip()
        if sku_clean in self.items:
            item = self.items[sku_clean]
            if description:
                item.description = description
            if category:
                item.category = category
            item.theoretical_stock = float(theoretical_stock)
            if physical_stock > 0:
                item.physical_stock = float(physical_stock)
            if photo_path:
                item.photo_path = photo_path
            item.recalculate_status()
            return item
        else:
            item = InventoryItem(
                sku=sku_clean,
                description=description,
                category=category,
                theoretical_stock=theoretical_stock,
                physical_stock=physical_stock,
                photo_path=photo_path,
                is_new_item=is_new_item
            )
            self.items[sku_clean] = item
            return item

    def update_physical_count(self, sku: str, physical_count: float, photo_path: str = "") -> Optional[InventoryItem]:
        """
        Actualiza el conteo físico de un producto existente y opcionalmente su evidencia fotográfica.
        """
        item = self.find_by_sku(sku)
        if item:
            item.physical_stock = float(physical_count)
            if photo_path:
                item.photo_path = photo_path
            item.recalculate_status()
            return item
        return None

    def load_from_dataframe(self, df: pd.DataFrame) -> int:
        """
        Carga datos desde un DataFrame de Pandas (proveniente de Excel o CSV).
        Identifica de forma inteligente los nombres de las columnas.
        """
        count = 0
        # Mapeo flexible de nombres de columnas
        col_map = {}
        for col in df.columns:
            c_norm = str(col).strip().lower()
            if any(k in c_norm for k in ['sku', 'codigo', 'código', 'id', 'clave']):
                col_map['sku'] = col
            elif any(k in c_norm for k in ['descripcion', 'descripción', 'nombre', 'producto', 'item']):
                col_map['description'] = col
            elif any(k in c_norm for k in ['categoria', 'categoría', 'grupo', 'famila', 'seccion']):
                col_map['category'] = col
            elif any(k in c_norm for k in ['teorico', 'teórico', 'registrado', 'sistema', 'stock', 'cantidad']):
                col_map['theoretical_stock'] = col
            elif any(k in c_norm for k in ['fisico', 'físico', 'contado', 'real']):
                col_map['physical_stock'] = col
            elif any(k in c_norm for k in ['foto', 'evidencia', 'imagen', 'ruta']):
                col_map['photo_path'] = col

        for idx, row in df.iterrows():
            # SKU obligatorio o autogenerado
            sku_val = str(row[col_map['sku']]).strip() if 'sku' in col_map and pd.notna(row[col_map['sku']]) else f"PROD-{idx+1:04d}"
            desc_val = str(row[col_map['description']]).strip() if 'description' in col_map and pd.notna(row[col_map['description']]) else f"Producto {sku_val}"
            cat_val = str(row[col_map['category']]).strip() if 'category' in col_map and pd.notna(row[col_map['category']]) else "General"

            try:
                teo_val = float(row[col_map['theoretical_stock']]) if 'theoretical_stock' in col_map and pd.notna(row[col_map['theoretical_stock']]) else 0.0
            except ValueError:
                teo_val = 0.0

            try:
                fis_val = float(row[col_map['physical_stock']]) if 'physical_stock' in col_map and pd.notna(row[col_map['physical_stock']]) else 0.0
            except ValueError:
                fis_val = 0.0

            photo_val = str(row[col_map['photo_path']]).strip() if 'photo_path' in col_map and pd.notna(row[col_map['photo_path']]) else ""

            self.add_or_update_item(
                sku=sku_val,
                description=desc_val,
                category=cat_val,
                theoretical_stock=teo_val,
                physical_stock=fis_val,
                photo_path=photo_val,
                is_new_item=False
            )
            count += 1
        return count

    def load_from_excel_or_csv(self, file_path: str) -> int:
        """
        Carga inventario desde un archivo .xlsx, .xls o .csv.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Archivo no encontrado: {file_path}")

        ext = os.path.splitext(file_path)[1].lower()
        if ext in ['.xlsx', '.xls']:
            df = pd.read_excel(file_path)
        elif ext == '.csv':
            df = pd.read_csv(file_path)
        else:
            raise ValueError("Formato de archivo no soportado. Use .xlsx, .xls o .csv")

        return self.load_from_dataframe(df)

    def import_from_xml_items(self, xml_items: List[Dict[str, Any]]) -> int:
        """
        Importa lista de items extraídos de XML. Si el SKU ya existe, incrementa el Stock Teórico.
        Si no existe, agrega el nuevo producto.
        """
        added_count = 0
        for item in xml_items:
            sku = item['sku']
            desc = item['description']
            cat = item.get('category', 'Importado de XML')
            qty = item.get('quantity', 1.0)

            existing = self.find_by_sku(sku)
            if existing:
                existing.theoretical_stock += qty
                existing.recalculate_status()
            else:
                self.add_or_update_item(
                    sku=sku,
                    description=desc,
                    category=cat,
                    theoretical_stock=qty,
                    physical_stock=0.0,
                    is_new_item=False
                )
            added_count += 1
        return added_count

    def to_dataframe(self) -> pd.DataFrame:
        """
        Genera un pandas DataFrame con la lista completa de inventario.
        """
        data = [item.to_dict() for item in self.get_all_items()]
        return pd.DataFrame(data)
