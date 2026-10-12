"""
Interfaz Gráfica de Usuario (GUI) para el Sistema de Control de Inventarios Mensuales.
Desarrollada con CustomTkinter (con soporte para Tkinter estándar).
Incluye pestañas de:
1. Carga de Datos y XML
2. Búsqueda y Verificación Multifunción (Código de Barras, Foto, Voz, Conteo, Evidencias)
3. Vista General del Inventario
4. Generación de Reportes Ejecutivos (Excel y PDF)
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional

import customtkinter as ctk
from PIL import Image, ImageTk

from inventory_model import InventoryManager, InventoryItem
from xml_parser import XMLInventoryParser
from pdf_generator import InventoryReportGenerator
from search_and_evidence import SearchAndEvidenceManager


# Configurar tema gráfico CustomTkinter
ctk.set_appearance_mode("System")  # "System", "Dark", "Light"
ctk.set_default_color_theme("blue")  # "blue", "green", "dark-blue"


class InventoryAppGUI(ctk.CTk):
    """
    Aplicación Principal con Interfaz Gráfica de Usuario en Español.
    """
    def __init__(self):
        super().__init__()

        self.title("Sistema de Control de Inventarios Mensuales v1.0")
        self.geometry("1100x700")
        self.minsize(950, 600)

        # Inicializar Administrador de Inventario y Evidencias
        self.inventory_mgr = InventoryManager()
        self.evidence_mgr = SearchAndEvidenceManager(self.inventory_mgr, evidence_dir="evidencias")

        # Cargar datos de prueba iniciales para demostración inmediata
        self._load_demo_data()

        # Construir Interfaz de Usuario
        self._create_widgets()

    def _load_demo_data(self):
        """Carga algunos productos de demostración iniciales."""
        self.inventory_mgr.add_or_update_item("SKU-101", "Laptop Dell Vostro 3510 15.6\"", "Cómputo", theoretical_stock=10, physical_stock=10)
        self.inventory_mgr.add_or_update_item("SKU-102", "Monitor LG 27\" IPS Full HD", "Monitores", theoretical_stock=15, physical_stock=12)
        self.inventory_mgr.add_or_update_item("SKU-103", "Teclado Inalámbrico Logitech K380", "Accesorios", theoretical_stock=8, physical_stock=8)
        self.inventory_mgr.add_or_update_item("SKU-104", "Silla Ergonómica Ejecutiva", "Mobiliario", theoretical_stock=5, physical_stock=0)

    def _create_widgets(self):
        """Crea la estructura principal de pestañas de la aplicación."""

        # Encabezado superior
        self.header_frame = ctk.CTkFrame(self, corner_radius=0, fg_color=("#1A365D", "#0F172A"))
        self.header_frame.pack(fill="x", side="top")

        self.header_label = ctk.CTkLabel(
            self.header_frame,
            text="📦 SISTEMA DE CONTROL Y AUDITORÍA DE INVENTARIOS MENSUALES",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="white",
            anchor="w",
            padx=20,
            pady=15
        )
        self.header_label.pack(side="left")

        # Vista de Pestañas (Tabview)
        self.tabview = ctk.CTkTabview(self, width=1050, height=620)
        self.tabview.pack(fill="both", expand=True, padx=15, pady=10)

        # Crear pestañas
        self.tab_data = self.tabview.add("1. Carga de Datos y XML")
        self.tab_search = self.tabview.add("2. Búsqueda y Verificación")
        self.tab_table = self.tabview.add("3. Tabla de Inventario")
        self.tab_reports = self.tabview.add("4. Reportes (Excel / PDF)")

        # Configurar cada pestaña
        self._setup_data_tab()
        self._setup_search_tab()
        self._setup_table_tab()
        self._setup_reports_tab()

    # ==========================================
    # PESTAÑA 1: CARGA DE DATOS Y XML
    # ==========================================
    def _setup_data_tab(self):
        grid_frame = ctk.CTkFrame(self.tab_data)
        grid_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Sección 1: Carga de Excel / CSV
        excel_box = ctk.CTkFrame(grid_frame)
        excel_box.pack(fill="x", padx=15, pady=15)

        ctk.CTkLabel(
            excel_box,
            text="📊 Carga Inicial de Base de Datos (Excel / CSV)",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 5))

        ctk.CTkLabel(
            excel_box,
            text="Seleccione un archivo de Excel (.xlsx) o CSV con el catálogo e inventario inicial.",
            text_color="gray"
        ).pack(anchor="w", padx=15, pady=(0, 10))

        btn_excel = ctk.CTkButton(
            excel_box,
            text="📁 Seleccionar Archivo Excel / CSV",
            command=self._cmd_load_excel,
            fg_color="#2B6CB0",
            hover_color="#2C5282"
        )
        btn_excel.pack(anchor="w", padx=15, pady=(0, 15))

        # Sección 2: Alimentación por XML (CFDI / Facturas)
        xml_box = ctk.CTkFrame(grid_frame)
        xml_box.pack(fill="x", padx=15, pady=15)

        ctk.CTkLabel(
            xml_box,
            text="📄 Importar Archivo XML (Facturas / CFDI)",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 5))

        ctk.CTkLabel(
            xml_box,
            text="Alimente el inventario extrayendo automáticamente conceptos y productos desde facturas XML.",
            text_color="gray"
        ).pack(anchor="w", padx=15, pady=(0, 10))

        btn_xml = ctk.CTkButton(
            xml_box,
            text="📥 Importar Factura XML",
            command=self._cmd_load_xml,
            fg_color="#2B6CB0",
            hover_color="#2C5282"
        )
        btn_xml.pack(anchor="w", padx=15, pady=(0, 15))

        # Indicador de estado de carga
        self.lbl_data_status = ctk.CTkLabel(
            grid_frame,
            text=f"Estado actual: {len(self.inventory_mgr.get_all_items())} productos registrados en inventario.",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#2B6CB0"
        )
        self.lbl_data_status.pack(anchor="w", padx=15, pady=20)

    def _cmd_load_excel(self):
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo de Excel o CSV",
            filetypes=[("Archivos Excel/CSV", "*.xlsx *.xls *.csv"), ("Todos los archivos", "*.*")]
        )
        if not file_path:
            return

        try:
            count = self.inventory_mgr.load_from_excel_or_csv(file_path)
            self._refresh_all_views()
            messagebox.showinfo("Éxito", f"Se cargaron correctamente {count} productos desde el archivo.")
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al cargar el archivo:\n{str(e)}")

    def _cmd_load_xml(self):
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo XML",
            filetypes=[("Archivos XML", "*.xml"), ("Todos los archivos", "*.*")]
        )
        if not file_path:
            return

        try:
            items = XMLInventoryParser.parse_xml_invoice(file_path)
            if not items:
                messagebox.showwarning("Aviso", "No se encontraron conceptos/productos en el archivo XML.")
                return

            count = self.inventory_mgr.import_from_xml_items(items)
            self._refresh_all_views()
            messagebox.showinfo("Éxito", f"Se importaron {count} productos/conceptos del XML al inventario.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al procesar el archivo XML:\n{str(e)}")

    # ==========================================
    # PESTAÑA 2: BÚSQUEDA Y VERIFICACIÓN
    # ==========================================
    def _setup_search_tab(self):
        main_search = ctk.CTkFrame(self.tab_search)
        main_search.pack(fill="both", expand=True, padx=15, pady=15)

        # Sub-panel de opciones de búsqueda
        search_methods_frame = ctk.CTkFrame(main_search)
        search_methods_frame.pack(fill="x", padx=15, pady=10)

        ctk.CTkLabel(
            search_methods_frame,
            text="🔍 Búsqueda Multifunción de Productos",
            font=ctk.CTkFont(size=15, weight="bold")
        ).pack(anchor="w", padx=15, pady=(10, 5))

        # 1. Entrada de Código de Barras / QR
        bc_frame = ctk.CTkFrame(search_methods_frame, fg_color="transparent")
        bc_frame.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(bc_frame, text="1. Código de Barras / SKU / QR:", width=220, anchor="w").pack(side="left")
        self.entry_barcode = ctk.CTkEntry(bc_frame, placeholder_text="Escanee o escriba el código...", width=300)
        self.entry_barcode.pack(side="left", padx=10)
        self.entry_barcode.bind("<Return>", lambda e: self._cmd_search_barcode())

        btn_bc_search = ctk.CTkButton(bc_frame, text="Buscar Código", command=self._cmd_search_barcode, width=120)
        btn_bc_search.pack(side="left")

        # 2. Búsqueda por Foto / Imagen
        img_frame = ctk.CTkFrame(search_methods_frame, fg_color="transparent")
        img_frame.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(img_frame, text="2. Búsqueda por Foto / Imagen:", width=220, anchor="w").pack(side="left")
        btn_img_search = ctk.CTkButton(img_frame, text="📷 Adjuntar Imagen para Identificar", command=self._cmd_search_image, width=230)
        btn_img_search.pack(side="left", padx=10)

        # 3. Búsqueda por Voz / Audio
        voice_frame = ctk.CTkFrame(search_methods_frame, fg_color="transparent")
        voice_frame.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(voice_frame, text="3. Búsqueda por Audio / Voz:", width=220, anchor="w").pack(side="left")
        self.entry_voice = ctk.CTkEntry(voice_frame, placeholder_text="Simular dictado de voz (ej. 'Laptop Dell')...", width=300)
        self.entry_voice.pack(side="left", padx=10)
        btn_voice_search = ctk.CTkButton(voice_frame, text="🎙️ Dictar / Buscar Voz", command=self._cmd_search_voice, width=150)
        btn_voice_search.pack(side="left")

        # --- SECCIÓN DE RESULTADO Y CONTEO FÍSICO ---
        self.result_card = ctk.CTkFrame(main_search)
        self.result_card.pack(fill="both", expand=True, padx=15, pady=10)

        ctk.CTkLabel(
            self.result_card,
            text="📋 Detalle del Producto Encontrado / Formulario de Verificación",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=15, pady=(10, 5))

        fields_frame = ctk.CTkFrame(self.result_card, fg_color="transparent")
        fields_frame.pack(fill="x", padx=15, pady=10)

        # Fila 1: Código y Categoría
        ctk.CTkLabel(fields_frame, text="Código / SKU:").grid(row=0, column=0, sticky="w", pady=5)
        self.txt_res_sku = ctk.CTkEntry(fields_frame, width=200)
        self.txt_res_sku.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        ctk.CTkLabel(fields_frame, text="Categoría:").grid(row=0, column=2, sticky="w", pady=5)
        self.txt_res_cat = ctk.CTkEntry(fields_frame, width=200)
        self.txt_res_cat.grid(row=0, column=3, padx=10, pady=5, sticky="w")

        # Fila 2: Descripción
        ctk.CTkLabel(fields_frame, text="Descripción:").grid(row=1, column=0, sticky="w", pady=5)
        self.txt_res_desc = ctk.CTkEntry(fields_frame, width=520)
        self.txt_res_desc.grid(row=1, column=1, columnspan=3, padx=10, pady=5, sticky="w")

        # Fila 3: Stocks
        ctk.CTkLabel(fields_frame, text="Stock Teórico / Registrado:").grid(row=2, column=0, sticky="w", pady=5)
        self.txt_res_teo = ctk.CTkEntry(fields_frame, width=200)
        self.txt_res_teo.grid(row=2, column=1, padx=10, pady=5, sticky="w")

        ctk.CTkLabel(fields_frame, text="Stock Físico (Contado):").grid(row=2, column=2, sticky="w", pady=5)
        self.txt_res_fis = ctk.CTkEntry(fields_frame, width=200, fg_color=("#EBF8FF", "#1A365D"))
        self.txt_res_fis.grid(row=2, column=3, padx=10, pady=5, sticky="w")

        # Fila 4: Estatus y Evidencia
        ctk.CTkLabel(fields_frame, text="Estatus Actual:").grid(row=3, column=0, sticky="w", pady=5)
        self.lbl_res_status = ctk.CTkLabel(fields_frame, text="-", font=ctk.CTkFont(weight="bold"), text_color="#3182CE")
        self.lbl_res_status.grid(row=3, column=1, padx=10, pady=5, sticky="w")

        ctk.CTkLabel(fields_frame, text="Evidencia Fotográfica:").grid(row=3, column=2, sticky="w", pady=5)
        self.lbl_res_photo = ctk.CTkLabel(fields_frame, text="Sin Foto", text_color="gray")
        self.lbl_res_photo.grid(row=3, column=3, padx=10, pady=5, sticky="w")

        # Botones de Acción sobre la Verificación
        action_bar = ctk.CTkFrame(self.result_card, fg_color="transparent")
        action_bar.pack(fill="x", padx=15, pady=15)

        btn_save_count = ctk.CTkButton(
            action_bar,
            text="💾 Actualizar Conteo Físico",
            command=self._cmd_save_physical_count,
            fg_color="#2B6CB0",
            hover_color="#2C5282"
        )
        btn_save_count.pack(side="left", padx=5)

        btn_attach_photo = ctk.CTkButton(
            action_bar,
            text="📸 Adjuntar / Capturar Foto Evidencia",
            command=self._cmd_attach_photo,
            fg_color="#D69E2E",
            hover_color="#B7791F"
        )
        btn_attach_photo.pack(side="left", padx=5)

        btn_add_new = ctk.CTkButton(
            action_bar,
            text="➕ Agregar al inventario como nuevo",
            command=self._cmd_add_as_new_catalog,
            fg_color="#38A169",
            hover_color="#2F855A"
        )
        btn_add_new.pack(side="left", padx=5)

    def _display_item_in_form(self, item: InventoryItem):
        """Muestra la información de un objeto InventoryItem en las cajas de texto."""
        self.txt_res_sku.delete(0, tk.END)
        self.txt_res_sku.insert(0, item.sku)

        self.txt_res_desc.delete(0, tk.END)
        self.txt_res_desc.insert(0, item.description)

        self.txt_res_cat.delete(0, tk.END)
        self.txt_res_cat.insert(0, item.category)

        self.txt_res_teo.delete(0, tk.END)
        self.txt_res_teo.insert(0, str(item.theoretical_stock))

        self.txt_res_fis.delete(0, tk.END)
        self.txt_res_fis.insert(0, str(item.physical_stock))

        self.lbl_res_status.configure(text=item.status)

        photo_info = os.path.basename(item.photo_path) if item.photo_path else "Sin Foto"
        self.lbl_res_photo.configure(text=photo_info)

    def _cmd_search_barcode(self):
        sku = self.entry_barcode.get().strip()
        if not sku:
            messagebox.showwarning("Atención", "Ingrese o escanee un código de barras / SKU.")
            return

        item = self.evidence_mgr.search_by_barcode(sku)
        if item:
            self._display_item_in_form(item)
        else:
            ans = messagebox.askyesno(
                "Producto No Encontrado",
                f"El código '{sku}' NO está registrado en el inventario actual.\n\n¿Desea agregarlo como producto NUEVO fuera de catálogo?"
            )
            if ans:
                self.txt_res_sku.delete(0, tk.END)
                self.txt_res_sku.insert(0, sku)
                self.txt_res_desc.delete(0, tk.END)
                self.txt_res_desc.insert(0, f"Producto Nuevo {sku}")
                self.txt_res_cat.delete(0, tk.END)
                self.txt_res_cat.insert(0, "Nuevo fuera de catálogo")
                self.txt_res_teo.delete(0, tk.END)
                self.txt_res_teo.insert(0, "0")
                self.txt_res_fis.delete(0, tk.END)
                self.txt_res_fis.insert(0, "1")
                self.lbl_res_status.configure(text="Nuevo fuera de catálogo")

    def _cmd_search_image(self):
        img_path = filedialog.askopenfilename(
            title="Seleccionar foto del producto para búsqueda",
            filetypes=[("Imágenes", "*.jpg *.png *.jpeg *.webp"), ("Todos los archivos", "*.*")]
        )
        if not img_path:
            return

        matches = self.evidence_mgr.search_by_image(img_path)
        if matches:
            self._display_item_in_form(matches[0])
            messagebox.showinfo("Búsqueda por Imagen", f"Se encontró coincidencia con el producto: {matches[0].description}")
        else:
            messagebox.showinfo("Búsqueda por Imagen", "No se encontró coincidencia automática con la imagen selecccionada.")

    def _cmd_search_voice(self):
        query = self.entry_voice.get().strip()
        if not query:
            messagebox.showwarning("Atención", "Escriba o simule un comando de voz en el campo.")
            return

        matches = self.evidence_mgr.search_by_voice(query)
        if matches:
            self._display_item_in_form(matches[0])
            messagebox.showinfo("Búsqueda por Voz", f"Coincidencia encontrada: {matches[0].description}")
        else:
            messagebox.showwarning("Búsqueda por Voz", f"No se encontraron productos para el término: '{query}'")

    def _cmd_save_physical_count(self):
        sku = self.txt_res_sku.get().strip()
        if not sku:
            messagebox.showwarning("Atención", "No hay ningún SKU seleccionado para actualizar.")
            return

        try:
            phys_count = float(self.txt_res_fis.get().strip())
        except ValueError:
            messagebox.showerror("Error", "Ingrese una cantidad numérica válida para el Stock Físico.")
            return

        item = self.inventory_mgr.update_physical_count(sku, phys_count)
        if item:
            self._display_item_in_form(item)
            self._refresh_all_views()
            messagebox.showinfo("Éxito", f"Stock físico de '{sku}' actualizado a {phys_count}.")
        else:
            messagebox.showerror("Error", "El SKU no se encuentra en el registro actual.")

    def _cmd_attach_photo(self):
        sku = self.txt_res_sku.get().strip()
        if not sku:
            messagebox.showwarning("Atención", "Seleccione un producto antes de adjuntar una foto.")
            return

        img_path = filedialog.askopenfilename(
            title="Seleccionar evidencia fotográfica",
            filetypes=[("Imágenes", "*.jpg *.png *.jpeg"), ("Todos los archivos", "*.*")]
        )

        if img_path:
            try:
                saved_path = self.evidence_mgr.save_photo_evidence(img_path, sku)
                self.lbl_res_photo.configure(text=os.path.basename(saved_path))
                self._refresh_all_views()
                messagebox.showinfo("Evidencia Guardada", f"Foto de evidencia asociada correctamente a {sku}.")
            except Exception as e:
                messagebox.showerror("Error", f"Error al guardar foto: {str(e)}")
        else:
            # Opción de foto simulada por cámara
            ans = messagebox.askyesno("Captura de Cámara", "¿Desea tomar/generar una foto instantánea simulada desde la cámara?")
            if ans:
                saved_path = self.evidence_mgr.capture_simulated_camera_photo(sku)
                self.lbl_res_photo.configure(text=os.path.basename(saved_path))
                self._refresh_all_views()
                messagebox.showinfo("Evidencia Capturada", f"Foto capturada correctamente para {sku}.")

    def _cmd_add_as_new_catalog(self):
        sku = self.txt_res_sku.get().strip()
        desc = self.txt_res_desc.get().strip()
        cat = self.txt_res_cat.get().strip() or "Nuevo fuera de catálogo"

        if not sku or not desc:
            messagebox.showwarning("Campos Incompletos", "Por favor ingrese al menos el SKU y la Descripción.")
            return

        try:
            phys_count = float(self.txt_res_fis.get().strip() or 1.0)
        except ValueError:
            phys_count = 1.0

        item = self.inventory_mgr.add_or_update_item(
            sku=sku,
            description=desc,
            category=cat,
            theoretical_stock=0.0,
            physical_stock=phys_count,
            is_new_item=True
        )

        self._display_item_in_form(item)
        self._refresh_all_views()
        messagebox.showinfo("Éxito", f"Producto '{desc}' registrado como NUEVO fuera de catálogo.")

    # ==========================================
    # PESTAÑA 3: TABLA GENERAL DE INVENTARIO
    # ==========================================
    def _setup_table_tab(self):
        frame_table = ctk.CTkFrame(self.tab_table)
        frame_table.pack(fill="both", expand=True, padx=15, pady=15)

        # Barra de Filtro / Búsqueda rápida
        filter_bar = ctk.CTkFrame(frame_table)
        filter_bar.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(filter_bar, text="Filtrar Tabla:").pack(side="left", padx=10)
        self.entry_table_search = ctk.CTkEntry(filter_bar, placeholder_text="Buscar SKU, descripción...", width=250)
        self.entry_table_search.pack(side="left", padx=5)
        self.entry_table_search.bind("<KeyRelease>", lambda e: self._populate_table())

        btn_refresh = ctk.CTkButton(filter_bar, text="🔄 Actualizar Tabla", command=self._populate_table, width=120)
        btn_refresh.pack(side="left", padx=10)

        # Crear Treeview de Tkinter para la tabla
        columns = ("sku", "description", "category", "theoretical", "physical", "diff", "status", "photo")
        self.tree = ttk.Treeview(frame_table, columns=columns, show="headings", height=15)

        # Configurar encabezados
        self.tree.heading("sku", text="Código / SKU")
        self.tree.heading("description", text="Descripción")
        self.tree.heading("category", text="Categoría")
        self.tree.heading("theoretical", text="Stock Teórico")
        self.tree.heading("physical", text="Stock Físico")
        self.tree.heading("diff", text="Diferencia")
        self.tree.heading("status", text="Estatus")
        self.tree.heading("photo", text="Evidencia")

        # Configurar anchos de columna
        self.tree.column("sku", width=100, anchor="center")
        self.tree.column("description", width=250, anchor="w")
        self.tree.column("category", width=120, anchor="w")
        self.tree.column("theoretical", width=90, anchor="center")
        self.tree.column("physical", width=90, anchor="center")
        self.tree.column("diff", width=80, anchor="center")
        self.tree.column("status", width=160, anchor="center")
        self.tree.column("photo", width=100, anchor="center")

        # Scrollbars
        vsb = ttk.Scrollbar(frame_table, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(frame_table, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.pack(fill="both", expand=True, side="left", padx=(10, 0), pady=10)
        vsb.pack(side="right", fill="y", pady=10)

        self._populate_table()

    def _populate_table(self):
        """Puebla o filtra la tabla con los datos actuales del inventario."""
        for row in self.tree.get_children():
            self.tree.delete(row)

        q = self.entry_table_search.get().strip() if hasattr(self, 'entry_table_search') else ""
        items = self.inventory_mgr.search(q)

        for item in items:
            has_photo = "Sí" if item.photo_path and os.path.exists(item.photo_path) else "No"
            self.tree.insert(
                "",
                "end",
                values=(
                    item.sku,
                    item.description,
                    item.category,
                    f"{item.theoretical_stock:g}",
                    f"{item.physical_stock:g}",
                    f"{item.difference:+g}",
                    item.status,
                    has_photo
                )
            )

    # ==========================================
    # PESTAÑA 4: EXPORTACIÓN DE REPORTES
    # ==========================================
    def _setup_reports_tab(self):
        rep_frame = ctk.CTkFrame(self.tab_reports)
        rep_frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(
            rep_frame,
            text="📑 Generación de Reportes de Auditoría de Inventario",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=20, pady=(20, 10))

        ctk.CTkLabel(
            rep_frame,
            text="Exporte el informe mensual oficial en formato hoja de cálculo (Excel) o informe ejecutivo formateado (PDF).",
            text_color="gray"
        ).pack(anchor="w", padx=20, pady=(0, 20))

        # Opción 1: Exportar a Excel
        box_excel = ctk.CTkFrame(rep_frame)
        box_excel.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(box_excel, text="🟢 Exportar Inventario Completo a Excel (.xlsx)", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=15, pady=(15, 5))
        ctk.CTkLabel(box_excel, text="Genera un archivo ejecutable en Excel con conteos físicos, diferencias de inventario y estatus.", text_color="gray").pack(anchor="w", padx=15, pady=(0, 10))
        btn_exp_excel = ctk.CTkButton(
            box_excel,
            text="📊 Exportar a Excel",
            command=self._cmd_export_excel,
            fg_color="#276749",
            hover_color="#22543D"
        )
        btn_exp_excel.pack(anchor="w", padx=15, pady=(0, 15))

        # Opción 2: Reporte Ejecutivo en PDF
        box_pdf = ctk.CTkFrame(rep_frame)
        box_pdf.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(box_pdf, text="🔴 Generar Reporte Ejecutivo Formal en PDF (.pdf)", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=15, pady=(15, 5))
        ctk.CTkLabel(box_pdf, text="Crea un reporte impreso listo para auditoría con KPIs de faltantes, sobrantes y sección de firmas.", text_color="gray").pack(anchor="w", padx=15, pady=(0, 10))
        btn_exp_pdf = ctk.CTkButton(
            box_pdf,
            text="📄 Generar Reporte PDF",
            command=self._cmd_export_pdf,
            fg_color="#C53030",
            hover_color="#9B2C2C"
        )
        btn_exp_pdf.pack(anchor="w", padx=15, pady=(0, 15))

    def _cmd_export_excel(self):
        save_path = filedialog.asksaveasfilename(
            title="Guardar Reporte Excel",
            defaultextension=".xlsx",
            filetypes=[("Archivos de Excel", "*.xlsx")]
        )
        if not save_path:
            return

        try:
            InventoryReportGenerator.export_to_excel(self.inventory_mgr, save_path)
            messagebox.showinfo("Éxito", f"Reporte de Excel exportado exitosamente a:\n{save_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar Excel: {str(e)}")

    def _cmd_export_pdf(self):
        save_path = filedialog.asksaveasfilename(
            title="Guardar Reporte PDF",
            defaultextension=".pdf",
            filetypes=[("Archivos PDF", "*.pdf")]
        )
        if not save_path:
            return

        try:
            InventoryReportGenerator.export_to_pdf(self.inventory_mgr, save_path)
            messagebox.showinfo("Éxito", f"Reporte PDF de auditoría generado exitosamente en:\n{save_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar PDF: {str(e)}")

    def _refresh_all_views(self):
        """Actualiza la interfaz de usuario en todas las pestañas."""
        count = len(self.inventory_mgr.get_all_items())
        if hasattr(self, 'lbl_data_status'):
            self.lbl_data_status.configure(text=f"Estado actual: {count} productos registrados en inventario.")
        self._populate_table()
