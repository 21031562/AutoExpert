from cargar_reglas import cargar_sintomas


def obtener_sintomas():

    sintomas_disponibles = cargar_sintomas()

    sintomas_usuario = []

    print("\n========== SINTOMAS ==========\n")

    for sintoma in sintomas_disponibles:

        respuesta = input(f"{sintoma}? (s/n): ")

        if respuesta.lower() == "s":
            sintomas_usuario.append(sintoma)

    return sintomas_usuario