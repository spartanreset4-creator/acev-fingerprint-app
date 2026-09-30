import cv2
import matplotlib.pyplot as plt
import numpy as np


def draw_minutiae(
    image: np.ndarray,
    terminations: list,
    bifurcations: list,
    radius: int = 4,
) -> np.ndarray:
    """Dibuja las minucias sobre la imagen de la huella:

    - Terminaciones: Círculos rojos
    - Bifurcaciones: Círculos azules
    """
    if len(image.shape) == 2:
        output_img = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    else:
        output_img = image.copy()

    # Dibujar terminaciones (Rojo)
    for x, y in terminations:
        cv2.circle(output_img, (x, y), radius, (0, 0, 255), 1)

    # Dibujar bifurcaciones (Azul)
    for x, y in bifurcations:
        cv2.circle(output_img, (x, y), radius, (255, 0, 0), 1)

    return output_img


def plot_acev_analysis(
    raw: np.ndarray,
    enhanced: np.ndarray,
    skeleton: np.ndarray,
    minutiae_img: np.ndarray,
    save_path: str = None,
):
    """Muestra un panel 2x2 con las 4 etapas principales de la fase de Análisis (A)."""
    fig, axes = plt.subplots(2, 2, figsize=(10, 10))

    axes[0, 0].imshow(raw, cmap="gray")
    axes[0, 0].set_title("1. Original / Latente")
    axes[0, 0].axis("off")

    axes[0, 1].imshow(enhanced, cmap="gray")
    axes[0, 1].set_title("2. Filtrado Gabor")
    axes[0, 1].axis("off")

    axes[1, 0].imshow(skeleton, cmap="gray")
    axes[1, 0].set_title("3. Esqueleto (Skeleton)")
    axes[1, 0].axis("off")

    axes[1, 1].imshow(cv2.cvtColor(minutiae_img, cv2.COLOR_BGR2RGB))
    axes[1, 1].set_title("4. Minucias (Nivel 2)")
    axes[1, 1].axis("off")

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300)
        print(f"Resultado guardado en: {save_path}")

    plt.show()