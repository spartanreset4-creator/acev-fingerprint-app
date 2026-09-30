import numpy as np


class PatternClassifier:
    """Clase para la detección de singularidades (Núcleo y Delta) mediante Índice de Poincaré

    y clasificación automática del tipo fundamental dactilar.
    """

    def __init__(self, block_size: int = 16):
        self.block_size = block_size

    def compute_poincare_index(self, orientation_map: np.ndarray) -> np.ndarray:
        """Calcula el índice de Poincaré sobre el mapa de orientación."""
        rows, cols = orientation_map.shape
        poincare = np.zeros_like(orientation_map, dtype=float)

        for r in range(1, rows - 1):
            for c in range(1, cols - 1):
                # Vecindario de 8 celdas en sentido horario
                neighbors = [
                    orientation_map[r - 1, c - 1], orientation_map[r - 1, c],
                    orientation_map[r - 1, c + 1], orientation_map[r, c + 1],
                    orientation_map[r + 1, c + 1], orientation_map[r + 1, c],
                    orientation_map[r + 1, c - 1], orientation_map[r, c - 1],
                    orientation_map[r - 1, c - 1]
                ]

                diff_sum = 0.0
                for k in range(8):
                    diff = neighbors[k + 1] - neighbors[k]
                    while diff > np.pi / 2:
                        diff -= np.pi
                    while diff < -np.pi / 2:
                        diff += np.pi
                    diff_sum += diff

                poincare[r, c] = diff_sum / np.pi

        return poincare

    def classify(self, orientation_map: np.ndarray) -> dict:
        """Determina los núcleos, deltas y sugiere el tipo de patrón dactiloscópico."""
        poincare = self.compute_poincare_index(orientation_map)

        # Detectar singularidades
        cores = np.argwhere(np.abs(poincare - 0.5) < 0.25)
        deltas = np.argwhere(np.abs(poincare + 0.5) < 0.25)

        num_cores = len(cores)
        num_deltas = len(deltas)

        # Regla Dactiloscópica Estándar
        if num_deltas == 0 or (num_cores == 0 and num_deltas == 0):
            predicted_pattern = "Arco (Adeltico)"
        elif num_deltas == 1 or num_cores == 1:
            predicted_pattern = "Presilla (Monodeltico)"
        elif num_deltas >= 2 or num_cores >= 2:
            predicted_pattern = "Verticilo (Bideltico / Polideltico)"
        else:
            predicted_pattern = "Indeterminado"

        return {
            "predicted_pattern": predicted_pattern,
            "cores_count": num_cores,
            "deltas_count": num_deltas,
        }