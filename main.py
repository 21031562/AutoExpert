from interfaz import obtener_sintomas
from motor_inferencia import diagnosticar
from explicacion import mostrar_resultado
from utils import limpiar_pantalla


def menu():

    while True:

        print("\n==============================")
        print("       AUTOEXPERT IA")
        print("==============================")
        print("1. Diagnosticar vehiculo")
        print("2. Salir")

        opcion = input("\nSeleccione una opcion: ")

        if opcion == "1":

            limpiar_pantalla()

            sintomas = obtener_sintomas()

            resultados = diagnosticar(sintomas)

            if resultados:

                mejor = resultados[0]

                mostrar_resultado(mejor)

            else:
                print("\nNo se encontro diagnostico.")

        elif opcion == "2":

            print("\nSaliendo del sistema...")
            break

        else:
            print("\nOpcion invalida")


menu()