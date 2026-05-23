import json
from pathlib import Path


PROBABLE_THRESHOLD_DEFAULT = 0.80
POSSIBLE_THRESHOLD_DEFAULT = 0.50


def _cargar_json_lista(ruta, nombre):
    ruta_archivo = Path(ruta)

    try:
        contenido = json.loads(ruta_archivo.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise FileNotFoundError(
            f"No se encontro el archivo de {nombre}: {ruta_archivo}"
        ) from exc
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"El archivo de {nombre} no contiene JSON valido: {ruta_archivo}"
        ) from exc

    if not isinstance(contenido, list):
        raise ValueError(f"El archivo de {nombre} debe contener una lista.")

    return contenido


def cargar_reglas(reglas_path="reglas.json"):
    reglas = _cargar_json_lista(reglas_path, "reglas")

    if not reglas:
        raise ValueError("No se encontraron reglas en el archivo de reglas.")

    return reglas


def cargar_sintomas(sintomas_path="sintomas.json"):
    sintomas = _cargar_json_lista(sintomas_path, "sintomas")

    if not sintomas:
        raise ValueError("No se encontraron sintomas en el archivo de sintomas.")

    return sintomas


def validar_sintomas(sintomas_usuario, sintomas_catalogo):
    sintomas_validos = set(sintomas_catalogo)
    desconocidos = sorted(set(sintomas_usuario) - sintomas_validos)

    if desconocidos:
        raise ValueError(
            f"Sintomas no validos seleccionados: {', '.join(desconocidos)}"
        )


def _evaluar_regla(regla, sintomas_usuario_set, min_match):
    condiciones = regla.get("condiciones", [])
    if not condiciones:
        return None

    condiciones_matched = [c for c in condiciones if c in sintomas_usuario_set]
    condiciones_missing = [c for c in condiciones if c not in sintomas_usuario_set]

    total_condiciones = len(condiciones)
    match_ratio = len(condiciones_matched) / total_condiciones

    if match_ratio < min_match:
        return None

    prioridad = regla.get("prioridad", 0)
    score = (match_ratio * 100) + prioridad

    return {
        "id": regla.get("id"),
        "modulo": regla.get("modulo", "otros"),
        "diagnostico": regla.get("diagnostico", "desconocido"),
        "prueba": regla.get("prueba", "sin_prueba"),
        "solucion": regla.get("solucion", "sin_solucion"),
        "prioridad": prioridad,
        "score": round(score, 2),
        # guardar también el ratio sin redondear fuerte para clasificar bien
        "match_ratio": float(match_ratio),
        "match": f"{len(condiciones_matched)}/{total_condiciones}",
        "condiciones_matched": condiciones_matched,
        "condiciones_missing": condiciones_missing,
    }


def diagnosticar(
    sintomas_usuario,
    reglas_path="reglas.json",
    sintomas_path="sintomas.json",
    min_match=POSSIBLE_THRESHOLD_DEFAULT,
    top_n=5,
):
    """
    Devuelve una lista ordenada de resultados (top_n).
    min_match controla el umbral mínimo general de resultados a incluir.
    """
    reglas = cargar_reglas(reglas_path)
    sintomas_catalogo = cargar_sintomas(sintomas_path)

    sintomas_usuario = list(sintomas_usuario)
    validar_sintomas(sintomas_usuario, sintomas_catalogo)

    sintomas_usuario_set = set(sintomas_usuario)
    resultados = []

    for regla in reglas:
        evaluado = _evaluar_regla(regla, sintomas_usuario_set, min_match=min_match)
        if evaluado:
            # redondeo solo para display: el valor real queda en match_ratio float
            evaluado["match_ratio_display"] = round(evaluado["match_ratio"], 4)
            resultados.append(evaluado)

    resultados.sort(
        key=lambda item: (item["score"], item["prioridad"]),
        reverse=True,
    )

    if top_n is None:
        return resultados

    return resultados[: max(0, top_n)]


def diagnosticar_probables_posibles(
    sintomas_usuario,
    reglas_path="reglas.json",
    sintomas_path="sintomas.json",
    probable_threshold=PROBABLE_THRESHOLD_DEFAULT,
    possible_threshold=POSSIBLE_THRESHOLD_DEFAULT,
    top_n=5,
):
    """
    Devuelve una tupla: (probables, posibles)
    - probables: match_ratio >= probable_threshold
    - posibles: possible_threshold <= match_ratio < probable_threshold
    - no devuelve < possible_threshold
    """
    # Asegurar rangos válidos
    probable_threshold = max(0.0, min(1.0, float(probable_threshold)))
    possible_threshold = max(0.0, min(1.0, float(possible_threshold)))

    # Si el usuario configura thresholds raros, normalizamos:
    if possible_threshold > probable_threshold:
        possible_threshold, probable_threshold = probable_threshold, possible_threshold

    resultados = diagnosticar(
        sintomas_usuario=sintomas_usuario,
        reglas_path=reglas_path,
        sintomas_path=sintomas_path,
        min_match=possible_threshold,
        top_n=None,  # clasificamos y luego recortamos
    )

    probables = []
    posibles = []

    for r in resultados:
        ratio = r["match_ratio"]
        if ratio >= probable_threshold:
            probables.append(r)
        elif ratio >= possible_threshold:
            posibles.append(r)

    # Mantener el orden (ya viene ordenado por score)
    if top_n is not None:
        top_n = max(1, int(top_n))
        probables = probables[:top_n]
        posibles = posibles[:top_n]

    return probables, posibles