# 📦 Sistema de Control de Inventarios Mensuales v1.0

Aplicación gráfica completa, robusta y automatizada para la gestión, auditoría y control de inventarios mensuales.

---

## 🚀 Guía Rápida de Instalación y Ejecución en 3 Pasos

Siga estos sencillos pasos para instalar y ejecutar la aplicación sin necesidad de modificar código.

### Paso 1: Instalar Python
Si aún no tiene instalado Python en su computadora:
- Descargue e instale **Python 3.10 o superior** desde el sitio web oficial: [https://www.python.org/downloads/](https://www.python.org/downloads/)
- **Importante durante la instalación:** Asegúrese de marcar la casilla **"Add Python to PATH"** (Agregar Python al PATH).

---

### Paso 2: Instalar las Librerías Requeridas
Abra una ventana de terminal o símbolo del sistema (CMD / PowerShell en Windows, o Terminal en macOS / Linux) en la carpeta del proyecto y ejecute el siguiente comando:

```bash
pip install pandas openpyxl reportlab pillow customtkinter opencv-python-headless
```

---

### Paso 3: Ejecutar el Programa
Para iniciar la aplicación gráfica, ejecute en la terminal el siguiente comando:

```bash
python main.py
```
*(En macOS o Linux puede ser `python3 main.py`)*

---

## 🌟 Características Principales del Sistema

1. **Interfaz Gráfica de Usuario (GUI) Amigable (CustomTkinter):**
   - Pestañas intuitivas para Carga de Datos, Búsqueda/Verificación, Tabla General de Inventario y Generación de Reportes.

2. **Carga y Sincronización de Datos:**
   - **Excel y CSV:** Carga inicial automática detectando encabezados de columnas (Código/SKU, Descripción, Categoría, Stock Teórico, Físico).
   - **XML / Facturas CFDI:** Extracción automática de productos y cantidades desde archivos de facturas electrónicas XML (SAT CFDI 3.3 y 4.0).

3. **Búsqueda Multifunción y Verificación:**
   - **Código de Barras / QR:** Optimizado para lectores de código de barras USB/Bluetooth o entrada manual rápida.
   - **Búsqueda por Foto:** Identificación por coincidencia o selección de imagen del producto.
   - **Búsqueda por Audio / Voz:** Entrada optimizada para búsquedas o dictado.
   - **Agregar al inventario como nuevo:** Opción automática al detectar productos no registrados en el catálogo base.

4. **Captura de Evidencias Fotográficas:**
   - Permite vincular y guardar fotos de evidencia para cada producto en la carpeta `evidencias/`.

5. **Reportes Profesionales (Excel y PDF):**
   - **Excel (.xlsx):** Exportación completa con cálculos de diferencias y estatus.
   - **PDF Ejecutivo:** Reporte con diseño limpio para auditorías e impresión, con resúmenes, tablas de faltantes y sección formal de firmas.

---

## 📁 Estructura del Código

- `main.py`: Punto de entrada principal de la aplicación.
- `app_gui.py`: Interfaz gráfica interactiva basada en CustomTkinter.
- `inventory_model.py`: Lógica de datos, cálculo de estatus y gestión de inventario.
- `xml_parser.py`: Lector y extractor de conceptos de facturas y XML.
- `search_and_evidence.py`: Módulo de búsquedas avanzadas y gestión de evidencias fotográficas.
- `pdf_generator.py`: Motor de exportación a hojas de cálculo Excel y reportes en PDF con ReportLab.
- `test_inventory.py`: Pruebas unitarias y de integración automatizadas.
