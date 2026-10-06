import cv2
import numpy as np

def extract_minutiae(skeleton_img, margin=10):
    """
    Extrae terminaciones y bifurcaciones utilizando el método Crossing Number (CN).
    Aplica un margen para omitir los bordes falsos de la huella.
    """
    # Asegurarse de que la imagen sea binaria (0 y 255 o 0 y 1)
    binary = (skeleton_img > 0).astype(np.uint8)
    height, width = binary.shape
    
    terminations = []
    bifurcations = []

    for y in range(margin, height - margin):
        for x in range(margin, width - margin):
            if binary[y, x] == 1:
                # Vecindario de 3x3 ordenado en sentido horario alrededor de (y, x)
                # P2 P3 P4
                # P9 P1 P5
                # P8 P7 P6
                p2 = binary[y - 1, x]
                p3 = binary[y - 1, x + 1]
                p4 = binary[y, x + 1]
                p5 = binary[y + 1, x + 1]
                p6 = binary[y + 1, x]
                p7 = binary[y + 1, x - 1]
                p8 = binary[y, x - 1]
                p9 = binary[y - 1, x - 1]

                neighbors = [p2, p3, p4, p5, p6, p7, p8, p9, p2]
                
                # Crossing Number: CN = 0.5 * sum(|P_i - P_{i+1}|)
                cn = 0.5 * sum(abs(int(neighbors[i]) - int(neighbors[i + 1])) for i in range(8))

                if cn == 1:
                    terminations.append((y, x))
                elif cn == 3:
                    bifurcations.append((y, x))

    return terminations, bifurcations


def draw_minutiae(image, terminations, bifurcations):
    """
    Dibuja las minucias sobre la imagen dada (sea a color o escala de grises).
    Terminaciones -> Círculos Rojos
    Bifurcaciones -> Círculos Azules
    """
    if len(image.shape) == 2:
        output = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    else:
        output = image.copy()

    # Dibujar Terminaciones (Rojo)
    for y, x in terminations:
        cv2.circle(output, (int(x), int(y)), 4, (255, 0, 0), 1)
        cv2.circle(output, (int(x), int(y)), 1, (255, 0, 0), -1)

    # Dibujar Bifurcaciones (Azul)
    for y, x in bifurcations:
        cv2.circle(output, (int(x), int(y)), 4, (0, 0, 255), 1)
        cv2.circle(output, (int(x), int(y)), 1, (0, 0, 255), -1)

    return output