# AUTOEXPERT IA

Sistema experto automotriz desarrollado en Python.

## Caracteristicas

- Sistema basado en reglas
- Motor de inferencia
- Explicacion del diagnostico
- Prioridades
- Reglas JSON
- Programacion logica

## Ejecucion

python main.py

## Interfaz desktop (Tkinter)

La opcion desktop permite seleccionar sintomas por categoria y ejecutar diagnostico con un boton.

### Como ejecutar

Tkinter viene incluido con Python estandar, por lo que no hay dependencias extra para la interfaz.

```bash
python app_desktop.py
```

### Flujo de diagnostico

1. Selecciona una categoria (arranque, motor, combustible, frenos, temperatura, sensores, transmision, direccion, suspension y otros).
2. Marca sintomas en el checklist.
3. Presiona **Diagnosticar**.
4. Se muestran resultados ordenados por score (top N configurable).

### Calculo de coincidencia

Para cada regla:

- `match_ratio = condiciones_matched / total_condiciones`
- `score = (match_ratio * 100) + prioridad`
- Se filtran reglas con `match_ratio >= 0.5` (ajustable en la UI)

En los resultados se muestran:

- `diagnostico`
- `match/score`
- `prioridad`
- `prueba`
- `solucion`
- `condiciones_matched` y `condiciones_missing`