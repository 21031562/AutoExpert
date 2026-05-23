import json
import tempfile
import unittest
from pathlib import Path

from diagnostico import diagnosticar


class DiagnosticoTest(unittest.TestCase):
    def _escribir_json(self, ruta, contenido):
        Path(ruta).write_text(
            json.dumps(contenido, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def test_devuelve_resultados_ordenados(self):
        with tempfile.TemporaryDirectory() as directorio:
            sintomas_path = Path(directorio) / "sintomas.json"
            reglas_path = Path(directorio) / "reglas.json"

            self._escribir_json(
                sintomas_path,
                ["no_enciende", "tablero_debil", "click_al_girar_llave", "humo_negro"],
            )
            self._escribir_json(
                reglas_path,
                [
                    {
                        "id": "R1",
                        "modulo": "arranque",
                        "condiciones": ["no_enciende", "tablero_debil"],
                        "diagnostico": "bateria_descargada",
                        "prueba": "medir_bateria",
                        "solucion": "cargar_bateria",
                        "prioridad": 10,
                    },
                    {
                        "id": "R2",
                        "modulo": "motor",
                        "condiciones": ["humo_negro", "no_enciende"],
                        "diagnostico": "mezcla_rica",
                        "prueba": "revisar_inyectores",
                        "solucion": "limpiar_inyectores",
                        "prioridad": 5,
                    },
                ],
            )

            resultados = diagnosticar(
                sintomas_usuario=["no_enciende", "tablero_debil"],
                reglas_path=reglas_path,
                sintomas_path=sintomas_path,
                min_match=0.5,
                top_n=10,
            )

            self.assertEqual(resultados[0]["diagnostico"], "bateria_descargada")
            self.assertGreaterEqual(resultados[0]["score"], resultados[1]["score"])

    def test_error_claro_si_faltan_archivos(self):
        with tempfile.TemporaryDirectory() as directorio:
            sintomas_path = Path(directorio) / "sintomas.json"
            self._escribir_json(sintomas_path, ["no_enciende"])

            with self.assertRaisesRegex(
                FileNotFoundError,
                "No se encontro el archivo de reglas",
            ):
                diagnosticar(
                    sintomas_usuario=["no_enciende"],
                    reglas_path=Path(directorio) / "reglas_inexistentes.json",
                    sintomas_path=sintomas_path,
                )

    def test_error_claro_si_reglas_esta_vacio(self):
        with tempfile.TemporaryDirectory() as directorio:
            sintomas_path = Path(directorio) / "sintomas.json"
            reglas_path = Path(directorio) / "reglas.json"

            self._escribir_json(sintomas_path, ["no_enciende"])
            self._escribir_json(reglas_path, [])

            with self.assertRaisesRegex(
                ValueError,
                "No se encontraron reglas en el archivo de reglas",
            ):
                diagnosticar(
                    sintomas_usuario=["no_enciende"],
                    reglas_path=reglas_path,
                    sintomas_path=sintomas_path,
                )


if __name__ == "__main__":
    unittest.main()
