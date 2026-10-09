import os
import shutil
import glob
import hashlib
import zipfile
import time
import tempfile
import subprocess
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from ..ui import BackException

class StorageModule:
    """Módulo de gestión de almacenamiento avanzado con UI Rich."""
    def __init__(self, core):
        self.ctx = core

    def menu(self):
        while True:
            try:
                self.ctx.ui.logo()
                
                # Mostrar uso de disco real
                try:
                    total, used, free = shutil.disk_usage(os.path.expanduser('~'))
                    used_gb = used / (1024**3)
                    total_gb = total / (1024**3)
                    free_gb = free / (1024**3)
                    used_percent = (used / total) * 100
                    
                    # Barra de progreso visual
                    bar_len = 20
                    filled = int(bar_len * used / total)
                    bar = "█" * filled + "░" * (bar_len - filled)
                    
                    self.ctx.ui.console.print(Panel(
                        f"[bold white]Uso:[/] [bold yellow]{used_gb:.1f}G[/] / [bold cyan]{total_gb:.1f}G[/] ({used_percent:.0f}%)\n"
                        f"[bold green]{bar}[/] [bold white]{free_gb:.1f}G Libres[/]",
                        title="[bold yellow]ESTADO DISCO[/]", border_style="blue"
                    ))
                except: pass

                table = Table(show_header=False, border_style="dim", box=None)
                table.add_row("[bold cyan]1.[/] Analizar Espacio", "[bold cyan]2.[/] Archivos Grandes")
                table.add_row("[bold cyan]3.[/] Limpiar Temporales", "[bold cyan]4.[/] Organizar Carpeta")
                table.add_row("[bold cyan]5.[/] Buscar Duplicados", "[bold cyan]6.[/] Comprimir ZIP")
                table.add_row("[bold cyan]7.[/] Limpiar Cachés", "[bold cyan]8.[/] Carpetas Vacías")
                table.add_row("[bold cyan]9.[/] CorpseFinder (Basura)", "[bold red]b.[/] Volver")
                
                self.ctx.ui.console.print(Panel(table, title="[bold yellow]GESTOR ALMACENAMIENTO[/]", border_style="green"))

                ans = self.ctx.ui.prompt().lower()
                if ans == '1': self.analyze_space()
                elif ans == '2': self.find_large()
                elif ans == '3': self.clean_temp()
                elif ans == '4': self.organize()
                elif ans == '5': self.find_duplicates()
                elif ans == '6': self.compress()
                elif ans == '7': self.clear_cache()
                elif ans == '8': self.remove_empty()
                elif ans == '9': self.clean_junk()
                elif ans == 'b': return
            except BackException: return

    def analyze_space(self):
        path = self.ctx.ui.file_explorer()
        if not path: return
        if os.path.isfile(path): path = os.path.dirname(path)
        
        self.ctx.ui.logo()
        self.ctx.ui.console.print(f"[bold yellow]Analizando:[/] {path}...")
        
        folders = {}
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=self.ctx.ui.console) as pr:
            task = pr.add_task("Calculando tamaños...", total=None)
            try:
                for entry in os.scandir(path):
                    if entry.is_dir(follow_symlinks=False):
                        size = 0
                        try:
                            for dp, dn, filenames in os.walk(entry.path):
                                for f in filenames:
                                    fp = os.path.join(dp, f)
                                    if not os.path.islink(fp): size += os.path.getsize(fp)
                            folders[entry.name] = size
                        except: continue
            except Exception as e:
                self.ctx.ui.console.print(f"[bold red]Error:[/] {e}")

        table = Table(title=f"Espacio en {os.path.basename(path)}", border_style="cyan")
        table.add_column("Carpeta", style="bold green")
        table.add_column("Tamaño", justify="right", style="bold yellow")
        
        for name, size in sorted(folders.items(), key=lambda x: x[1], reverse=True):
            table.add_row(name, f"{size/(1024*1024):.2f} MB")
            
        self.ctx.ui.console.print(table)
        input("\nPresiona ENTER para continuar...")

    def find_large(self):
        path = self.ctx.ui.file_explorer()
        if not path: return
        if os.path.isfile(path): path = os.path.dirname(path)
        
        limit_mb = self.ctx.ui.prompt("Mínimo (MB) [50]", default="50")
        try: limit = int(limit_mb) * 1024 * 1024
        except: limit = 50 * 1024 * 1024
        
        large = []
        self.ctx.ui.console.print(f"[bold yellow]Buscando archivos > {limit_mb}MB...[/]")
        
        for dp, _, filenames in os.walk(path):
            for f in filenames:
                fp = os.path.join(dp, f)
                try:
                    if not os.path.islink(fp) and os.path.getsize(fp) > limit:
                        large.append((fp, os.path.getsize(fp)))
                except: continue
        
        if not large:
            self.ctx.ui.console.print("[bold green]No se encontraron archivos grandes.[/]")
            time.sleep(2); return

        table = Table(title="Archivos Grandes", border_style="red")
        table.add_column("N°", style="dim"); table.add_column("Ruta"); table.add_column("Tamaño", style="bold yellow")
        
        large.sort(key=lambda x: x[1], reverse=True)
        for i, (fp, size) in enumerate(large[:20], 1):
            table.add_row(str(i), fp, f"{size/(1024*1024):.2f} MB")
            
        self.ctx.ui.console.print(table)
        
        opt = self.ctx.ui.prompt("¿Borrar alguno? (N° separado por espacio o 'n')").lower()
        if opt != 'n' and opt:
            indices = self.ctx.utils.parse_selection(opt, len(large))
            for idx in indices:
                try: 
                    os.remove(large[idx][0])
                    self.ctx.ui.console.print(f"[bold red]Eliminado:[/] {os.path.basename(large[idx][0])}")
                except: pass
            time.sleep(2)

    def clean_temp(self):
        self.ctx.ui.logo()
        if self.ctx.ui.prompt("¿Limpiar carpetas temporales? (s/n)", default="n").lower() == 's':
            freed = 0
            temp_dir = os.environ.get("TMPDIR") or tempfile.gettempdir() or "/data/data/com.termux/files/usr/tmp"
            for d in [os.path.expanduser("~/.cache"), temp_dir]:
                if os.path.isdir(d):
                    try:
                        for item in os.listdir(d):
                            item_path = os.path.join(d, item)
                            try:
                                if os.path.isfile(item_path) or os.path.islink(item_path):
                                    freed += os.path.getsize(item_path)
                                    os.remove(item_path)
                                elif os.path.isdir(item_path):
                                    for dp, dn, fn in os.walk(item_path):
                                        for f in fn: freed += os.path.getsize(os.path.join(dp, f))
                                    shutil.rmtree(item_path)
                            except: pass
                    except: pass
            self.ctx.ui.console.print(Panel(f"[bold green]Limpieza completada.[/]\n[bold white]Espacio liberado: {freed/(1024*1024):.2f} MB[/]", border_style="green"))
            self.ctx.utils.notify(f"Limpieza de temporales: {freed/(1024*1024):.2f} MB liberados", "INFO")
        input("\nENTER...")

    def organize(self):
        path = self.ctx.ui.file_explorer()
        if not path: return
        if os.path.isfile(path): path = os.path.dirname(path)
        
        if self.ctx.ui.prompt(f"¿Organizar archivos en {os.path.basename(path)}? (s/n)").lower() == 's':
            types = {
                "Imagenes": ["jpg", "jpeg", "png", "gif", "webp", "bmp"],
                "Videos": ["mp4", "mkv", "avi", "mov", "wmv", "webm"],
                "Audio": ["mp3", "wav", "ogg", "m4a", "flac"],
                "Documentos": ["pdf", "doc", "docx", "txt", "pdf", "epub"],
                "Comprimidos": ["zip", "rar", "7z", "tar", "gz"]
            }
            
            moved = 0
            for f in os.listdir(path):
                f_path = os.path.join(path, f)
                if os.path.isfile(f_path):
                    ext = f.split('.')[-1].lower()
                    for folder, exts in types.items():
                        if ext in exts:
                            dest = os.path.join(path, folder)
                            os.makedirs(dest, exist_ok=True)
                            try:
                                shutil.move(f_path, os.path.join(dest, f))
                                moved += 1
                                break
                            except: pass
            self.ctx.ui.console.print(f"[bold green]Hecho![/] Se organizaron {moved} archivos.")
        time.sleep(2)

    def find_duplicates(self):
        path = self.ctx.ui.file_explorer()
        if not path: return
        if os.path.isfile(path): path = os.path.dirname(path)
        
        self.ctx.ui.console.print("[bold yellow]Escaneando duplicados por contenido (MD5)...[/]")
        hashes = {}
        duplicates = []
        
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=self.ctx.ui.console) as pr:
            task = pr.add_task("Calculando hashes...", total=None)
            for dp, _, filenames in os.walk(path):
                for f in filenames:
                    fp = os.path.join(dp, f)
                    try:
                        # Solo archivos < 100MB para evitar lentitud extrema
                        if os.path.getsize(fp) < 100 * 1024 * 1024:
                            with open(fp, 'rb') as file:
                                h = hashlib.md5(file.read()).hexdigest()
                            if h in hashes:
                                duplicates.append((fp, hashes[h]))
                            else: hashes[h] = fp
                    except: continue
        
        if not duplicates:
            self.ctx.ui.console.print("[bold green]No se encontraron duplicados.[/]")
        else:
            table = Table(title="Archivos Duplicados", border_style="yellow")
            table.add_column("Archivo duplicado"); table.add_column("Original")
            for dup, orig in duplicates[:15]:
                table.add_row(os.path.basename(dup), os.path.basename(orig))
            self.ctx.ui.console.print(table)
        input("\nPresiona ENTER...")

    def compress(self):
        path = self.ctx.ui.file_explorer()
        if not path: return
        if os.path.isfile(path): path = os.path.dirname(path)
        
        files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
        if not files: return
        
        self.ctx.ui.logo()
        for i, f in enumerate(files, 1):
            self.ctx.ui.console.print(f" [bold cyan][{i}][/] {f}")
            
        idx_str = self.ctx.ui.prompt("Números (ej: 1 3 5-8)")
        if not idx_str: return
        
        idx = self.ctx.utils.parse_selection(idx_str, len(files))
        if not idx:
            self.ctx.ui.console.print("[bold red]No se seleccionaron archivos válidos.[/]")
            time.sleep(1.5)
            return

        name = self.ctx.ui.prompt("Nombre del ZIP (sin .zip)", default="comprimido") + ".zip"
        
        with zipfile.ZipFile(os.path.join(path, name), 'w') as z:
            for i in idx:
                f_to_add = files[i]
                z.write(os.path.join(path, f_to_add), arcname=f_to_add)
        
        self.ctx.ui.console.print(f"[bold green]ZIP creado:[/] {name}")
        time.sleep(2)

    def clear_cache(self):
        self.ctx.ui.logo()
        self.ctx.ui.console.print("[bold yellow]Limpiando cachés de Python y Node...[/]")
        self.ctx.utils.execute(["pip", "cache", "purge"])
        self.ctx.utils.execute(["npm", "cache", "clean", "--force"])
        self.ctx.ui.console.print("[bold green]Cachés vaciadas.[/]")
        time.sleep(2)

    def remove_empty(self):
        path = self.ctx.ui.file_explorer()
        if not path: return
        if os.path.isfile(path): path = os.path.dirname(path)
        
        count = 0
        for dp, dn, fn in os.walk(path, topdown=False):
            if not dn and not fn:
                try:
                    os.rmdir(dp)
                    count += 1
                except: pass
        self.ctx.ui.console.print(f"[bold green]Se eliminaron {count} carpetas vacías.[/]")
        time.sleep(2)

    def clean_junk(self):
        self.ctx.ui.logo()
        self.ctx.ui.console.print(Panel("[bold yellow]Análisis de Basura (CorpseFinder)[/]\nBuscando restos de paquetes y archivos temporales...", border_style="red"))
        
        junk = []
        patterns = ['*.tmp', '*.bak', '*.swp', '*.log', '*~']
        search_path = os.path.expanduser("~")
        
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=self.ctx.ui.console) as pr:
            pr.add_task("Escaneando sistema...", total=None)
            for pat in patterns:
                # Usamos glob para búsqueda recursiva (limitada por seguridad)
                for f in glob.glob(os.path.join(search_path, '**', pat), recursive=True):
                    if os.path.isfile(f) and "/.git/" not in f:
                        junk.append(f)

        # Simular pkg autoremove si estamos en Termux
        orphans = []
        if shutil.which("pkg"):
            try:
                res = subprocess.run(["pkg", "autoremove", "--simulate"], capture_output=True, text=True)
                if "REM_PACKS" in res.stdout or "following packages will be REMOVED" in res.stdout:
                    # Intento simple de extraer nombres
                    parts = res.stdout.split("REMOVED:")
                    if len(parts) > 1: orphans = parts[1].split("\n")[1].strip().split()
            except: pass

        if not junk and not orphans:
            self.ctx.ui.console.print("[bold green]¡Sistema limpio![/] No se encontró basura.")
        else:
            if junk: self.ctx.ui.console.print(f"[bold yellow]Archivos basura found:[/] {len(junk)}")
            if orphans: self.ctx.ui.console.print(f"[bold red]Paquetes huérfanos found:[/] {len(orphans)}")
            
            if self.ctx.ui.prompt("¿Deseas realizar una limpieza profunda? (s/n)").lower() == 's':
                for f in junk: 
                    try: os.remove(f)
                    except: pass
                if orphans and shutil.which("pkg"):
                    subprocess.run(["pkg", "autoremove", "-y"])
                self.ctx.ui.console.print("[bold green]Limpieza terminada.[/]")
            else:
                self.ctx.ui.console.print("[bold cyan]Limpieza cancelada.[/]")
        input("\nPresiona ENTER...")
