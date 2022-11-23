import os

import pandas as pd
import pytest

from src.LectorModelosEconometricos import LectorModelosEconometricos
from pandas.testing import assert_frame_equal


@pytest.fixture()
def modelos_test() -> LectorModelosEconometricos:
    procesador_modelos = LectorModelosEconometricos(os.sep.join(['test', 'test_inputs', 'Modelos_test.xlsx']),
                                                    os.sep.join(['test', 'test_inputs', 'Diccionarios.xlsx']))
    procesador_modelos.agno_i = 2022
    procesador_modelos.agno_f = 2023
    return procesador_modelos


def test_leer_escenarios_escogidos(modelos_test):
    resultados = {
        'ReguladosLD': 1,
        'Cobre': 1
    }

    diccionario_leido = modelos_test.entregar_modelos_escogidos()

    assert diccionario_leido == resultados


def test_lista_agnos(modelos_test):
    assert [2022, 2023] == modelos_test._armar_lista_agnos_proyeccion()


def test_lista_meses(modelos_test):
    assert [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12] == modelos_test._armar_lista_meses_proyeccion()


def test_armar_df_temporal(modelos_test):
    objetivo = pd.read_csv(os.sep.join(['test', 'test_inputs', 'test_df_temporal.csv']))
    assert assert_frame_equal(objetivo, modelos_test._armar_df_temporal()) is None


def test_resolucion_modelo_1(modelos_test):
    obj_coef = 'Nacional'
    obj_ef = 'Barra'
    test_coef, test_ef = modelos_test.obtener_resolucion_modelo(1, 'ReguladosLD')
    assert obj_coef == test_coef and test_ef == obj_ef


def test_resolucion_modelo_3(modelos_test):
    obj_coef = 'Region'
    obj_ef = 'Barra'
    test_coef, test_ef = modelos_test.obtener_resolucion_modelo(3, 'ReguladosLD')
    assert obj_coef == test_coef and test_ef == obj_ef


def test_efecto_fijo_modelo_1(modelos_test):
    df_obj = pd.DataFrame(data={'Barra': ['Barra1', 'Barra2'], 'Efecto_Fijo': [4.5, 6]})
    assert assert_frame_equal(df_obj, modelos_test._obtener_efectos_fijos(1, 'ReguladosLD', 'Barra')) is None


def test_coeficientes_modelo_1(modelos_test):
    df_obj = {'IMACEC': 0.65, 'Precio': -0.4, 'Poblacion': 0.21}
    assert df_obj == modelos_test._obtener_coeficientes(1, 'ReguladosLD')


def test_coeficientes_modelo_2(modelos_test):
    df_obj = {'Produccion': 0.6}
    assert df_obj == modelos_test._obtener_coeficientes(1, 'Cobre')


def test_coeficientes_cuadrado_modelo_1(modelos_test):
    df_obj = {'IMACEC': 0.1}
    assert df_obj == modelos_test._obtener_coeficientes_cuadrado(1, 'ReguladosLD')


def test_coeficientes_cuadrado_modelo_2(modelos_test):
    with pytest.raises(ValueError):
        modelos_test._obtener_coeficientes_cuadrado(1, 'Cobre')

# def test_armado_proyeccion_1(modelos_test):
#     dataframe = pd.read_csv(os.sep.join(['test', 'test_inputs', 'output_reguladosLD.csv']))
#     dataframe_leido = modelos_test.armar_df_proyecciones()[0]
#     assert assert_frame_equal(dataframe, dataframe_leido) is None
