import os
import subprocess
import time
import re
import json
import shutil
import shlex
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from ..ui import BackException

class AdvancedModule:
    """Módulo avanzado con herramientas de diagnóstico y benchmark."""
    def __init__(self, core):
        self.ctx = core

    def menu(self):
        while True:
            try:
                self.ctx.ui.logo()
                
                table = Table(show_header=False, border_style="dim", box=None)
                table.add_row("[bold cyan]1.[/] Editor FFmpeg Pro", "[bold cyan]2.[/] Editor Magick Pro")
                table.add_row("[bold cyan]3.[/] Monitor de Recursos", "[bold cyan]4.[/] Consola Profesional")
                table.add_row("[bold cyan]5.[/] Integridad Multimedia", "[bold cyan]6.[/] Benchmark Rendimiento")
                table.add_row("[bold cyan]7.[/] Espectrograma Audio", "[bold cyan]8.[/] Informe Técnico")
                table.add_row("[bold red]b.[/] Volver", "")
                
                self.ctx.ui.console.print(Panel(table, title="[bold yellow]MODO AVANZADO[/]", border_style="purple"))

                ans = self.ctx.ui.prompt().lower()
                if ans == '1': self.ffmpeg_pro()
                elif ans == '2': self.magick_pro()
                elif ans == '3': self.monitor()
                elif ans == '4': self.console()
                elif ans == '5': self.verify_integrity()
                elif ans == '6': self.benchmark()
                elif ans == '7': self.spectrogram()
                elif ans == '8': self.technical_report()
                elif ans == 'b': return
            except BackException: return

    def ffmpeg_pro(self):
        self.ctx.ui.logo()
        self.ctx.ui.console.print("[bold yellow]Editor FFmpeg Personalizado[/]")
        self.ctx.ui.console.print("Ejemplo: [dim]ffmpeg -i input.mp4 -vf scale=720:-1 output.mp4[/]")
        
        cmd = self.ctx.ui.prompt("FFmpeg CMD")
        if cmd.startswith("ffmpeg"):
            try:
                self.ctx.ui.console.print(f"[bold green]Ejecutando...[/]")
                subprocess.run(shlex.split(cmd), check=False)
            except Exception as e:
                self.ctx.ui.console.print(f"[bold red]Error:[/] {e}")
        input("\nPresiona ENTER...")

    def magick_pro(self):
        self.ctx.ui.logo()
        self.ctx.ui.console.print("[bold yellow]Editor ImageMagick Personalizado[/]")
        self.ctx.ui.console.print("Ejemplo: [dim]convert in.png -resize 50% out.png[/]")
        
        cmd = self.ctx.ui.prompt("Magick CMD")
        if cmd.startswith("convert") or cmd.startswith("mogrify"):
            try:
                subprocess.run(shlex.split(cmd), check=False)
            except Exception as e:
                self.ctx.ui.console.print(f"[bold red]Error:[/] {e}")
        input("\nPresiona ENTER...")

    def monitor(self):
        self.ctx.ui.logo()
        self.ctx.ui.console.print("[bold yellow]Monitor de Sistema (top)[/]\n[dim]Presiona 'q' para salir del monitor[/]")
        time.sleep(1)
        subprocess.run(["top", "-n", "1"])
        input("\nPresiona ENTER...")

    def console(self):
        self.ctx.ui.logo()
        # Panel de advertencia serio y visual
        self.ctx.ui.console.print(Panel(
            "[bold red]¡ADVERTENCIA DE SEGURIDAD![/]\n\n"
            "Estás a punto de entrar a una shell del sistema desde Converter.\n"
            "Cualquier comando que ejecutes aquí afectará directamente a tu sistema.\n"
            "El uso irresponsable puede ocasionar [bold underline]cambios irreversibles[/].\n\n"
            "Escribe [bold yellow]'exit'[/] para volver a Converter de forma segura.",
            title="MODO PROFESIONAL",
            border_style="red",
            padding=(1, 2)
        ))
        
        # Pausa obligatoria para que el usuario lea
        input("\nPresiona ENTER para aceptar los riesgos y continuar...")
        
        # Configuración del entorno
        shell = os.environ.get("SHELL", "bash")
        env = os.environ.copy()
        
        try:
            if "fish" in shell:
                # Limpieza agresiva de cualquier rastro de temas anteriores
                prompt_cmds = (
                    "for f in (functions -n | grep prompt); functions -e $f; end; "
                    "function fish_prompt; set_color -o green; echo -n 'Console Converter >> '; set_color normal; end; "
                    "function fish_right_prompt; end; "
                    "function fish_mode_prompt; end; "
                    "set -g fish_greeting ''"
                )
                subprocess.run([shell, "-C", prompt_cmds], env=env)
            else:
                # Para bash, zsh y otros compatibles con PS1
                env["PS1"] = "\033[1;32mConsole Converter >> \033[0m"
                subprocess.run([shell], env=env)
            
            # Al salir de la shell, mostramos este mensaje y esperamos ENTER
            print("\n" + "-"*40)
            self.ctx.ui.console.print("[bold green]Has salido de la Consola Profesional.[/]")
            input("Presiona ENTER para regresar al menú...")
            
        except Exception as e:
            self.ctx.ui.console.print(f"[bold red]Error al iniciar la consola:[/] {e}")
            input("\nPresiona ENTER para continuar...")

    def verify_integrity(self):
        path = self.ctx.ui.file_explorer()
        if not path or os.path.isdir(path): return
        
        self.ctx.ui.logo()
        self.ctx.ui.console.print(f"[bold yellow]Verificando integridad:[/] {os.path.basename(path)}")
        
        cmd = ["ffmpeg", "-v", "error", "-i", path, "-f", "null", "-"]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True)
            if res.stderr:
                self.ctx.ui.console.print(Panel(res.stderr, title="Errores Detectados", border_style="red"))
            else:
                self.ctx.ui.console.print("[bold green]✓ El archivo parece estar íntegro.[/]")
        except Exception as e:
            self.ctx.ui.console.print(f"[bold red]Error:[/] {e}")
        input("\nENTER...")

    def benchmark(self):
        path = self.ctx.ui.file_explorer()
        if not path or os.path.isdir(path): return
        
        self.ctx.ui.logo()
        self.ctx.ui.console.print(f"[bold yellow]Iniciando benchmark de decodificación...[/]")
        
        cmd = ["ffmpeg", "-benchmark", "-i", path, "-f", "null", "-"]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True)
            output = res.stderr
            
            speed = re.search(r"speed=\s*([0-9.]+)", output)
            utime = re.search(r"bench:\s*utime=([0-9.]+)s", output)
            
            table = Table(title="Resultados Benchmark", border_style="green")
            table.add_column("Métrica"); table.add_column("Valor")
            table.add_row("Velocidad", f"{speed.group(1)}x" if speed else "N/A")
            table.add_row("Tiempo CPU (user)", f"{utime.group(1)}s" if utime else "N/A")
            
            self.ctx.ui.console.print(table)
        except Exception as e:
            self.ctx.ui.console.print(f"[bold red]Error:[/] {e}")
        input("\nENTER...")

    def spectrogram(self):
        path = self.ctx.ui.file_explorer()
        if not path or os.path.isdir(path): return
        
        out = os.path.splitext(path)[0] + "_spec.png"
        self.ctx.ui.logo()
        self.ctx.ui.console.print(f"[bold yellow]Generando espectrograma...[/]")
        
        cmd = ["ffmpeg", "-i", path, "-lavfi", "showspectrumpic=s=1024x512:color=rainbow", "-y", out]
        if self.ctx.utils.execute(cmd, capture=False)[0]:
            self.ctx.ui.console.print(f"[bold green]Generado:[/] {out}")
            if shutil.which("termux-open"):
                if self.ctx.ui.prompt("¿Abrir imagen? (s/n)").lower() == 's':
                    subprocess.run(["termux-open", out])
        input("\nENTER...")

    def technical_report(self):
        path = self.ctx.ui.file_explorer()
        if not path or os.path.isdir(path): return
        
        self.ctx.ui.logo()
        cmd = ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", path]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True)
            data = json.loads(res.stdout)
            
            # Formatear JSON con color
            syntax = Syntax(json.dumps(data, indent=2), "json", theme="monokai", line_numbers=True)
            self.ctx.ui.console.print(Panel(syntax, title=f"Informe Técnico: {os.path.basename(path)}", border_style="cyan"))
        except Exception as e:
            self.ctx.ui.console.print(f"[bold red]Error:[/] {e}")
        input("\nENTER...")
