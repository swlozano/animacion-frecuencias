import librosa
import numpy as np
import cv2
import os

# --- Configuración ---
AUDIO_PATH = 'sounds/backfrom.mp3'
FPS = 24
ANCHO, ALTO = 1280, 720
CARPETA_FRAMES = 'frames'
UMBRAL_SPIKE = 0.5  # a partir de qué nivel (0-1) se considera "se disparó"

bandas = {
    'subbajo':  (20, 60),
    'bajo':     (60, 250),
    'medios':   (250, 2000),
    'brillo':   (2000, 20000),
}

# Posición de cada banda en el grid 2x2
posiciones = {
    'subbajo': (0, 0),   # arriba-izq
    'bajo':    (0, 1),   # arriba-der
    'medios':  (1, 0),   # abajo-izq
    'brillo':  (1, 1),   # abajo-der
}

ANCHO_CUAD = ANCHO // 2
ALTO_CUAD = ALTO // 2

# --- Cargar audio ---
print("Cargando audio...")
y, sr = librosa.load(AUDIO_PATH, sr=None)

hop_length = int(sr / FPS)
D = librosa.stft(y, hop_length=hop_length)
S = np.abs(D)
freqs = librosa.fft_frequencies(sr=sr)

band_masks = {nombre: (freqs >= fmin) & (freqs <= fmax) for nombre, (fmin, fmax) in bandas.items()}

# --- Calcular energía normalizada (0-1) por banda para toda la canción ---
print("Calculando energía por banda...")
energia_por_banda = {}
for nombre, mask in band_masks.items():
    energia = np.mean(S[mask, :], axis=0)
    energia_norm = energia / (np.max(energia) + 1e-9)
    energia_por_banda[nombre] = energia_norm

# --- Cargar sets de imágenes (frames) por banda ---
print("Cargando frames...")
extensiones_validas = ('.png', '.jpg', '.jpeg')
frames_por_banda = {}
for nombre in bandas:
    carpeta = os.path.join(CARPETA_FRAMES, nombre)
    archivos = sorted(
        [f for f in os.listdir(carpeta) if f.lower().endswith(extensiones_validas)],
        key=lambda x: int(os.path.splitext(x)[0])
    )
    imgs = []
    for archivo in archivos:
        img = cv2.imread(os.path.join(carpeta, archivo))
        img = cv2.resize(img, (ANCHO_CUAD, ALTO_CUAD))
        imgs.append(img)
    frames_por_banda[nombre] = imgs
    print(f"  {nombre}: {len(imgs)} frames")

# --- Generar video ---
n_frames_audio = S.shape[1]
out = cv2.VideoWriter('video_temp.mp4', cv2.VideoWriter_fourcc(*'mp4v'), FPS, (ANCHO, ALTO))

contador_anim = {nombre: 0 for nombre in bandas}

print(f"Generando {n_frames_audio} frames de video...")
for i in range(n_frames_audio):
    canvas = np.zeros((ALTO, ANCHO, 3), dtype=np.uint8)

    for nombre in bandas:
        nivel = energia_por_banda[nombre][i]
        set_frames = frames_por_banda[nombre]

        if nivel >= UMBRAL_SPIKE:
            # Se disparó -> avanza la animación
            idx = contador_anim[nombre] % len(set_frames)
            contador_anim[nombre] += 1
            frame_img = set_frames[idx]
        else:
            # En reposo -> frame idle (el primero del set)
            frame_img = set_frames[0]

        fila, col = posiciones[nombre]
        y1, y2 = fila * ALTO_CUAD, (fila + 1) * ALTO_CUAD
        x1, x2 = col * ANCHO_CUAD, (col + 1) * ANCHO_CUAD
        canvas[y1:y2, x1:x2] = frame_img

    # Líneas divisorias entre cuadrantes (opcional, estético)
    cv2.line(canvas, (ANCHO_CUAD, 0), (ANCHO_CUAD, ALTO), (30, 30, 30), 2)
    cv2.line(canvas, (0, ALTO_CUAD), (ANCHO, ALTO_CUAD), (30, 30, 30), 2)

    out.write(canvas)

    if i % 100 == 0:
        print(f"Frame {i}/{n_frames_audio}")

out.release()
print("Video sin audio generado: video_temp.mp4")

# --- Pegar audio original ---
os.system(f'ffmpeg -y -i video_temp.mp4 -i "{AUDIO_PATH}" -c:v copy -c:a aac -shortest video_final.mp4')
print("Listo: video_final.mp4")
