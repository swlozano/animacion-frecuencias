import librosa
import numpy as np
import cv2
import os

# --- Configuración ---
AUDIO_PATH = 'sounds/nookie.mp3'
FPS = 24
ANCHO, ALTO = 1280, 720
CARPETA_FRAMES = 'frames'

bandas = {
    'subbajo':  (20, 60),
    'bajo':     (60, 250),
    'medios':   (250, 2000),
    'brillo':   (2000, 20000),
}

# --- Cargar audio ---
print("Cargando audio...")
y, sr = librosa.load(AUDIO_PATH, sr=None)

hop_length = int(sr / FPS)
D = librosa.stft(y, hop_length=hop_length)
S = np.abs(D)
freqs = librosa.fft_frequencies(sr=sr)

band_masks = {nombre: (freqs >= fmin) & (freqs <= fmax) for nombre, (fmin, fmax) in bandas.items()}

# --- Cargar sets de imágenes (frames) por banda ---
print("Cargando frames...")
frames_por_banda = {}
for nombre in bandas:
    carpeta = os.path.join(CARPETA_FRAMES, nombre)
    extensiones_validas = ('.png', '.jpg', '.jpeg', '.gif')
    archivos = sorted(
        [f for f in os.listdir(carpeta) if f.lower().endswith(extensiones_validas)],
        key=lambda x: int(os.path.splitext(x)[0])
    )
    imgs = []
    for archivo in archivos:
        img = cv2.imread(os.path.join(carpeta, archivo))
        img = cv2.resize(img, (ANCHO, ALTO))
        imgs.append(img)
    frames_por_banda[nombre] = imgs
    print(f"  {nombre}: {len(imgs)} frames")

# --- Generar video ---
n_frames_audio = S.shape[1]
out = cv2.VideoWriter('video_temp.mp4', cv2.VideoWriter_fourcc(*'mp4v'), FPS, (ANCHO, ALTO))

# Contador de animación independiente por banda (para que cicle sus frames)
contador_anim = {nombre: 0 for nombre in bandas}

print(f"Generando {n_frames_audio} frames de video...")
for i in range(n_frames_audio):
    # Energía de cada banda en este instante
    energias = {nombre: np.mean(S[mask, i]) for nombre, mask in band_masks.items()}
    banda_dominante = max(energias, key=energias.get)

    # Set de frames de la banda dominante
    set_frames = frames_por_banda[banda_dominante]

    # Avanza el contador de animación SOLO de la banda activa (ciclo tipo GIF)
    idx = contador_anim[banda_dominante] % len(set_frames)
    frame_img = set_frames[idx]
    contador_anim[banda_dominante] += 1

    out.write(frame_img)

    if i % 100 == 0:
        print(f"Frame {i}/{n_frames_audio} -> {banda_dominante} (frame {idx})")

out.release()
print("Video sin audio generado: video_temp.mp4")

# --- Pegar audio original ---
os.system(f'ffmpeg -y -i video_temp.mp4 -i "{AUDIO_PATH}" -c:v copy -c:a aac -shortest video_final.mp4')
print("Listo: video_final.mp4")