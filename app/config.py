#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import json

class Config:
    """Centraliza todas las rutas y configuraciones del proyecto."""
    def __init__(self):
        self.BASE_DIR = os.path.expanduser("~/.milux")
        self.LOG_DIR = os.path.join(self.BASE_DIR, "logs")
        self.PROJECTS_DIR = os.path.expanduser("~/ConverterProjects")
        self.HISTORY_FILE = os.path.join(self.BASE_DIR, "history.json")
        self.CONFIG_FILE = os.path.join(self.BASE_DIR, "settings.json")
        self.NOTIF_LOG = os.path.join(self.BASE_DIR, "notifications.log")
        self.CAV_FILE = os.path.join(self.BASE_DIR, "cav.mlx")
        self.CCV_FILE = os.path.join(self.BASE_DIR, "ccv.mlx")
        self.CHANGELOG_FILE = os.path.join(self.BASE_DIR, "changelog.txt")
        
        self._ensure_dirs()
        self.data = self._load()

    def _ensure_dirs(self):
        for d in [self.BASE_DIR, self.LOG_DIR, self.PROJECTS_DIR]:
            os.makedirs(d, exist_ok=True)

    def _load(self):
        if os.path.exists(self.CONFIG_FILE):
            try:
                with open(self.CONFIG_FILE, 'r') as f: return json.load(f)
            except: pass
        return {"theme": "default", "last_path": os.path.expanduser("~")}

    def save(self):
        with open(self.CONFIG_FILE, 'w') as f:
            json.dump(self.data, f, indent=4)

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value
        self.save()
