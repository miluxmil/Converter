# 🎬 CONVERTER

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/Platform-Termux%20%7C%20Linux-green?logo=linux&logoColor=white" alt="Platform: Termux / Linux">
  <img src="https://img.shields.io/badge/License-GPL--3.0--or--later-blue.svg" alt="License: GPL-3.0-or-later">
  <img src="https://img.shields.io/badge/UI-Rich-brightgreen" alt="Rich UI">
</p>

```
      \_/
     (* *)
    __)#(__
   ( )...( )(_)  C O N V E R T E R
   || |_| ||//           By
>==() | | ()/      </[M]iLu{×}_> | DNP
    _(___)_
   [-]   [-]        Music - Video - Images
```

**CONVERTER** es una potente suite multimedia de terminal modular, diseñada especialmente para **Termux** y entornos **Linux**. Combina la potencia de **FFmpeg**, **ImageMagick** y **yt-dlp** bajo una interfaz visual en terminal (TUI) moderna, interactiva y fluida desarrollada con [Rich](https://github.com/Textualize/rich).

---

## 🚀 Características Principales

### 🎵 1. Conversión y Edición de Audio
- Conversión por lotes entre formatos (**MP3**, **WAV**, **OGG**, etc.).
- Editor de audio integrado:
  - Edición de metadatos (Título, Artista).
  - Recorte de fragmentos (Trim por marcas de tiempo).
  - Normalización de volumen mediante `loudnorm` con nivel configurable en dB.
  - Efectos de desvanecimiento de entrada y salida (*Fade In* / *Fade Out*).
- Barras de progreso precisas calculadas a partir de la duración del audio.

### 🖼️ 2. Conversión de Imágenes
- Conversión rápida entre formatos populares (**JPG**, **PNG**, **WEBP**, etc.).
- Soporte para procesamiento individual y por lotes.

### 🎬 3. Conversión y Manipulación de Video
- Transcodificación a formatos estándar (**MP4**, **MKV**, **AVI** con H.264 y AAC).
- Editor de video integrado:
  - Recorte de video (*Trim*).
  - Reescalado de resolución (ej. `1280:720`, `1920:1080`).
  - Silenciado de audio (*Mute* / eliminación de pistas sonoras).
  - Rotación de video (transposición 90°/180°).
  - Edición de metadatos.

### ✂️ 4. Extracción de Audio
- Extracción directa de pistas de audio desde cualquier formato de video a **MP3**, **WAV** u **OGG** de alta calidad con un solo clic.

### 🌐 5. Descargas desde Internet (`yt-dlp`)
- Descarga de videos y música desde plataformas soportadas mediante `yt-dlp`.
- Opciones para descargar video en máxima calidad, extraer MP3 directo o mantener audio original.
- Configuración de ruta personalizada para descargas.
- Conexión directa: permite enviar el archivo recién descargado al módulo de conversión de forma automática.

### 💾 6. Gestor Avanzado de Almacenamiento (Storage)
- **Monitoreo de Disco**: Gráfico visual en tiempo real de espacio disponible y utilizado.
- **Analizador de Espacio**: Calcula recursivamente el peso de cada subcarpeta.
- **Detector de Archivos Grandes**: Localiza archivos que superan un umbral personalizable en MB y permite su borrado interactivo.
- **Limpieza de Temporales**: Vaciado seguro de carpetas temporales y caché del sistema.
- **Organizador de Archivos**: Clasifica automáticamente archivos sueltos en carpetas temáticas (`Imagenes`, `Videos`, `Audio`, `Documentos`, `Comprimidos`).
- **Buscador de Duplicados**: Identifica duplicados reales mediante comparación de hash MD5.
- **Compresor ZIP**: Selección múltiple o por rangos de archivos para empaquetar en `.zip`.
- **Limpiador de Cachés**: Purga de cachés de `pip` y `npm`.
- **Eliminación de Carpetas Vacías**: Remueve ramas de directorios sin contenido.
- **CorpseFinder**: Escaneo inteligente de archivos basura (`.tmp`, `.bak`, `.swp`, etc.) y detección de paquetes huérfanos.

### ⚡ 7. Herramientas Profesionales (Modo Avanzado)
- **Editor FFmpeg Pro & Magick Pro**: Ejecución de comandos avanzados con soporte completo de argumentos entrecomillados.
- **Monitor de Sistema**: Visualización de procesos en vivo con `top`.
- **Consola Profesional**: Shell integrada con advertencia de seguridad y entorno configurado.
- **Verificación de Integridad Multimedia**: Detección de streams corruptos o errores en contenedores de video.
- **Benchmark de Rendimiento**: Mide velocidad de procesamiento (`speed`) y tiempo de uso de CPU en decodificación.
- **Generador de Espectrogramas**: Crea representaciones visuales del espectro acústico en imagen PNG (`showspectrumpic`).
- **Informe Técnico**: Inspección exhaustiva de metadatos, códecs y streams usando `ffprobe` en formato JSON coloreado.

### 🔔 8. Notificaciones e Historial
- Registro persistente de conversiones y eventos.
- Historial accesible con fechas, formatos y número de archivos procesados.
- Centro de notificaciones con niveles de severidad (`SUCCESS`, `INFO`, `WARN`, `ERROR`).

---

## 📋 Requisitos del Sistema

### En Termux (Android):
```bash
pkg update && pkg upgrade -y
pkg install python ffmpeg imagemagick curl yt-dlp -y
```

### En Debian / Ubuntu / Linux Mint:
```bash
sudo apt update
sudo apt install -y python3 python3-pip ffmpeg imagemagick curl yt-dlp
```

### En Arch Linux:
```bash
sudo pacman -S python python-pip ffmpeg imagemagick curl yt-dlp
```

---

## 📦 Instalación

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/miluxmil/Converter.git
   cd Converter
   ```

2. **Instalar dependencias de Python:**
   ```bash
   pip install -r requirements.txt
   ```
   *(Nota: Si no se instala previamente, el script `main.py` cuenta con un sistema de auto-instalación que detecta e instala `rich` automáticamente).*

3. **Verificar el entorno:**
   ```bash
   python3 main.py --check
   ```

---

## 🎮 Uso

Para iniciar la aplicación interactiva:

```bash
python3 main.py
```

### Controles y Atajos Globales en la TUI:
- `b`: Volver al menú anterior.
- `mi`: Regresar al menú principal en cualquier momento.
- `s`: Confirmar selección (en explorador de carpetas).
- `..`: Subir un nivel en el explorador de archivos.
- `o [N°]`: Abrir archivo con la aplicación predeterminada del sistema (`termux-open`).
- Selecciones múltiples: Acepta listas separadas por espacios o comas y rangos (ej. `1 3 5-8`).

---

## 📁 Estructura del Proyecto

```text
Converter/
├── main.py                     # Punto de entrada principal y bootstrap
├── requirements.txt            # Dependencias de Python
├── LICENSE                     # Licencia GNU GPL v3.0 o posterior
├── README.md                   # Documentación oficial
└── app/
    ├── __init__.py             # Inicializador del paquete app
    ├── config.py               # Gestión centralizada de rutas y configuraciones
    ├── core.py                 # Orquestador del ciclo de vida y menús principales
    ├── ui.py                   # Renderizado de interfaz visual con Rich
    ├── utils.py                # Utilidades de sistema, subprocesos y dependencias
    └── modules/
        ├── __init__.py
        ├── conversion.py       # Lógica de conversión, lotes y edición multimedia
        ├── storage.py          # Analizador de almacenamiento, limpieza y compresión
        ├── internet.py         # Descargas multimedia con yt-dlp
        ├── advanced.py         # Diagnóstico, espectrogramas y benchmarks
        └── notification.py     # Centro de notificaciones y logs
```

---

## 📄 Licencia

Este proyecto se distribuye bajo los términos de la **GNU General Public License v3.0 o posterior (GPL-3.0-or-later)**.

Consulta el archivo [LICENSE](LICENSE) para obtener los términos y condiciones completos de la licencia.

```text
Converter is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
```

---

## 👤 Autor

Desarrollado con dedicación por:
- **</[M]iLu{×}_> | DNP**
- Repositorio: [miluxmil/Converter](https://github.com/miluxmil/Converter)
- Telegram: [t.me/miluxmil](t.me/miluxmil)
