"""
Punto de Entrada Principal de la Aplicación de Control de Inventarios Mensuales.
Ejecuta la interfaz gráfica de usuario (GUI) desarrollada en CustomTkinter / Tkinter.
"""

import sys
import os

# Asegurar que el directorio de la aplicación está en el path de Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app_gui import InventoryAppGUI


def main():
    """Inicializa y arranca la aplicación gráfica."""
    print("Iniciando Sistema de Control de Inventarios Mensuales...")
    app = InventoryAppGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
