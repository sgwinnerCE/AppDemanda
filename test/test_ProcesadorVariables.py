import os

import pytest

from src.ProcesadorVariables import ProcesadorVariables


@pytest.fixture()
def variables_test() -> ProcesadorVariables:
    procesador_variables = ProcesadorVariables(os.sep.join(['test', 'test_inputs', 'Escenarios']))
    return procesador_variables


def test_leer_escenarios(variables_test):
    resultados = ['Escenario_test1',
                  'Escenario_test2']

    lista_leida = variables_test.obtener_lista_escenarios()

    assert lista_leida == resultados
