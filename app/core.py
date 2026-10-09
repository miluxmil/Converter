#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
import json
import time
from rich.table import Table
from rich.panel import Panel

from .config import Config
from .utils import Utils
from .ui import UI, MainMenuException, BackException

# Módulos
from .modules.conversion import ConversionModule
from .modules.storage import StorageModule
from .modules.advanced import AdvancedModule
from .modules.internet import InternetModule
from .modules.notification import NotificationModule

class Converter:
    """Clase base orquestadora."""
    def __init__(self):
        self.config = Config()
        self.ui = UI(self)
        self.utils = Utils(self)
        
        # Pantalla de carga inicial
        self.ui.splash_screen()
        
        self.conversion = ConversionModule(self)
        self.storage = StorageModule(self)
        self.advanced = AdvancedModule(self)
        self.internet = InternetModule(self)
        self.notification = NotificationModule(self)
        
        # Verificar dependencias al iniciar
        self.check_dependencies()

    def check_dependencies(self):
        deps = ["ffmpeg", "mogrify", "curl", "yt-dlp", "ffprobe", "python:rich"]
        missing = [d for d in deps if not self.utils.is_installed(d)]
        
        if missing:
            self.ui.logo()
            self.ui.console.print(Panel(
                f"[bold red]Faltan dependencias críticas:[/] {', '.join(missing)}\n"
                "[bold yellow]Iniciando instalación automática...[/]",
                title="SISTEMA DE DEPENDENCIAS", border_style="red"
            ))
            time.sleep(2)
            
            # Intentar instalación automática
            if self.utils.install_missing(missing):
                # Volver a verificar después de instalar
                still_missing = [d for d in deps if not self.utils.is_installed(d)]
                if not still_missing:
                    self.ui.console.print("[bold green]✓ Todas las dependencias han sido instaladas con éxito.[/]")
                    self.utils.notify("Todas las dependencias están listas.", "SUCCESS")
                else:
                    self.ui.console.print(Panel(
                        f"[bold red]Error:[/] No se pudieron instalar: {', '.join(still_missing)}\n"
                        "Por favor, instálalas manualmente para usar el programa.",
                        title="FALLO DE INSTALACIÓN", border_style="red"
                    ))
                    self.utils.notify(f"Fallo en instalación de dependencias: {', '.join(still_missing)}", "ERROR")
                    time.sleep(4)
            else:
                self.ui.console.print("[bold red]No se pudo determinar un gestor de paquetes compatible.[/]")
                time.sleep(3)
        
        # Verificar librerías de Python (rich) - Aunque ya estamos corriendo con ella
        # Podríamos añadir más si el proyecto crece.

    def main_menu(self):
        while True:
            try:
                self.ui.logo()
                
                table = Table(show_header=False, border_style="dim", box=None)
                table.add_row("[bold green]1.[/] Audio", "[bold green]2.[/] Imagen", "[bold green]3.[/] Video")
                table.add_row("[bold green]4.[/] Extraer", "[bold green]5.[/] Almacén", "[bold green]6.[/] Avanzado")
                table.add_row("[bold green]7.[/] Internet", "[bold green]8.[/] Historial", "[bold green]9.[/] Notif.")
                table.add_row("[bold cyan]A.[/] Acerca de", "[bold yellow]00.[/] Update", "")
                table.add_row("[bold red]0.[/] Salir", "", "")

                self.ui.console.print(Panel(table, title="[bold yellow]MENÚ PRINCIPAL[/]", border_style="cyan"))
                
                opt = self.ui.prompt("Selecciona una opción").lower()
                
                if opt == '1': self.conversion.start("- Audio -", ("mp3", "wav", "ogg"))
                elif opt == '2': self.conversion.start("- Imagen -", ("jpg", "png", "webp"))
                elif opt == '3': self.conversion.start("- Video -", ("mp4", "mkv", "avi"))
                elif opt == '4': self.conversion.start("- Extraer Audio -", ("mp3", "wav", "ogg"))
                elif opt == '5': self.storage.menu()
                elif opt == '6': self.advanced.menu()
                elif opt == '7': self.internet.download()
                elif opt == '8': self.show_history()
                elif opt == '9': self.notification.menu()
                elif opt == 'a': self.about()
                elif opt == '00': self.update()
                elif opt == '0': self.exit_app()
                
            except MainMenuException: continue
            except BackException: continue

    def about(self):
        self.ui.logo()
        self.ui.console.print(Panel(
            "[bold green]CONVERTER[/]\n"
            "[bold white]Versión:[/] 1.1.0 (Modular)\n"
            "[bold white]Autor:[/] </[M]iLu{×}_> | DNP\n"
            "[bold white]Licencia:[/] GNU General Public License v3.0 o posterior (GPL-3.0-or-later)\n\n"
            "Herramienta integral de conversión y gestión multimedia para Termux.",
            title="Acerca de", border_style="green"
        ))
        input("\nPresiona ENTER para continuar...")

    def update(self):
        """Verifica y aplica actualizaciones del paquete .deb desde GitHub."""
        self.ui.logo()
        self.ui.console.print("[bold green]Buscando actualizaciones...[/]")
        time.sleep(1)

        # Crear archivo de versión local si no existe
        if not os.path.exists(self.config.CAV_FILE):
            with open(self.config.CAV_FILE, 'w') as f:
                f.write("1.1.0")

        try:
            # Descargar información de versión remota
            subprocess.run(["curl", "-s", "-o", self.config.CCV_FILE, "https://raw.githubusercontent.com/miluxmil/milux/master/CCV"], check=True)
            
            with open(self.config.CCV_FILE, 'r') as f: 
                remote_version = f.read().strip()
            with open(self.config.CAV_FILE, 'r') as f: 
                local_version = f.read().strip()

            if remote_version == local_version:
                self.ui.logo()
                self.ui.console.print(f"[bold green]Tienes la última versión (v{local_version})[/]")
                time.sleep(2)
                return

            self.ui.logo()
            self.ui.console.print("[bold green]¡Nueva versión disponible![/]")
            self.ui.console.print(f"[bold yellow]Tu versión: v{local_version}[/]")
            self.ui.console.print(f"[bold yellow]Versión remota: v{remote_version}[/]")
            self.ui.console.print("[bold cyan]Descargando paquete de actualización (.deb)...[/]")

            # Descargar CHANGELOG
            subprocess.run(["curl", "-s", "-o", self.config.CHANGELOG_FILE, "https://raw.githubusercontent.com/miluxmil/milux/master/CHANGELOG"], check=True)
            
            # Ruta temporal para el paquete .deb
            deb_path = os.path.join(self.config.BASE_DIR, "converter_update.deb")
            
            # Descargar el paquete .deb
            # Nota: Asegúrate de que la URL apunte al archivo .deb correcto en el repo
            subprocess.run(["curl", "-L", "-s", "-o", deb_path, "https://raw.githubusercontent.com/miluxmil/milux/master/converter.deb"], check=True) 

            if not os.path.exists(deb_path) or os.path.getsize(deb_path) == 0:
                self.ui.console.print("[bold red]Error: No se pudo descargar el paquete .deb.[/]")
                time.sleep(2)
                return

            # Instalar el paquete usando dpkg
            self.ui.console.print("[bold yellow]Instalando actualización...[/]")
            # En Termux dpkg no suele requerir sudo, pero usamos check=True para validar éxito
            subprocess.run(["dpkg", "-i", deb_path], check=True)
            
            # Limpiar el paquete descargado
            if os.path.exists(deb_path):
                os.remove(deb_path)
            
            # Actualizar la versión local
            with open(self.config.CAV_FILE, 'w') as f:
                f.write(remote_version)

            # Mostrar changelog
            self._show_changelog(remote_version)
            
            # Reiniciar
            self.ui.logo()
            self.ui.console.print("[bold green]¡Actualización completada con éxito![/]")
            self.ui.console.print(f"[bold yellow]Reiniciando CONVERTER v{remote_version}[/]")
            time.sleep(3)
            
            # Reiniciar el script (el binario /usr/bin/converter ahora apuntará al nuevo código)
            os.execv(sys.executable, [sys.executable] + sys.argv)

        except subprocess.CalledProcessError as e:
            self.ui.console.print(Panel(f"[bold red]Error durante la instalación:[/] {e}\nEs posible que necesites permisos de root o corregir dependencias.", title="ERROR DE UPDATE", border_style="red"))
            time.sleep(4)
        except Exception as e: 
            self.ui.console.print(f"[bold red]Error inesperado durante la actualización: {e}[/]")
            time.sleep(2)

    def _show_changelog(self, version):
        """Muestra el archivo de cambios tras actualizar."""
        self.ui.logo()
        self.ui.console.print(f"[bold cyan]--- Novedades en v{version} ---[/]\n")
        if os.path.exists(self.config.CHANGELOG_FILE):
            with open(self.config.CHANGELOG_FILE, 'r') as f:
                self.ui.console.print(f.read())
        else:
            self.ui.console.print("[dim]No hay información detallada de cambios.[/]")
        input("\nPresiona ENTER para continuar...")

    def exit_app(self):
        self.ui.logo()
        self.ui.console.print(f"[bold green]¡Hasta luego![/]")
        sys.exit(0)

    def show_history(self):
        self.ui.logo()
        if os.path.exists(self.config.HISTORY_FILE):
            table = Table(title="Historial", border_style="green")
            table.add_column("Fecha"); table.add_column("Formato"); table.add_column("Archivos")
            try:
                with open(self.config.HISTORY_FILE, 'r') as f:
                    history = json.load(f)
                if history:
                    for entry in history:
                        table.add_row(
                            str(entry.get('date', '-')),
                            str(entry.get('format', '')).upper(),
                            str(len(entry.get('files', [])))
                        )
                    self.ui.console.print(table)
                else:
                    self.ui.console.print("[bold yellow]El historial está vacío.[/]")
            except Exception:
                self.ui.console.print("[bold red]No se pudo leer el archivo de historial.[/]")
        else:
            self.ui.console.print("[bold yellow]No hay historial registrado aún.[/]")
        input("\nPresiona ENTER...")
