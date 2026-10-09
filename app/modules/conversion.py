#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import shutil
import time
import json
import subprocess
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TaskProgressColumn, TimeRemainingColumn
from ..ui import BackException, MainMenuException

class ConversionModule:
    """Módulo de conversión con soporte para segundo plano y UI Rich."""
    def __init__(self, core):
        self.ctx = core
        self.RUTA = ""
        self.FILES = []
        self.EXIT = ""
        self.MODE = ""
        self.PROFILE_SELECTED = False

    def start(self, mode, formats):
        self.MODE = mode
        self.FR1, self.FR2, self.FR3 = formats
        self.PROFILE_SELECTED = False
        while True:
            try:
                self.ctx.ui.logo()
                self.ctx.ui.console.print(f"[bold green]Origen de archivos ({self.MODE})[/]")
                self.ctx.ui.console.print(f"[bold cyan]EXPLORADOR (e) | MANUAL (m) | YOUTUBE (mi) | VOLVER (b)[/]")
                
                ans = self.ctx.ui.prompt(global_shortcuts=False).lower()
                if ans == 'e': ruta = self.ctx.ui.file_explorer()
                elif ans == 'm': ruta = self.ctx.ui.prompt("Ruta >> ")
                elif ans == 'mi': ruta = os.path.join(os.path.expanduser('/sdcard/'), 'youtube')
                elif ans == 'b': return
                else: continue
                
                if ruta and os.path.exists(ruta):
                    self.RUTA = ruta
                    self.continue_conversion()
                    return
                else:
                    self.ctx.ui.console.print(f"[bold red][!][/] La ruta no existe o es inválida: {ruta}")
                    time.sleep(2)
            except BackException: return

    def show_toolbar(self):
        table = Table(show_header=False, border_style="dim", box=None)
        table.add_row("[bold green]REFRESH (r)[/]", "[bold green]DELETE (d)[/]", "[bold green]NEW PATH (p)[/]", "[bold green]NEW CONV (n)[/]")
        table.add_row("[bold green]SEARCH (s)[/]", "[bold green]COPY (c)[/]", "[bold green]MOVE (m)[/]", "[bold green]BACK (b)[/]")
        self.ctx.ui.console.print(Panel(table, title="[bold yellow]COMANDOS[/]", border_style="blue", expand=False))

    def continue_conversion(self):
        while True:
            try:
                self.ctx.ui.logo()
                self.ctx.ui.console.print(f"[bold cyan]Ubicación:[/][bold white] {self.RUTA}[/]")
                files = [f for f in os.listdir(self.RUTA) if os.path.isfile(os.path.join(self.RUTA, f))]
                
                file_table = Table(title="Archivos Disponibles", border_style="green", box=None)
                file_table.add_column("N°", style="bold red")
                file_table.add_column("Nombre", style="bold green")
                for i, f in enumerate(files, 1): file_table.add_row(str(i), f)
                self.ctx.ui.console.print(file_table)
                
                self.show_toolbar()
                
                sel = self.ctx.ui.prompt("Selección").lower()
                if sel == 'r': continue
                elif sel == 'p': return
                elif sel == 'n': raise MainMenuException()
                elif sel in ['d', 'c', 'm']: self.copy_move_del(sel); continue
                elif sel == 's': self.search_files(); continue
                elif sel == 'b': return
                
                indices = self.ctx.utils.parse_selection(sel, len(files))
                self.FILES = [files[i] for i in indices]
                if self.FILES: self.check_files()
            except BackException: return

    def check_files(self):
        while True:
            try:
                if not self.PROFILE_SELECTED:
                    self.ctx.ui.logo()
                    self.ctx.ui.console.print(f"[bold yellow]Sugerencias:[/][bold cyan] {self.FR1}, {self.FR2}, {self.FR3}[/]")
                    exit_fmt = self.ctx.ui.prompt("Formato de salida", default=self.FR1).strip().lower().lstrip('.')
                    self.EXIT = exit_fmt if exit_fmt else self.FR1
                
                self.ctx.ui.logo()
                self.ctx.ui.console.print(Panel("\n".join(self.FILES), title=f"Confirmar a {self.EXIT}", border_style="green"))
                
                print("\n[s] Iniciar ahora | [e] Editar | [b] Volver")
                ans = self.ctx.ui.prompt().lower()
                
                if ans == 'e':
                    new_files = []
                    for f in self.FILES:
                        edited = self.editor(os.path.join(self.RUTA, f))
                        new_files.append(os.path.basename(edited))
                    self.FILES = new_files
                    continue
                
                if ans == 's':
                    self.process_batch()
                    self.post_process()
                    return
                elif ans == 'b': return
            except BackException: return

    def process_batch(self):
        self.ctx.ui.logo()
        progress = Progress(
            SpinnerColumn(), 
            TextColumn("[bold blue]{task.fields[filename]}"), 
            BarColumn(bar_width=20), 
            TaskProgressColumn(), 
            TimeRemainingColumn(),
            console=self.ctx.ui.console
        )
        progress.start()

        for f in self.FILES:
            inp = os.path.join(self.RUTA, f)
            out_ext = self.EXIT
            base_name = os.path.splitext(f)[0]
            out = os.path.join(self.RUTA, f"{base_name}.{out_ext}")
            
            # Evitar sobrescribir el archivo de entrada con el mismo nombre y extensión
            if os.path.abspath(inp) == os.path.abspath(out):
                out = os.path.join(self.RUTA, f"{base_name}_converted.{out_ext}")

            duration = self.ctx.utils.get_duration(inp)
            
            cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", inp]
            if self.MODE == "- Video -": cmd += ["-c:v", "libx264", "-c:a", "aac"]
            elif self.MODE == "- Extraer Audio -": cmd += ["-vn", "-c:a", "libmp3lame"]
            cmd.append(out)
            
            self.ctx.utils.execute_with_progress(cmd, duration, prefix=f, progress_obj=progress)
        if progress: 
            progress.stop()
            # Mensaje de éxito
            self.ctx.ui.logo()
            self.ctx.ui.console.print("[bold yellow]¡Convertido correctamente![/]")
            for f in self.FILES:
                self.ctx.ui.console.print(f" [bold green]• {os.path.splitext(f)[0]}.{self.EXIT}[/]")
                self.ctx.utils.notify(f"Conversión exitosa: {f} -> {self.EXIT}", "SUCCESS")
            self.ctx.ui.console.print(f"[bold white]En:[/] [bold cyan]{self.RUTA}[/]")
            input("\nPresiona ENTER para continuar...")


        self.add_to_history(self.FILES, self.EXIT)

    def editor(self, file_path):
        while True:
            self.ctx.ui.logo()
            self.ctx.ui.console.print(f"[bold yellow]Editor:[/][bold white] {os.path.basename(file_path)}[/]")
            is_video = self.MODE == "- Video -"
            print(f"\n1. Renombrar\n2. Metadatos\n3. Recortar (Trim)")
            if is_video: print(f"4. Silenciar\n5. Escalar\n6. Rotar\n7. Fin")
            else: print(f"4. Normalizar\n5. Fade\n6. Fin")
            
            opt = self.ctx.ui.prompt("Opción")
            if opt == '1':
                new = self.ctx.ui.prompt("Nuevo nombre")
                if new:
                    new_p = os.path.join(os.path.dirname(file_path), new + os.path.splitext(file_path)[1])
                    os.rename(file_path, new_p); file_path = new_p
            elif opt == '2': self.edit_metadata(file_path)
            elif opt == '3': self.trim_file(file_path)
            if is_video:
                if opt == '4': self.mute_video(file_path)
                elif opt == '5': self.scale_video(file_path)
                elif opt == '6': self.rotate_video(file_path)
                elif opt == '7': return file_path
            else:
                if opt == '4': self.normalize_audio(file_path)
                elif opt == '5': self.apply_fade(file_path)
                elif opt == '6': return file_path

    def edit_metadata(self, f):
        t = self.ctx.ui.prompt("Título"); a = self.ctx.ui.prompt("Artista")
        tmp = f + ".meta" + os.path.splitext(f)[1]
        cmd = ["ffmpeg", "-i", f, "-metadata", f"title={t}", "-metadata", f"artist={a}", "-c", "copy", "-y", tmp]
        if self.ctx.utils.execute(cmd, capture=False)[0]: os.replace(tmp, f)

    def trim_file(self, f):
        start = self.ctx.ui.prompt("Inicio", default="00:00")
        end = self.ctx.ui.prompt("Fin")
        tmp = f + ".trim" + os.path.splitext(f)[1]
        cmd = ["ffmpeg", "-ss", start, "-i", f]
        if end: cmd += ["-to", end]
        cmd += ["-c", "copy", "-y", tmp]
        if self.ctx.utils.execute(cmd, capture=False)[0]: os.replace(tmp, f)

    def mute_video(self, f):
        tmp = f + ".mute" + os.path.splitext(f)[1]
        cmd = ["ffmpeg", "-i", f, "-an", "-vcodec", "copy", "-y", tmp]
        if self.ctx.utils.execute(cmd, capture=False)[0]: os.replace(tmp, f)

    def scale_video(self, f):
        res = self.ctx.ui.prompt("Resolución (ej: 1280:720)")
        tmp = f + ".scale" + os.path.splitext(f)[1]
        cmd = ["ffmpeg", "-i", f, "-vf", f"scale={res}", "-c:a", "copy", "-y", tmp]
        if self.ctx.utils.execute(cmd, capture=False)[0]: os.replace(tmp, f)

    def rotate_video(self, f):
        tmp = f + ".rot" + os.path.splitext(f)[1]
        cmd = ["ffmpeg", "-i", f, "-vf", "transpose=1", "-y", tmp]
        if self.ctx.utils.execute(cmd, capture=False)[0]: os.replace(tmp, f)

    def normalize_audio(self, f):
        target = self.ctx.ui.prompt("Nivel dB", default="-14")
        tmp = f + ".norm" + os.path.splitext(f)[1]
        cmd = ["ffmpeg", "-i", f, "-filter:a", f"loudnorm=I={target}", "-y", tmp]
        if self.ctx.utils.execute(cmd, capture=False)[0]: os.replace(tmp, f)

    def apply_fade(self, f):
        fi = self.ctx.ui.prompt("Fade In", default="0"); fo = self.ctx.ui.prompt("Fade Out", default="0")
        tmp = f + ".fade" + os.path.splitext(f)[1]
        cmd = ["ffmpeg", "-i", f, "-af", f"afade=t=in:d={fi},afade=t=out:d={fo}", "-y", tmp]
        if self.ctx.utils.execute(cmd, capture=False)[0]: os.replace(tmp, f)

    def post_process(self):
        self.ctx.ui.logo()
        self.ctx.ui.console.print("[bold green]¿Qué hacemos con los originales?[/]")
        print("1. Conservar\n2. Borrar\n3. Mover nuevos y borrar antiguos")
        opt = self.ctx.ui.prompt()
        if opt == '2':
            if self.ctx.ui.prompt("¿BORRAR ORIGINALES? (s/n)").lower() == 's':
                for f in self.FILES:
                    orig = os.path.join(self.RUTA, f)
                    if os.path.exists(orig):
                        try: os.remove(orig)
                        except: pass
        elif opt == '3':
            dest = self.ctx.ui.prompt("Ruta destino (o 'e')")
            if dest == 'e': dest = self.ctx.ui.file_explorer()
            if os.path.exists(dest):
                for f in self.FILES:
                    orig = os.path.join(self.RUTA, f)
                    new = os.path.join(self.RUTA, f"{os.path.splitext(f)[0]}.{self.EXIT}")
                    if os.path.exists(orig): os.remove(orig)
                    if os.path.exists(new): shutil.move(new, dest)
        self.continue_conversion()

    def search_files(self):
        term = self.ctx.ui.prompt("Buscar texto").lower()
        all_f = [f for f in os.listdir(self.RUTA) if os.path.isfile(os.path.join(self.RUTA, f))]
        matches = [f for f in all_f if term in f.lower()]
        if matches:
            self.ctx.ui.logo()
            table = Table(title=f"Resultados: {term}", border_style="yellow")
            table.add_column("N°", style="red"); table.add_column("Nombre")
            for i, f in enumerate(matches, 1): table.add_row(str(i), f)
            self.ctx.ui.console.print(table)
            sel = self.ctx.ui.prompt("Selecciona")
            indices = self.ctx.utils.parse_selection(sel, len(matches))
            self.FILES = [matches[i] for i in indices]
            if self.FILES: self.check_files()

    def copy_move_del(self, mode):
        self.ctx.ui.logo()
        all_f = [f for f in os.listdir(self.RUTA) if os.path.isfile(os.path.join(self.RUTA, f))]
        for i, f in enumerate(all_f, 1): self.ctx.ui.console.print(f"  [bold red][{i}][/] {f}")
        sel = self.ctx.ui.prompt(f"Selección para {mode}")
        selected = [all_f[i] for i in self.ctx.utils.parse_selection(sel, len(all_f))]
        if not selected: return
        if mode == 'd':
            self.ctx.ui.console.print(Panel("\n".join(selected), title="BORRAR", border_style="red"))
            if self.ctx.ui.prompt("¿BORRAR? (s/n)").lower() == 's':
                for f in selected: os.remove(os.path.join(self.RUTA, f))
        else:
            dest = self.ctx.ui.prompt("Destino")
            if os.path.exists(dest):
                for f in selected:
                    src = os.path.join(self.RUTA, f)
                    if mode == 'c': shutil.copy(src, dest)
                    else: shutil.move(src, dest)

    def add_to_history(self, files, output_fmt):
        h = []
        if os.path.exists(self.ctx.config.HISTORY_FILE):
            try: h = json.load(open(self.ctx.config.HISTORY_FILE))
            except: pass
        entry = {"date": time.strftime("%Y-%m-%d %H:%M:%S"), "path": self.RUTA, "files": files, "format": output_fmt}
        h.insert(0, entry)
        json.dump(h[:20], open(self.ctx.config.HISTORY_FILE, 'w'), indent=4)
