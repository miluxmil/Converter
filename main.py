#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# CONVERTER - Herramienta integral de conversión y gestión multimedia
# Copyright (C) 2026 </[M]iLu{×}_> | DNP
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import sys
import os
import subprocess

# --- MECANISMO DE BOOTSTRAP PARA RICH ---
try:
    import rich
except ImportError:
    print("[!] La librería 'rich' no está instalada.")
    print("[*] Intentando instalación automática...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "rich"])
        print("[V] 'rich' instalado correctamente. Iniciando...")
    except Exception as e:
        print(f"[X] No se pudo instalar 'rich' automáticamente: {e}")
        print("[i] Por favor, ejecuta: pip install rich")
        sys.exit(1)
# ---------------------------------------

# Añadir el directorio actual al path para encontrar el paquete 'app'
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import Converter

if __name__ == "__main__":
    try:
        app = Converter()
        
        # Modo de verificación rápida (autofix ya ocurre en el __init__ del core)
        if len(sys.argv) > 1 and sys.argv[1] == "--check":
            print("\n[V] Entorno verificado y reparado.")
            sys.exit(0)
            
        app.main_menu()
    except KeyboardInterrupt:
        # Al presionar Ctrl+C, ejecutamos la salida original
        if 'app' in locals():
            app.exit_app()
        else:
            print("\n\nSaliendo...")
            sys.exit(0)
