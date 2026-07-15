# eqAnimSet

Generador de **videos de ecualizador animado** a partir de un archivo de audio. El script analiza el audio por bandas de frecuencia (sub-bajo, bajo, medios y brillo) y, según la energía de cada banda en cada instante, reproduce un set de frames (imágenes) tipo GIF sincronizado con la música. Al final, se le pega el audio original al video generado.

Incluye dos variantes del generador:

- **`eqAnimSet.py`** — Modo "banda dominante": en cada frame se detecta cuál banda tiene más energía y se muestra a pantalla completa el set de animación correspondiente a esa banda.
- **`eqAnimSet2.py`** — Modo "grid 2x2": la pantalla se divide en 4 cuadrantes (uno por banda) y cada uno anima su propio set de frames cuando su energía supera un umbral; si está en reposo, muestra el frame idle (el primero del set).

## Demo conceptual

```
eqAnimSet.py                     eqAnimSet2.py
┌─────────────────────┐          ┌───────────┬───────────┐
│                      │          │ subbajo   │  bajo     │
│   banda dominante    │          ├───────────┼───────────┤
│    (pantalla completa)│         │  medios   │  brillo   │
└─────────────────────┘          └───────────┴───────────┘
```

## Requisitos

- Python 3.8+
- [FFmpeg](https://ffmpeg.org/) instalado y disponible en el PATH (se usa para unir el audio final al video)
- Dependencias de Python:

```bash
pip install librosa numpy opencv-python
```

## Estructura de carpetas esperada

```
proyecto/
├── eqAnimSet.py
├── eqAnimSet2.py
├── sounds/
│   └── tu_cancion.mp3
└── frames/
    ├── subbajo/
    │   ├── 1.png
    │   ├── 2.png
    │   └── ...
    ├── bajo/
    │   ├── 1.png
    │   └── ...
    ├── medios/
    │   ├── 1.png
    │   └── ...
    └── brillo/
        ├── 1.png
        └── ...
```

- Cada subcarpeta dentro de `frames/` contiene el set de imágenes (frames) que se van a ciclar como animación para esa banda de frecuencia.
- Los archivos deben nombrarse con números (`1.png`, `2.png`, `3.png`, ...) ya que se ordenan numéricamente.
- Formatos soportados: `.png`, `.jpg`, `.jpeg` (`eqAnimSet.py` también acepta `.gif` como nombre de archivo, aunque se lee como imagen estática con OpenCV).

## Configuración

Antes de correr cualquiera de los scripts, ajustá las variables al inicio del archivo:

| Variable | Descripción |
|---|---|
| `AUDIO_PATH` | Ruta al archivo de audio (mp3, wav, etc.) |
| `FPS` | Frames por segundo del video de salida |
| `ANCHO, ALTO` | Resolución del video final |
| `CARPETA_FRAMES` | Carpeta donde están los sets de imágenes por banda |
| `bandas` | Diccionario con los rangos de frecuencia (Hz) de cada banda |
| `UMBRAL_SPIKE` *(solo `eqAnimSet2.py`)* | Nivel de energía normalizada (0–1) a partir del cual una banda se considera "activa" y avanza su animación |

## Uso

```bash
python eqAnimSet.py
```

o

```bash
python eqAnimSet2.py
```

Cada script:

1. Carga el audio y calcula el espectrograma (STFT) para obtener la energía por banda de frecuencia en cada instante de tiempo.
2. Carga los sets de frames desde `frames/<banda>/`.
3. Genera un video (`video_temp.mp4`) frame por frame, animando los sets de imágenes según la energía de audio.
4. Combina el video generado con el audio original usando `ffmpeg`, produciendo `video_final.mp4`.

## Salida

- `video_temp.mp4`: video sin audio (intermedio).
- `video_final.mp4`: video final con audio y animación sincronizada.

## Notas

- El análisis usa `librosa.stft` con `hop_length = sr / FPS`, de modo que la cantidad de frames del video coincide con la cantidad de ventanas del espectrograma.
- En `eqAnimSet.py`, cada banda tiene su propio contador de animación que solo avanza cuando esa banda es la dominante (para que el ciclo de frames no se "salte" mientras no está activa).
- En `eqAnimSet2.py`, cada cuadrante anima de forma independiente y en paralelo, dando una lectura visual simultánea de las 4 bandas.

## Licencia

Este proyecto está bajo la licencia CC0 1.0 Universal (Creative Commons Zero). Esto significa que el autor renuncia a todos los derechos de autor sobre la obra en la medida permitida por la ley, dedicándola al dominio público: podés copiar, modificar, distribuir y usar este proyecto, incluso con fines comerciales, sin pedir permiso. Ver el archivo LICENSE para el texto completo.
