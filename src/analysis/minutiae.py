import cv2
import numpy as np


class MinutiaeExtractor:
    """Extractor de minucias (terminaciones y bifurcaciones) usando el método Crossing Number (CN)."""

    def __init__(self, border_margin: int = 10):
        self.border_margin = border_margin

    def get_crossing_number(self, region: np.ndarray) -> int:
        """Calcula el Crossing Number (CN) para un píxel central en una vecindad de 3x3.

        P8 P1 P2
        P7 P0 P3
        P6 P5 P4
        """
        # Secuencia de vecinos en sentido horario
        p = [
            region[0, 1],
            region[0, 2],
            region[1, 2],
            region[2, 2],
            region[2, 1],
            region[2, 0],
            region[1, 0],
            region[0, 0],
            region[0, 1],
        ]
        return sum(abs(int(p[i]) - int(p[i + 1])) for i in range(8)) // 2

    def extract(self, skeleton: np.ndarray) -> dict:
        """Saca las coordenadas y tipo de minucias desde la imagen esqueletizada (0 y 255)."""
        # Convertir a matriz binaria de 0s y 1s
        skel_binary = (skeleton > 0).astype(np.uint8)
        h, w = skel_binary.shape

        terminations = []
        bifurcations = []

        for y in range(self.border_margin, h - self.border_margin):
            for x in range(self.border_margin, w - self.border_margin):
                if skel_binary[y, x] == 1:
                    region = skel_binary[y - 1 : y + 2, x - 1 : x + 2]
                    cn = self.get_crossing_number(region)

                    if cn == 1:
                        terminations.append((x, y))
                    elif cn == 3:
                        bifurcations.append((x, y))

        return {
            "terminations": terminations,
            "bifurcations": bifurcations,
        }