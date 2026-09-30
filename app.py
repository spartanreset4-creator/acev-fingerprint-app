import os
import cv2
import numpy as np

from src.analysis.preprocessing import FingerprintPreprocessor
from src.analysis.minutiae import MinutiaeExtractor
from src.utils.visualization import draw_minutiae, plot_acev_analysis


def create_sample_fingerprint_if_missing(file_path: str):
    """Genera una imagen sintética de prueba si no existe ninguna en data/raw/."""
    if os.path.exists(file_path):
        return

    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    # Crear una imagen sintética con patrones circulares simulando cresta
    img = np.zeros((300, 300), dtype=np.uint8) + 255
    for r in range(20, 140, 12):
        cv2.circle(img, (150, 150), r, (0,), 2)

    # Introducir algunas rupturas y variaciones (simulando minucias)
    cv2.line(img, (140, 130), (160, 130), (255,), 4)
    cv2.line(img, (100, 150), (110, 150), (255,), 4)

    cv2.imwrite(file_path, img)
    print(f"Imagen de muestra generada en: {file_path}")


def main():
    sample_image_path = "data/raw/sample_fingerprint.png"

    # 1. Asegurar imagen de prueba
    create_sample_fingerprint_if_missing(sample_image_path)

    print("--- FASE 1: ANÁLISIS (ACE-V) ---")
    
    # 2. Preprocesamiento (Normalización, Gabor, Esqueleto)
    print("[1/3] Procesando imagen y aplicando filtros de Gabor...")
    preprocessor = FingerprintPreprocessor()
    results = preprocessor.process(sample_image_path)

    # 3. Extracción de Minucias (Nivel 2)
    print("[2/3] Extrayendo minucias (Crossing Number)...")
    extractor = MinutiaeExtractor()
    minutiae = extractor.extract(results["skeleton"])

    print(f" -> Terminaciones encontradas: {len(minutiae['terminations'])}")
    print(f" -> Bifurcaciones encontradas: {len(minutiae['bifurcations'])}")

    # 4. Visualización de Resultados
    print("[3/3] Generando mapa visual...")
    minutiae_img = draw_minutiae(
        results["skeleton"],
        minutiae["terminations"],
        minutiae["bifurcations"]
    )

    output_plot_path = "data/processed/analysis_result.png"
    plot_acev_analysis(
        raw=results["raw"],
        enhanced=results["enhanced"],
        skeleton=results["skeleton"],
        minutiae_img=minutiae_img,
        save_path=output_plot_path
    )


if __name__ == "__main__":
    main()