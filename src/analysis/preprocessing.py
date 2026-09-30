import cv2
import numpy as np
from skimage.morphology import skeletonize


class FingerprintPreprocessor:
    """Clase encargada del preprocesamiento de imágenes dactiloscópicas

    para la etapa de Análisis en el protocolo ACE-V.
    """

    def __init__(self, block_size: int = 16, gabor_ksize: int = 16):
        self.block_size = block_size
        self.gabor_ksize = gabor_ksize

    def normalize(
        self, image: np.ndarray, mean_target: float = 100.0, var_target: float = 100.0
    ) -> np.ndarray:
        """Normaliza la imagen para ajustar el contraste y brillo a valores estándar."""
        image = image.astype(np.float32)
        mean_current = np.mean(image)
        var_current = np.var(image)

        if var_current == 0:
            return image.astype(np.uint8)

        normalized = np.where(
            image > mean_current,
            mean_target + np.sqrt((var_target * (image - mean_current) ** 2) / var_current),
            mean_target - np.sqrt((var_target * (image - mean_current) ** 2) / var_current),
        )

        return np.clip(normalized, 0, 255).astype(np.uint8)

    def estimate_orientation_map(self, image: np.ndarray) -> np.ndarray:
        """Calcula el mapa del ángulo local de las crestas usando gradientes Sobel."""
        gx = cv2.Sobel(image, cv2.CV_32F, 1, 0, ksize=3)
        gy = cv2.Sobel(image, cv2.CV_32F, 0, 1, ksize=3)

        vx = 2 * gx * gy
        vy = gx**2 - gy**2

        vx = cv2.GaussianBlur(vx, (5, 5), 0)
        vy = cv2.GaussianBlur(vy, (5, 5), 0)

        orientation = 0.5 * np.arctan2(vx, vy)
        return orientation

    def apply_gabor_filter(
        self, image: np.ndarray, orientation_map: np.ndarray, wavelength: float = 8.0
    ) -> np.ndarray:
        """Aplica un banco de filtros de Gabor orientados según el mapa de cresta."""
        h, w = image.shape
        enhanced = np.zeros_like(image, dtype=np.float32)

        num_angles = 16
        gabor_bank = []
        for i in range(num_angles):
            theta = i * np.pi / num_angles
            kernel = cv2.getGaborKernel(
                (self.gabor_ksize, self.gabor_ksize),
                sigma=4.0,
                theta=theta + np.pi / 2,
                lambd=wavelength,
                gamma=0.5,
                psi=0,
                ktype=cv2.CV_32F,
            )
            gabor_bank.append(kernel)

        bs = self.block_size
        for y in range(0, h, bs):
            for x in range(0, w, bs):
                block_orient = orientation_map[
                    y : min(y + bs, h), x : min(x + bs, w)
                ]
                mean_angle = np.mean(block_orient) % np.pi

                angle_idx = int(np.round(mean_angle / (np.pi / num_angles))) % num_angles
                kernel = gabor_bank[angle_idx]

                block = image[y : min(y + bs, h), x : min(x + bs, w)]
                filtered_block = cv2.filter2D(block, cv2.CV_32F, kernel)
                enhanced[y : min(y + bs, h), x : min(x + bs, w)] = filtered_block

        return cv2.normalize(enhanced, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

    def binarize_and_thin(self, enhanced_image: np.ndarray) -> np.ndarray:
        """Binariza mediante Otsu adaptativo y aplica skeletonization (esqueletización)."""
        _, binary = cv2.threshold(
            enhanced_image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
        )
        binary_bool = binary > 0
        skeleton = skeletonize(binary_bool)
        return (skeleton * 255).astype(np.uint8)

    def process(self, image_path: str) -> dict:
        """Flujo completo de Análisis de Huella."""
        raw = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if raw is None:
            raise FileNotFoundError(f"No se pudo cargar la imagen en la ruta: {image_path}")

        normalized = self.normalize(raw)
        orientation = self.estimate_orientation_map(normalized)
        enhanced = self.apply_gabor_filter(normalized, orientation)
        skeleton = self.binarize_and_thin(enhanced)

        return {
            "raw": raw,
            "normalized": normalized,
            "orientation_map": orientation,
            "enhanced": enhanced,
            "skeleton": skeleton,
        }