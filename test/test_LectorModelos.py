import os

import pytest

from src.LectorModelosEconometricos import LectorModelosEconometricos


@pytest.fixture()
def modelos_test() -> LectorModelosEconometricos:
    procesador_modelos = LectorModelosEconometricos(os.sep.join(['test', 'test_inputs', 'Modelos_test.xlsx']))
    return procesador_modelos


def test_leer_escenarios_escogidos(modelos_test):
    resultados = {
        'ReguladosLD': 1,
        'Cobre': 1
    }

    diccionario_leido = modelos_test.entregar_modelos_escogidos()

    assert diccionario_leido == resultados
