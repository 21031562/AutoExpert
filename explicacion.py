def mostrar_resultado(resultado):

    print("\n==============================")
    print("DIAGNOSTICO ENCONTRADO")
    print("==============================")

    print(f"\nID Regla: {resultado['id']}")

    print(f"\nModulo: {resultado['modulo']}")

    print(f"\nDiagnostico:")
    print(f"  {resultado['diagnostico']}")

    print(f"\nPrueba Recomendada:")
    print(f"  {resultado['prueba']}")

    print(f"\nSolucion Recomendada:")
    print(f"  {resultado['solucion']}")

    print(f"\nPrioridad:")
    print(f"  {resultado['prioridad']}")

    print("\nCondiciones detectadas:")

    for condicion in resultado["condiciones"]:
        print(f"  - {condicion}")