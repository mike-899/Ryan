import cv2
import numpy as np

# ----------------------------
# Parámetros ajustables
# ----------------------------
HSV_THRESHOLDS = {
    "verde": ((35, 80, 60), (85, 255, 255)),
    "negro": ((0, 0, 0), (180, 255, 50)),
    "blanco": ((0, 0, 200), (180, 50, 255)),
}
MIN_RATIO = 0.30            # ratio mínimo (pixeles_detectados / area_ROI) para declarar predominancia
MORPH_KERNEL = (3, 3)
USE_MEDIAN_BLUR = True
BLUR_KSIZE = 5              # debe ser impar >=3 si USE_MEDIAN_BLUR True
CAM_INDEXS = [3, 0, 1, 2]   # orden de intentos para abrir la cámara
DEBUG = False                # imprime ratios, caso y acción por iteración
# ----------------------------

def clamp_coords(x1, y1, x2, y2, w, h):
    x1 = max(0, min(w - 1, int(x1)))
    x2 = max(0, min(w, int(x2)))
    y1 = max(0, min(h - 1, int(y1)))
    y2 = max(0, min(h, int(y2)))
    if x2 <= x1 or y2 <= y1:
        return None
    return x1, y1, x2, y2

def detectar_color_en_roi(hsv_frame, coords):
    """Devuelve (color_predominante, mejor_ratio) para el ROI dado."""
    h, w = hsv_frame.shape[:2]
    clamped = clamp_coords(*coords, w=w, h=h)
    if clamped is None:
        return "indefinido", 0.0
    x1, y1, x2, y2 = clamped
    roi = hsv_frame[y1:y2, x1:x2]
    if roi.size == 0:
        return "indefinido", 0.0

    if USE_MEDIAN_BLUR and BLUR_KSIZE >= 3 and BLUR_KSIZE % 2 == 1:
        roi = cv2.medianBlur(roi, BLUR_KSIZE)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, MORPH_KERNEL)
    best_color = "indefinido"
    best_ratio = 0.0
    area = (x2 - x1) * (y2 - y1)
    if area == 0:
        return "indefinido", 0.0

    for color_name, (low, high) in HSV_THRESHOLDS.items():
        low = np.array(low, dtype=np.uint8)
        high = np.array(high, dtype=np.uint8)
        mask = cv2.inRange(roi, low, high)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
        count = int(cv2.countNonZero(mask))
        ratio = count / area
        if ratio > best_ratio:
            best_ratio = ratio
            best_color = color_name

    if best_ratio >= MIN_RATIO:
        return best_color, best_ratio
    return "indefinido", best_ratio

def mov(grado):
    mapping = {
        90: "adelante",
        0: "izquierda",
        1: "izquierdaYAjuste",
        180: "derecha",
        181: "derechaYAjuste",
        270: "atras"
    }
    return mapping.get(grado, "No existe(No se que paso entonces XD)")

def abrir_camara(indices_preferidos):
    for idx in indices_preferidos:
        cap = cv2.VideoCapture(idx)
        if cap.isOpened():
            if DEBUG:
                print(f"[DEBUG] Cámara abierta en índice {idx}")
            return cap
        cap.release()
    return None

def main():
    # Definición de segmentos (x1,y1,x2,y2)
    segmentos = {
        "segmento1": (100, 200, 200, 300),
        "segmento2": (400, 200, 500, 300),
        "segmento3": (250, 50, 350, 150),
        "segmento4": (100, 400, 200, 500),
        "segmento5": (400, 400, 500, 500),
    }

    camara = abrir_camara(CAM_INDEXS)
    if camara is None:
        print("Error al abrir la cámara. Probá cambiar CAM_INDEXS.")
        return

    while True:
        ret, frame = camara.read()
        if not ret or frame is None:
            print("Error al capturar frame")
            break

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        resultados = {}
        ratios = {}
        for nombre, coords in segmentos.items():
            color, ratio = detectar_color_en_roi(hsv, coords)
            resultados[nombre] = color
            ratios[nombre] = ratio

        # seg4_flag según tu lógica original: si segmento4 o 5 son negro o verde
        seg4_flag = resultados["segmento4"] in ("negro", "verde") or resultados["segmento5"] in ("negro", "verde")

        # Dibujar rectángulos y etiquetas
        for nombre, coords in segmentos.items():
            clamped = clamp_coords(*coords, w=frame.shape[1], h=frame.shape[0])
            if clamped is None:
                continue
            x1, y1, x2, y2 = clamped
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            text = f"{nombre}: {resultados[nombre]} ({ratios[nombre]:.2f})"
            cv2.putText(frame, text, (x1, max(10, y1 - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 0), 1)

        # Decisión usando match/case (Python 3.10+)
        c1 = resultados["segmento1"]
        c2 = resultados["segmento2"]
        c3 = resultados["segmento3"]
        accion = None
        caso = None

        match (c1, c2, c3, seg4_flag):
            case ("verde", "verde", _, _):
                accion = mov(270)
                caso = "c1_y_c2_verde"
            case ("verde", _, _, False):
                accion = mov(1)
                caso = "c1_verde_no_seg4"
            case (_, "verde", _, False):
                accion = mov(181)
                caso = "c2_verde_no_seg4"
            case (_, _, "negro", _) if c1 != "verde" and c2 != "verde":
                accion = mov(90)
                caso = "c3_negro_sin_c1_c2_verde"
            case (_, _, "negro", _) if c1 == "verde" and not seg4_flag:
                accion = mov(1)
                caso = "c3_negro_y_c1_verde_no_seg4"
            case (_, _, "negro", _) if c2 == "verde" and not seg4_flag:
                accion = mov(181)
                caso = "c3_negro_y_c2_verde_no_seg4"
            case ("blanco", "blanco", _, _):
                accion = mov(90)
                caso = "c1_c2_blanco"
            case ("negro", "blanco", _, _):
                accion = mov(0)
                caso = "c1_negro_c2_blanco"
            case ("blanco", "negro", _, _):
                accion = mov(180)
                caso = "c1_blanco_c2_negro"
            case _:
                accion = mov(90)
                caso = "fallback"

        if DEBUG:
            print(f"[DEBUG] Resultados: c1={c1}({ratios['segmento1']:.2f}), c2={c2}({ratios['segmento2']:.2f}), c3={c3}({ratios['segmento3']:.2f}), seg4_flag={seg4_flag}")
            print(f"[DEBUG] Caso disparado: {caso} -> Accion: {accion}")

        # Un solo print/mandado por ciclo
        print("Accion:", accion)

        cv2.imshow("Deteccion de colores (final, match/case)", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    camara.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
