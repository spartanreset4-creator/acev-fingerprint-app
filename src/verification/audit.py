import datetime
from typing import Dict, Any


class VerificationAudit:
    """Clase para la Fase 4: Verificación (V) del protocolo ACE-V.

    Permite a un segundo examinador independiente auditar y validar el dictamen.
    """

    def __init__(self, verifier_name: str, verifier_id: str):
        self.verifier_name = verifier_name
        self.verifier_id = verifier_id

    def verify_decision(
        self,
        original_evaluation: Dict[str, Any],
        agree: bool,
        notes: str = "",
    ) -> Dict[str, Any]:
        """Registra la auditoría ciega o abierta del segundo examinador."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        status = "CONFIRMADO" if agree else "DISCREPANCIA / REVISIÓN REQUERIDA"

        return {
            "verifier": f"{self.verifier_name} (ID: {self.verifier_id})",
            "verification_time": timestamp,
            "original_decision": original_evaluation.get("decision"),
            "verification_status": status,
            "verifier_notes": notes,
            "is_valid": agree,
        }