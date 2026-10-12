"""
Suite de Pruebas Unitarias e Integración para el Sistema de Control de Inventarios.
Prueba todas las funcionalidades principales:
- Modelo de Datos y Cálculo de Estatus
- Parser XML/CFDI
- Búsqueda Multifunción y Evidencias
- Exportación a Excel y PDF
"""

import unittest
import os
import tempfile
import pandas as pd

from inventory_model import InventoryManager, InventoryItem
from xml_parser import XMLInventoryParser
from search_and_evidence import SearchAndEvidenceManager
from pdf_generator import InventoryReportGenerator


class TestInventorySystem(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.mgr = InventoryManager()
        self.evidence_mgr = SearchAndEvidenceManager(self.mgr, evidence_dir=self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_inventory_item_status(self):
        # Item en regla
        item1 = InventoryItem("SKU1", "Item 1", "Cat A", 10, 10)
        self.assertEqual(item1.status, "En inventario")
        self.assertEqual(item1.difference, 0)

        # Item Faltante
        item2 = InventoryItem("SKU2", "Item 2", "Cat A", 10, 7)
        self.assertEqual(item2.status, "Faltante")
        self.assertEqual(item2.difference, -3)

        # Item Excedente
        item3 = InventoryItem("SKU3", "Item 3", "Cat A", 5, 8)
        self.assertEqual(item3.status, "Excedente")
        self.assertEqual(item3.difference, 3)

        # Item Nuevo
        item4 = InventoryItem("SKU4", "Item 4", "Cat B", 0, 2, is_new_item=True)
        self.assertEqual(item4.status, "Nuevo fuera de catálogo")

    def test_excel_loading(self):
        excel_path = os.path.join(self.temp_dir.name, "test_data.xlsx")
        df = pd.DataFrame([
            {"SKU": "A001", "Descripción": "Silla de Oficina", "Categoría": "Muebles", "Teórico": 20, "Físico": 18},
            {"SKU": "A002", "Descripción": "Escritorio", "Categoría": "Muebles", "Teórico": 5, "Físico": 5}
        ])
        df.to_excel(excel_path, index=False)

        count = self.mgr.load_from_excel_or_csv(excel_path)
        self.assertEqual(count, 2)

        silla = self.mgr.find_by_sku("A001")
        self.assertIsNotNone(silla)
        self.assertEqual(silla.status, "Faltante")

    def test_xml_parsing(self):
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
        <cfdi:Comprobante xmlns:cfdi="http://www.sat.gob.mx/cfd/4">
            <cfdi:Conceptos>
                <cfdi:Concepto NoIdentificacion="XML-999" Descripcion="Monitor Samsung 24" Cantidad="3" ClaveUnidad="H87"/>
            </cfdi:Conceptos>
        </cfdi:Comprobante>
        """
        xml_path = os.path.join(self.temp_dir.name, "test_factura.xml")
        with open(xml_path, "w", encoding="utf-8") as f:
            f.write(xml_content)

        items = XMLInventoryParser.parse_xml_invoice(xml_path)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["sku"], "XML-999")
        self.assertEqual(items[0]["quantity"], 3.0)

        imported_count = self.mgr.import_from_xml_items(items)
        self.assertEqual(imported_count, 1)
        self.assertIsNotNone(self.mgr.find_by_sku("XML-999"))

    def test_search_and_evidence(self):
        self.mgr.add_or_update_item("SKU-AUDIO", "Auriculares Inalámbricos Bluetooth", "Audio", 10, 10)

        # Búsqueda por código
        bc_item = self.evidence_mgr.search_by_barcode("SKU-AUDIO")
        self.assertIsNotNone(bc_item)

        # Búsqueda por voz
        v_items = self.evidence_mgr.search_by_voice("Auriculares")
        self.assertEqual(len(v_items), 1)

        # Evidencia fotográfica simulada
        sim_photo = self.evidence_mgr.capture_simulated_camera_photo("SKU-AUDIO")
        self.assertTrue(os.path.exists(sim_photo))
        self.assertEqual(self.mgr.find_by_sku("SKU-AUDIO").photo_path, sim_photo)

    def test_report_generation(self):
        self.mgr.add_or_update_item("R001", "Item R1", "Cat R", 10, 8)

        excel_out = os.path.join(self.temp_dir.name, "reporte.xlsx")
        pdf_out = os.path.join(self.temp_dir.name, "reporte.pdf")

        InventoryReportGenerator.export_to_excel(self.mgr, excel_out)
        InventoryReportGenerator.export_to_pdf(self.mgr, pdf_out)

        self.assertTrue(os.path.exists(excel_out))
        self.assertTrue(os.path.exists(pdf_out))
        self.assertGreater(os.path.getsize(excel_out), 1000)
        self.assertGreater(os.path.getsize(pdf_out), 1000)


if __name__ == "__main__":
    unittest.main()
