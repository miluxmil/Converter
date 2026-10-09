import os
import subprocess
import time
from rich.table import Table
from rich.panel import Panel
from ..ui import BackException

class InternetModule:
    """Módulo de descargas multimedia desde internet con soporte para rutas personalizadas."""
    def __init__(self, core):
        self.ctx = core

    def download(self):
        while True:
            try:
                self.ctx.ui.logo()
                
                # Obtener ruta de descarga configurada o por defecto
                custom_dest = self.ctx.config.get("download_path")
                default_dest = os.path.join(os.path.expanduser('~'), 'Downloads', 'Converter')
                dest = custom_dest if custom_dest else default_dest
                
                self.ctx.ui.console.print(Panel(
                    f"[bold green]Descargador Universal (yt-dlp)[/]\n"
                    f"[bold white]Destino actual:[/] [cyan]{dest}[/]",
                    title="INTERNET",
                    border_style="cyan"
                ))
                
                self.ctx.ui.console.print("\n[bold cyan]1.[/] Descargar desde URL\n[bold cyan]2.[/] Cambiar ruta de descarga\n[bold red]b.[/] Volver")
                
                menu_opt = self.ctx.ui.prompt("Selecciona una opción").lower()
                
                if menu_opt == 'b': return
                elif menu_opt == '2':
                    self.change_download_path()
                    continue
                elif menu_opt != '1':
                    continue

                # Inicia flujo de descarga (Opción 1)
                self.ctx.ui.logo()
                url = self.ctx.ui.prompt("Introduce URL (o 'b' para volver)")
                if not url: continue
                if url.lower() == 'b': continue

                self.ctx.ui.logo()
                self.ctx.ui.console.print(Panel(f"[bold white]URL:[/] [dim]{url}[/]", title="[bold yellow]CONFIGURACIÓN DE DESCARGA[/]"))
                
                self.ctx.ui.console.print("\n[bold cyan]1.[/] Video (Mejor Calidad)\n[bold cyan]2.[/] Audio (MP3)\n[bold cyan]3.[/] Audio (Original)\n[bold red]b.[/] Cancelar")
                
                opt = self.ctx.ui.prompt("Selecciona formato").lower()
                if opt == 'b': continue
                
                os.makedirs(dest, exist_ok=True)
                
                cmd = ["yt-dlp", "-o", f"{dest}/%(title)s.%(ext)s"]
                
                if opt == '1':
                    cmd += ["-f", "bestvideo+bestaudio/best"]
                elif opt == '2':
                    cmd += ["-x", "--audio-format", "mp3", "--audio-quality", "0"]
                elif opt == '3':
                    cmd += ["-x"]
                else:
                    self.ctx.ui.console.print("[bold red]Opción inválida.[/]")
                    time.sleep(1); continue

                self.ctx.ui.logo()
                self.ctx.ui.console.print(f"[bold yellow]Descargando en:[/] [bold cyan]{dest}[/]")
                
                # Ejecutar con salida visible para que el usuario vea el progreso de yt-dlp
                try:
                    subprocess.run(cmd + [url], check=True)
                    
                    self.ctx.ui.console.print(Panel(f"[bold green]¡Descarga completada exitosamente![/]\n[bold white]Ruta:[/] {dest}", border_style="green"))
                    
                    # Preguntar si desea convertir
                    if self.ctx.ui.prompt("¿Deseas convertir el archivo descargado ahora? (s/n)", default="n").lower() == 's':
                        # Buscamos el archivo más reciente en la carpeta de descargas
                        files = sorted(
                            [f for f in os.listdir(dest) if os.path.isfile(os.path.join(dest, f))],
                            key=lambda x: os.path.getmtime(os.path.join(dest, x)),
                            reverse=True
                        )
                        
                        if files:
                            downloaded_file = files[0]
                            self.ctx.ui.console.print(f"[bold yellow]Redirigiendo a conversión:[/] {downloaded_file}")
                            time.sleep(1)
                            
                            # Configurar metadatos del módulo de conversión para evitar AttributeError
                            ext = downloaded_file.split('.')[-1].lower()
                            if ext in ['mp4', 'mkv', 'avi', 'mov', 'webm', 'flv']:
                                self.ctx.conversion.MODE = "- Video -"
                                self.ctx.conversion.FR1, self.ctx.conversion.FR2, self.ctx.conversion.FR3 = ("mp4", "mkv", "avi")
                            else:
                                self.ctx.conversion.MODE = "- Audio -"
                                self.ctx.conversion.FR1, self.ctx.conversion.FR2, self.ctx.conversion.FR3 = ("mp3", "wav", "ogg")
                            
                            # Preparamos el módulo de conversión
                            self.ctx.conversion.RUTA = dest
                            self.ctx.conversion.FILES = [downloaded_file]
                            self.ctx.conversion.PROFILE_SELECTED = False
                            
                            self.ctx.conversion.check_files()
                            return # Salimos del bucle de internet tras la conversión
                    
                except subprocess.CalledProcessError:
                    self.ctx.ui.console.print(Panel("[bold red]Error durante la descarga.[/]\nVerifica la URL o tu conexión a internet.", border_style="red"))
            except BackException: return

    def change_download_path(self):
        """Permite al usuario definir una ruta personalizada."""
        self.ctx.ui.logo()
        self.ctx.ui.console.print("[bold yellow]Configuración de Ruta de Descarga[/]")
        self.ctx.ui.console.print("Usa el explorador para seleccionar la carpeta destino.")
        time.sleep(1)
        
        new_path = self.ctx.ui.file_explorer()
        if new_path and os.path.isdir(new_path):
            self.ctx.config.set("download_path", new_path)
            self.ctx.ui.console.print(f"[bold green]✓ Ruta actualizada:[/] {new_path}")
        else:
            self.ctx.ui.console.print("[bold red]Operación cancelada o ruta inválida.[/]")
        time.sleep(2)
