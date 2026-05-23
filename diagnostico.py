import json
from pathlib import Path


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


def diagnosticar(
    sintomas_usuario,
    reglas_path="reglas.json",
    sintomas_path="sintomas.json",
    min_match=0.5,
    top_n=5,
):
    reglas = cargar_reglas(reglas_path)
    sintomas_catalogo = cargar_sintomas(sintomas_path)

    sintomas_usuario = list(sintomas_usuario)
    validar_sintomas(sintomas_usuario, sintomas_catalogo)

    sintomas_usuario_set = set(sintomas_usuario)
    resultados = []

    for regla in reglas:
        condiciones = regla.get("condiciones", [])
        if not condiciones:
            continue

        condiciones_matched = [
            condicion
            for condicion in condiciones
            if condicion in sintomas_usuario_set
        ]
        condiciones_missing = [
            condicion
            for condicion in condiciones
            if condicion not in sintomas_usuario_set
        ]

        total_condiciones = len(condiciones)
        match_ratio = len(condiciones_matched) / total_condiciones

        if match_ratio < min_match:
            continue

        prioridad = regla.get("prioridad", 0)
        score = (match_ratio * 100) + prioridad

        resultados.append(
            {
                "id": regla.get("id"),
                "modulo": regla.get("modulo", "otros"),
                "diagnostico": regla.get("diagnostico", "desconocido"),
                "prueba": regla.get("prueba", "sin_prueba"),
                "solucion": regla.get("solucion", "sin_solucion"),
                "prioridad": prioridad,
                "score": round(score, 2),
                "match_ratio": round(match_ratio, 4),
                "match": f"{len(condiciones_matched)}/{total_condiciones}",
                "condiciones_matched": condiciones_matched,
                "condiciones_missing": condiciones_missing,
            }
        )

    resultados.sort(
        key=lambda item: (item["score"], item["prioridad"]),
        reverse=True,
    )

    if top_n is None:
        return resultados

    return resultados[:max(0, top_n)]
