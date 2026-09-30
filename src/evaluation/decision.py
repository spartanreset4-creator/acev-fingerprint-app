from enum import Enum
from typing import Dict, Any


class DecisionOutcome(str, Enum):
    IDENTIFICATION = "IDENTIFICACIÓN (Coincidencia Positiva)"
    EXCLUSION = "EXCLUSIÓN (No Coinciden)"
    INCONCLUSIVE = "INCONCLUSO (Evidencia Insuficiente)"


class Evaluator:
    """Clase encargada de emitir el dictamen forense en la fase de Evaluación (E)

    siguiendo los estándares del protocolo ACE-V.
    """

    def __init__(
        self,
        min_matches_threshold: int = 12,
        min_score_threshold: float = 0.60,
        quality_threshold: float = 0.50,
    ):
        """Parámetros:

        - min_matches_threshold: Número mínimo de minucias coincidentes requeridas.
        - min_score_threshold: Puntuación mínima de similitud (0.0 a 1.0).
        - quality_threshold: Umbral mínimo de calidad de la huella latente.
        """
        self.min_matches_threshold = min_matches_threshold
        self.min_score_threshold = min_score_threshold
        self.quality_threshold = quality_threshold

    def evaluate(
        self,
        match_result: Dict[str, Any],
        latent_quality: float = 1.0,
        reference_quality: float = 1.0,
    ) -> Dict[str, Any]:
        """Aplica las reglas de decisión forense.

        Retorna un diccionario con el dictamen, justificación técnica y nivel de confianza.
        """
        matches = match_result.get("matches", 0)
        score = match_result.get("score", 0.0)

        # 1. Comprobar suficiencia de calidad de las imágenes
        if latent_quality < self.quality_threshold:
            return {
                "decision": DecisionOutcome.INCONCLUSIVE.value,
                "reason": (
                    f"Calidad insuficiente de la huella latente ({latent_quality:.2f} < "
                    f"{self.quality_threshold:.2f}). No apta para cotejo decisivo."
                ),
                "confidence": "Baja",
                "details": {"matches": matches, "score": score},
            }

        # 2. Regla de Identificación
        if matches >= self.min_matches_threshold and score >= self.min_score_threshold:
            return {
                "decision": DecisionOutcome.IDENTIFICATION.value,
                "reason": (
                    f"Se alcanzaron {matches} minucias coincidentes con una similitud del "
                    f"{score * 100:.1f}%, superando el estándar mínimo de {self.min_matches_threshold} puntos."
                ),
                "confidence": "Alta",
                "details": {"matches": matches, "score": score},
            }

        # 3. Regla de Exclusión
        elif matches < 4 or (score < 0.25 and latent_quality >= self.quality_threshold):
            return {
                "decision": DecisionOutcome.EXCLUSION.value,
                "reason": (
                    f"Diferencias estructurales claras o discrepancias no explicables en los puntos de cotejo "
                    f"({matches} coincidencias, score: {score * 100:.1f}%)."
                ),
                "confidence": "Alta",
                "details": {"matches": matches, "score": score},
            }

        # 4. Caso Inconcluso (Zona de penumbra)
        else:
            return {
                "decision": DecisionOutcome.INCONCLUSIVE.value,
                "reason": (
                    f"Cantidad o claridad de puntos coincidentes intermedia ({matches} coincidencias, "
                    f"score: {score * 100:.1f}%). Insuficiente para afirmar identidad o exclusión con certeza."
                ),
                "confidence": "Media",
                "details": {"matches": matches, "score": score},
            }