from motor_inferencia import diagnosticar

caso1 = [
    "no_enciende",
    "tablero_debil",
    "click_al_girar_llave"
]

caso2 = [
    "humo_blanco",
    "temperatura_alta"
]

caso3 = [
    "pedal_esponjoso"
]

casos = [caso1, caso2, caso3]

for i, caso in enumerate(casos, start=1):

    print(f"\n======= CASO {i} =======")

    resultados = diagnosticar(caso)

    if resultados:

        print(resultados[0]["diagnostico"])

    else:
        print("Sin diagnostico")