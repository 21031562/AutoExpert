from cargar_reglas import cargar_reglas

reglas = cargar_reglas()


def diagnosticar(sintomas_usuario):

    resultados = []

    for regla in reglas:

        condiciones = regla["condiciones"]

        if all(condicion in sintomas_usuario
               for condicion in condiciones):

            resultados.append(regla)

    resultados.sort(
        key=lambda x: x["prioridad"],
        reverse=True
    )

    return resultados