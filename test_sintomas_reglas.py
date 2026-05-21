import json
import unittest
from pathlib import Path


class SintomasReglasConsistencyTest(unittest.TestCase):
    def test_todas_las_condiciones_de_reglas_existen_en_sintomas(self):
        reglas = json.loads(Path('reglas.json').read_text(encoding='utf-8'))
        sintomas = set(json.loads(Path('sintomas.json').read_text(encoding='utf-8')))

        condiciones = {
            condicion
            for regla in reglas
            for condicion in regla.get('condiciones', [])
        }

        faltantes = sorted(condiciones - sintomas)

        self.assertEqual(faltantes, [])


if __name__ == '__main__':
    unittest.main()
