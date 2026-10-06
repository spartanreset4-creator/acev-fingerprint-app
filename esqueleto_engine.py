import cv2
import numpy as np

def extraer_esqueleto_y_minucias(imagen_input):
    """
    Procesa la huella y devuelve:
    1. img_binaria: Máscara blanca y negra de alto contraste
    2. img_esqueleto: Esqueleto delgado línea por línea
    3. img_minucias: Esqueleto con puntos de minucias (rojos y azules)
    4. minucias: Lista con las coordenadas de las minucias
    """
    # 1. Cargar la imagen
    if isinstance(imagen_input, str):
        img_bgr = cv2.imread(imagen_input)
    else:
        img_bgr = imagen_input.copy() if len(imagen_input.shape) == 3 else cv2.cvtColor(imagen_input, cv2.COLOR_GRAY2BGR)

    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

    # 2. Ecualización CLAHE para maximizar contraste de crestas
    clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(8, 8))
    img_contrast = clahe.apply(gray)
    blurred = cv2.medianBlur(img_contrast, 5)

    # 3. Binarización Adaptativa Inversa (Crestas = Blanco)
    img_binaria = cv2.adaptiveThreshold(
        blurred,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        blockSize=21,
        C=5
    )

    # Limpieza morfológica
    kernel_close = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    img_binaria = cv2.morphologyEx(img_binaria, cv2.MORPH_CLOSE, kernel_close)

    # 4. Esqueletización Real (Thinning Zhang-Suen)
    try:
        img_esqueleto = cv2.ximgproc.thinning(img_binaria, thinningType=cv2.ximgproc.THINNING_ZHANGSUEN)
    except AttributeError:
        img_esqueleto = np.zeros(img_binaria.shape, np.uint8)
        element = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
        temp_bin = img_binaria.copy()
        while True:
            eroded = cv2.erode(temp_bin, element)
            temp = cv2.dilate(eroded, element)
            temp = cv2.subtract(temp_bin, temp)
            img_esqueleto = cv2.bitwise_or(img_esqueleto, temp)
            temp_bin = eroded.copy()
            if cv2.countNonZero(temp_bin) == 0:
                break

    # 5. Extracción de Minucias sobre el Esqueleto
    skel_norm = img_esqueleto // 255
    h, w = skel_norm.shape
    
    minucias = []
    img_minucias = cv2.cvtColor(img_esqueleto, cv2.COLOR_GRAY2BGR)
    margin = 20

    for y in range(margin, h - margin):
        for x in range(margin, w - margin):
            if skel_norm[y, x] == 1:
                neighborhood = skel_norm[y-1:y+2, x-1:x+2]
                p = [
                    neighborhood[0, 1], neighborhood[0, 2], neighborhood[1, 2],
                    neighborhood[2, 2], neighborhood[2, 1], neighborhood[2, 0],
                    neighborhood[1, 0], neighborhood[0, 0], neighborhood[0, 1]
                ]
                cn = 0.5 * sum(abs(p[i] - p[i+1]) for i in range(8))

                if cn == 1:
                    minucias.append({'x': x, 'y': y, 'tipo': 'Fin de Cresta'})
                    cv2.circle(img_minucias, (x, y), 3, (0, 0, 255), -1)  # Rojo

                elif cn == 3:
                    minucias.append({'x': x, 'y': y, 'tipo': 'Bifurcación'})
                    cv2.circle(img_minucias, (x, y), 3, (255, 0, 0), -1)  # Azul

    return img_binaria, img_esqueleto, img_minucias, minucias