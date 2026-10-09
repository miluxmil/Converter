#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import subprocess
import shutil
import time
import re
import logging
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TaskProgressColumn, TimeRemainingColumn

class Utils:
    """Clase de utilidades con soporte para logging y progreso optimizado."""
    def __init__(self, core):
        self.ctx = core
        self._setup_logging()

    def _setup_logging(self):
        log_file = os.path.join(self.ctx.config.LOG_DIR, "converter.log")
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(message)s'
        )
        self.logger = logging.getLogger("Converter")

    def log(self, message, level="info"):
        """Registra un mensaje en el log de desarrollo."""
        if level == "info": self.logger.info(message)
        elif level == "error": self.logger.error(message)
        elif level == "warning": self.logger.warning(message)

    def notify(self, message, category="INFO"):
        """Registra una notificación para el usuario en el Centro de Notificaciones."""
        log_file = self.ctx.config.NOTIF_LOG
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        try:
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            with open(log_file, "a") as f:
                f.write(f"[{timestamp}] [{category.upper()}] {message}\n")
        except: pass

    def execute(self, cmd, capture=True):
        try:
            self.log(f"CMD: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
            res = subprocess.run(cmd, check=True, capture_output=capture, text=True if capture else False)
            return True, res.stdout if capture else None
        except Exception as e:
            self.log(f"FAIL: {str(e)}", "error")
            return False, str(e)

    def get_duration(self, file_path):
        cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", file_path]
        success, out = self.execute(cmd)
        try: return float(out.strip()) if success else 0
        except: return 0

    def execute_with_progress(self, cmd, duration, prefix="Archivo", progress_obj=None):
        """Ejecuta FFmpeg con diseño optimizado para evitar desbordamiento en Termux."""
        if duration <= 0: return self.execute(cmd, capture=False)[0]
        
        display_name = (prefix[:30] + '..') if len(prefix) > 32 else prefix
        
        if progress_obj is None:
            with Progress(
                SpinnerColumn(),
                TextColumn("[bold blue]{task.fields[filename]}"),
                BarColumn(bar_width=20),
                TaskProgressColumn(),
                TimeRemainingColumn(),
                console=self.ctx.ui.console,
                transient=True
            ) as local_progress:
                task = local_progress.add_task("Procesando", total=duration, filename=display_name)
                return self._run_ffmpeg_loop(cmd, local_progress, task)
        else:
            task = progress_obj.add_task("Procesando", total=duration, filename=display_name)
            return self._run_ffmpeg_loop(cmd, progress_obj, task)

    def _run_ffmpeg_loop(self, cmd, progress, task):
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        time_pattern = re.compile(r"time=(\d+):(\d+):(\d+\.\d+)")
        for line in process.stdout:
            match = time_pattern.search(line)
            if match:
                h, m, s = map(float, match.groups())
                curr = h * 3600 + m * 60 + s
                progress.update(task, completed=curr)
        process.wait()
        progress.update(task, completed=progress.tasks[task].total)
        return process.returncode == 0

    def parse_selection(self, s, max_v):
        res = set()
        for p in s.replace(',', ' ').split():
            try:
                if '-' in p:
                    a, b = map(int, p.split('-'))
                    for i in range(min(a,b), max(a,b)+1):
                        if 1 <= i <= max_v: res.add(i-1)
                elif 1 <= int(p) <= max_v: res.add(int(p)-1)
            except: continue
        return sorted(list(res))

    def is_installed(self, pkg): 
        """Verifica si un binario o un módulo de Python está instalado."""
        # Si el nombre empieza con 'python:', verificamos como módulo
        if pkg.startswith("python:"):
            module_name = pkg.split(":")[1]
            try:
                __import__(module_name)
                return True
            except ImportError:
                return False
        # Si no, verificamos como binario del sistema
        return shutil.which(pkg) is not None

    def install_missing(self, packages):
        """Intenta instalar paquetes del sistema o de Python."""
        manager = None
        if shutil.which("pkg"): manager = "pkg"
        elif shutil.which("apt-get"): manager = "apt-get"
        
        system_pkgs = [p for p in packages if not p.startswith("python:")]
        python_pkgs = [p.split(":")[1] for p in packages if p.startswith("python:")]

        # Instalar paquetes del sistema
        if system_pkgs and manager:
            for pkg in system_pkgs:
                pkg_name = pkg
                if pkg == "mogrify": pkg_name = "imagemagick"
                cmd = [manager, "install", "-y", pkg_name]
                if manager != "pkg" and shutil.which("sudo"): cmd = ["sudo"] + cmd
                self.execute(cmd, capture=False)

        # Instalar paquetes de Python
        if python_pkgs:
            self.notify(f"Instalando módulos Python: {', '.join(python_pkgs)}", "INFO")
            for py_pkg in python_pkgs:
                cmd = [sys.executable, "-m", "pip", "install", py_pkg]
                self.execute(cmd, capture=False)
        
        return True
