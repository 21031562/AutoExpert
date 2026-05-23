from collections import Counter, defaultdict

from diagnostico import cargar_reglas, cargar_sintomas

CATEGORIAS_BASE = (
    "arranque",
    "motor",
    "combustible",
    "frenos",
    "temperatura",
    "sensores",
    "transmision",
    "direccion",
    "suspension",
)


def inferir_categoria_por_sintoma(reglas):
    frecuencia = defaultdict(Counter)

    for regla in reglas:
        modulo = regla.get("modulo", "otros")
        for condicion in regla.get("condiciones", []):
            frecuencia[condicion][modulo] += 1

    categorias = {}
    for sintoma, contador in frecuencia.items():
        categorias[sintoma] = contador.most_common(1)[0][0]

    return categorias


def construir_mapa_sintoma_categoria(sintomas, reglas):
    categorias_inferidas = inferir_categoria_por_sintoma(reglas)
    mapa = {categoria: [] for categoria in CATEGORIAS_BASE}
    mapa["otros"] = []

    for sintoma in sorted(set(sintomas)):
        categoria = categorias_inferidas.get(sintoma, "otros")
        if categoria not in mapa:
            mapa[categoria] = []
        mapa[categoria].append(sintoma)

    return mapa


def obtener_catalogo_sintomas(
    sintomas_path="sintomas.json",
    reglas_path="reglas.json",
):
    sintomas = cargar_sintomas(sintomas_path)
    reglas = cargar_reglas(reglas_path)
    return construir_mapa_sintoma_categoria(sintomas, reglas)
