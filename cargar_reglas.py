import json

def cargar_reglas():

    with open("reglas.json", "r", encoding="utf-8") as archivo:
        reglas = json.load(archivo)

    return reglas


def cargar_sintomas():

    with open("sintomas.json", "r", encoding="utf-8") as archivo:
        sintomas = json.load(archivo)

    return sintomas