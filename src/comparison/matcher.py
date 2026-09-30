import numpy as np


class MinutiaeMatcher:
    """Clase para la Fase de Comparación (C) en el protocolo ACE-V.

    Alinea espacialmente y compara dos conjuntos de minucias.
    """

    def __init__(self, distance_threshold: float = 12.0):
        self.distance_threshold = distance_threshold

    def align_and_match(self, minutiae_a: dict, minutiae_b: dict) -> dict:
        """Compara minucias de la Huella A (Dudosa) y Huella B (Referencia).

        Retorna el número de coincidencias y un score normalizado.
        """
        pts_a = np.array(minutiae_a.get("terminations", []) + minutiae_a.get("bifurcations", []))
        pts_b = np.array(minutiae_b.get("terminations", []) + minutiae_b.get("bifurcations", []))

        if len(pts_a) == 0 or len(pts_b) == 0:
            return {"matches": 0, "score": 0.0, "matched_pairs": []}

        matched_pairs = []
        matched_b_indices = set()

        # Cálculo de distancia euclidiana directa sin depender de np.linalg
        for pt_a in pts_a:
            diffs = pts_b - pt_a
            distances = np.sqrt(np.sum(diffs ** 2, axis=1))
            min_idx = int(np.argmin(distances))
            min_dist = distances[min_idx]

            if min_dist <= self.distance_threshold and min_idx not in matched_b_indices:
                matched_pairs.append((pt_a.tolist(), pts_b[min_idx].tolist()))
                matched_b_indices.add(min_idx)

        total_minutiae = min(len(pts_a), len(pts_b))
        score = (len(matched_pairs) / total_minutiae) if total_minutiae > 0 else 0.0

        return {
            "matches": len(matched_pairs),
            "score": round(score, 4),
            "matched_pairs": matched_pairs,
        }