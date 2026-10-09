#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import time
import threading
import subprocess

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn
from rich.align import Align

class MainMenuException(Exception): pass
class BackException(Exception): pass

class UI:
    """Clase para la interfaz visual enriquecida con Rich corregida."""
    def __init__(self, core):
        self.ctx = core
        self.console = Console()
        # Mantenemos COLORS para compatibilidad, pero Rich prefiere [color]Texto[/]
        self.COLORS = {
            'C': 'cyan', 'G': 'green', 'R': 'red', 'Y': 'yellow', 
            'B': 'blue', 'P': 'purple', 'RE': 'white' # 'RE' ahora mapea a blanco
        }

    def prompt(self, text=">>", default="", global_shortcuts=True):
        try:
            ans = Prompt.ask(f"[bold cyan]{text}[/]", default=default).strip()
            if global_shortcuts:
                if ans.lower() == 'mi': raise MainMenuException()
                if ans.lower() == 'b': raise BackException()
            return ans
        except KeyboardInterrupt:
            self.console.print("\n[bold red]Interrupción detectada. Saliendo...[/]")
            sys.exit(0)

    def splash_screen(self):
        """Muestra una pantalla de carga de 1 segundo con animación fluida."""
        self.logo()
        self.console.print("\n" * 2)
        
        # Texto centrado arriba
        self.console.print(Align.center("[bold cyan]CONVERTER | Iniciando..[/]"))
        
        progress = Progress(
            SpinnerColumn(),
            BarColumn(bar_width=40),
            TaskProgressColumn(),
            console=self.console,
            transient=False 
        )

        with progress:
            task = progress.add_task("Iniciando", total=100)
            while not progress.finished:
                # 20 pasos de 0.05s = 1 segundo total
                progress.update(task, advance=5)
                time.sleep(0.05)
            
            # Breve pausa de confirmación al llegar al final
            time.sleep(0.1)

    def logo(self):
        os.system('clear')
        year = time.strftime("%Y")
        art = rf"""
[bold purple]      \_/
     (* *)
    __)#(__
   ( )...( )(_)  [bold green]C O N V E R T E R[/]
   || |_| ||//     [bold green]      By[/]
>==() | | ()/      [bold green]</[M]iLu{{×}}_> | DNP | {year}[/]
    _(___)_
   [-]   [-]  [italic white]      Music - Video - Images[/]
        """
        # Imprimimos el arte directamente sin Panel
        self.console.print(art)

    def file_explorer(self, start_path=None):
        current = start_path or self.ctx.config.get("last_path") or os.path.expanduser("~")
        if os.path.isfile(current):
            current = os.path.dirname(current)
        if not os.path.isdir(current):
            current = os.path.expanduser("~")
        while True:
            self.logo()
            table = Table(title=f"Explorando: {current}", title_style="bold cyan", border_style="blue")
            table.add_column("N°", justify="right", style="dim")
            table.add_column("Tipo", justify="center")
            table.add_column("Nombre", style="green")
            
            try:
                items = sorted(os.listdir(current))
                dirs = [d for d in items if os.path.isdir(os.path.join(current, d))]
                files = [f for f in items if os.path.isfile(os.path.join(current, f))]
                all_items = dirs + files
                
                for i, item in enumerate(all_items, 1):
                    is_dir = os.path.isdir(os.path.join(current, item))
                    table.add_row(str(i), "[yellow]DIR[/]" if is_dir else "[blue]FILE[/]", item)
                
                self.console.print(table)
                self.console.print("\n[bold cyan]Seleccionar (s)[/] | [bold yellow]Atrás (..)[/] | [bold magenta]Abrir (o N)[/]")
                self.console.print("[bold red]Volver (b)[/] | [bold magenta]Menú Principal (mi)[/]")
                
                ans = self.prompt()
                if ans == 's': 
                    self.ctx.config.set("last_path", current)
                    return current
                if ans == '..': 
                    current = os.path.dirname(current)
                    continue
                if ans.startswith('o '):
                    try:
                        idx = int(ans.split()[1])-1
                        if 0 <= idx < len(all_items):
                            self.open_file(os.path.join(current, all_items[idx]))
                    except: pass
                    continue
                if ans.isdigit():
                    try:
                        idx = int(ans)-1
                        if 0 <= idx < len(all_items):
                            target = os.path.join(current, all_items[idx])
                            if os.path.isdir(target): current = target
                            else: 
                                self.ctx.config.set("last_path", current)
                                return target
                    except: pass
            except (PermissionError, FileNotFoundError):
                self.console.print(f"[bold red]Error al acceder a {current}. Volviendo a inicio...[/]")
                time.sleep(2)
                current = os.path.expanduser("~")

    def draw_progress(self, percent, bar_length=30, prefix="Progreso"):
        # Rich maneja su propio progreso, pero dejamos esto por compatibilidad si se usa fuera de un context manager
        pass

    def start_custom_spinner(self, mensaje="Procesando..."):
        self.spinner_running = True
        def spin():
            with self.console.status(f"[bold yellow]{mensaje}[/]") as status:
                while self.spinner_running:
                    time.sleep(0.1)
        self.spin_thread = threading.Thread(target=spin)
        self.spin_thread.start()

    def stop_custom_spinner(self):
        self.spinner_running = False
        if hasattr(self, 'spin_thread'): self.spin_thread.join()

    def show_conversion_success_message(self):
        self.console.print(Panel("[bold green]¡OPERACIÓN COMPLETADA CON ÉXITO![/]", border_style="green"))
        input("\nPresiona ENTER para continuar...")

    def open_file(self, file_path):
        if os.path.exists(file_path):
            self.console.print(f"[dim]Abriendo: {os.path.basename(file_path)}...[/]")
            subprocess.run(["termux-open", file_path])
