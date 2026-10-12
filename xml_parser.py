"""
Módulo de procesamiento de archivos XML para la alimentación de inventario.
Soporta archivos XML de facturas electrónicas (CFDI 3.3 y 4.0 del SAT)
así como estructuras XML genéricas de productos.
"""

import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional
import os


class XMLInventoryParser:
    """
    Parser especializado para extraer productos/conceptos desde archivos XML.
    """

    @staticmethod
    def parse_xml_invoice(file_path: str) -> List[Dict[str, Any]]:
        """
        Lee un archivo XML (CFDI o genérico) y extrae la lista de productos/conceptos.

        Retorna una lista de diccionarios con la estructura:
        [
            {
                'sku': '12345',
                'description': 'Laptop Dell Vostro',
                'category': 'Electrónica',
                'quantity': 5.0,
                'unit': 'PZA'
            }, ...
        ]
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"El archivo XML no existe: {file_path}")

        tree = ET.parse(file_path)
        root = tree.getroot()

        extracted_items: List[Dict[str, Any]] = []

        # Limpiar namespaces para facilitar búsqueda en XML
        for elem in root.iter():
            if '}' in elem.tag:
                elem.tag = elem.tag.split('}', 1)[1]  # Elimina el prefijo del namespace

        # 1. Intentar parsear como CFDI (Factura SAT México 3.3 / 4.0)
        conceptos = root.findall('.//Concepto')
        if conceptos:
            for idx, concepto in enumerate(conceptos, start=1):
                sku = (
                    concepto.attrib.get('NoIdentificacion') or
                    concepto.attrib.get('ClaveProdServ') or
                    f"CFDI-PROD-{idx:03d}"
                ).strip()

                description = concepto.attrib.get('Descripcion', 'Producto sin descripción').strip()
                cantidad_str = concepto.attrib.get('Cantidad', '1')
                try:
                    cantidad = float(cantidad_str)
                except ValueError:
                    cantidad = 1.0

                unidad = concepto.attrib.get('Unidad') or concepto.attrib.get('ClaveUnidad') or 'Pieza'

                extracted_items.append({
                    'sku': sku,
                    'description': description,
                    'category': 'Importado de XML/CFDI',
                    'quantity': cantidad,
                    'unit': unidad
                })
            return extracted_items

        # 2. Intentar parsear como XML genérico de inventario/productos
        # Busca etiquetas comunes como <producto>, <item>, <artículo>
        items = root.findall('.//producto') or root.findall('.//item') or root.findall('.//articulo') or root.findall('.//product')

        if items:
            for idx, item in enumerate(items, start=1):
                sku_elem = item.find('sku') or item.find('codigo') or item.find('code') or item.find('clave')
                desc_elem = item.find('descripcion') or item.find('nombre') or item.find('description') or item.find('name')
                cat_elem = item.find('categoria') or item.find('category')
                cant_elem = item.find('cantidad') or item.find('quantity') or item.find('stock')

                sku = sku_elem.text.strip() if sku_elem is not None and sku_elem.text else f"XML-PROD-{idx:03d}"
                description = desc_elem.text.strip() if desc_elem is not None and desc_elem.text else f"Producto XML #{idx}"
                category = cat_elem.text.strip() if cat_elem is not None and cat_elem.text else "General"

                try:
                    cantidad = float(cant_elem.text.strip()) if cant_elem is not None and cant_elem.text else 1.0
                except ValueError:
                    cantidad = 1.0

                extracted_items.append({
                    'sku': sku,
                    'description': description,
                    'category': category,
                    'quantity': cantidad,
                    'unit': 'Pieza'
                })
            return extracted_items

        # 3. Si no hay nodos de lista, intentar leer atributos directos de la raíz
        return extracted_items
