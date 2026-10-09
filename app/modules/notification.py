import os
import time
from rich.table import Table
from rich.panel import Panel
from ..ui import BackException

class NotificationModule:
    """Centro de notificaciones y log de eventos del usuario."""
    def __init__(self, core):
        self.ctx = core

    def menu(self):
        while True:
            try:
                self.ctx.ui.logo()
                
                log_path = self.ctx.config.NOTIF_LOG
                table = Table(title="Últimas Notificaciones", border_style="cyan", expand=True)
                table.add_column("Fecha", style="dim", width=20)
                table.add_column("Categoría", justify="center")
                table.add_column("Mensaje", style="bold white")

                if os.path.exists(log_path):
                    with open(log_path, 'r') as f:
                        lines = f.readlines()
                        for line in lines[-10:]:
                            line = line.strip()
                            if not line: continue
                            
                            try:
                                # Formato esperado: [2024-03-29 12:00:00] [INFO] Mensaje
                                # Buscamos los corchetes
                                if line.startswith("["):
                                    # Dividimos por el cierre de corchete ']'
                                    parts = line.split("] ")
                                    if len(parts) >= 3:
                                        date = parts[0].strip("[]")
                                        cat = parts[1].strip("[]")
                                        msg = "] ".join(parts[2:]) # Por si el mensaje tiene "] "
                                        
                                        color = "green"
                                        if "ERROR" in cat: color = "red"
                                        elif "WARN" in cat: color = "yellow"
                                        elif "SUCCESS" in cat: color = "bold green"
                                        
                                        table.add_row(date, f"[{color}]{cat}[/]", msg)
                                    else:
                                        table.add_row("-", "LOG", line)
                                else:
                                    table.add_row("-", "LOG", line)
                            except Exception:
                                table.add_row("-", "LOG", line)
                else:
                    table.add_row("-", "INFO", "No hay notificaciones pendientes.")

                self.ctx.ui.console.print(table)
                
                self.ctx.ui.console.print("\n[bold cyan]1.[/] Ver historial completo\n[bold cyan]2.[/] Limpiar todo\n[bold red]b.[/] Volver")
                
                ans = self.ctx.ui.prompt().lower()
                if ans == '1': self.view_all()
                elif ans == '2': self.clear()
                elif ans == 'b': return
            except BackException: return

    def view_all(self):
        self.ctx.ui.logo()
        log_path = self.ctx.config.NOTIF_LOG
        if os.path.exists(log_path):
            with open(log_path, 'r') as f:
                self.ctx.ui.console.print(Panel(f.read(), title="Historial Completo", border_style="blue"))
        else:
            self.ctx.ui.console.print("[bold yellow]No hay historial disponible.[/]")
        input("\nPresiona ENTER para continuar...")

    def clear(self):
        log_path = self.ctx.config.NOTIF_LOG
        if os.path.exists(log_path):
            if self.ctx.ui.prompt("¿Estás seguro de eliminar todas las notificaciones? (s/n)").lower() == 's':
                try:
                    os.remove(log_path)
                    self.ctx.ui.console.print("[bold green]Centro de notificaciones vaciado.[/]")
                except:
                    self.ctx.ui.console.print("[bold red]Error al eliminar el archivo de log.[/]")
                time.sleep(1)
