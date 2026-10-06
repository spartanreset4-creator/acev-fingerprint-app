import cv2
import numpy as np

def load_image_from_bytes(file_bytes):
    """Convierte los bytes subidos por Streamlit a una imagen en formato OpenCV."""
    nparr = np.frombuffer(file_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return image

def process_fingerprint_pipeline(image_bgr):
    """
    Aplica el flujo de procesamiento básico a la huella:
    1. Escala de grises
    2. Binarización con umbral de Otsu
    3. Esqueletizado / Thinning
    """
    # 1. Escala de grises
    if len(image_bgr.shape) == 3:
        gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    else:
        gray = image_bgr.copy()

    # 2. Binarización (inversa para trabajar con crestas negras/blancas según el estándar)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # 3. Esqueletizado (Guo-Hall o Zhang-Suen mediante opencv-contrib)
    skeleton = cv2.ximgproc.thinning(binary)

    return gray, binary, skeleton