import logging
import os

import pandas as pd

from configuracion import *
from src.LectorModelosEconometricos import LectorModelosEconometricos
from src.ProcesadorVariables import ProcesadorVariables

logger = logging.getLogger('simple_example')


class CompiladorEscenarios:
    """
    Clase que lee y procesa las variables exogenas a usar por los modelos econometricos
    """

    def __init__(self, ruta_archivo_modelos: str, ruta_escenarios: str, ruta_diccionarios: str) -> None:
        self.procesador_modelos = LectorModelosEconometricos(ruta_archivo_modelos, ruta_diccionarios)
        self.modelos_escogidos = self.procesador_modelos.entregar_modelos_escogidos()
        self.df_coeficientes = self.procesador_modelos.armar_df_proyecciones()
        self.procesador_variables = ProcesadorVariables(ruta_escenarios)
        self.TIPO_VARIABLE = DICCIONARIO_TIPO_VARIABLE
        self.excel_diccionarios = pd.ExcelFile(ruta_diccionarios)
        self.df_compilados = dict()

    def leer_diccionario(self, resolucion_1: str, resolucion_2: str) -> pd.DataFrame:
        """
        Funcion que lee los diccionarios para cambiar la variable de resolucion
        :param resolucion_1: nombre de resolucion 1, por ejemplo Barra. Para pasar de Barra a Comuna
        :param resolucion_2: nombre de resolucion 2 por ejemplo Comuna. Para pasar de Barra a Comuna
        :return: Dataframe con diccionario con las asignaciones respectivas
        """
        dicc = pd.read_excel(self.excel_diccionarios, sheet_name=f'{resolucion_1}_{resolucion_2}', header=None)
        dicc.rename(columns={0: resolucion_1, 1: resolucion_2}, inplace=True)
        # dicc = dicc.set_index(0).to_dict()[1]
        return dicc

    def agregar_variables(self) -> None:
        """
        Funcion que agrega las variables al dataframe que contiene los coeficientes del modelo
        """
        for subsector, df_subsector in self.df_coeficientes.items():
            _, resolucion_modelo = self.procesador_modelos.obtener_resolucion_modelo(
                modelo=self.modelos_escogidos[subsector], subsector=subsector)
            for columna in df_subsector.columns:
                if columna.startswith('Coef') or columna.startswith('Coef'):
                    variable = columna.split('_', 1)[-1]
                    if variable in df_subsector.columns:
                        continue

                    df_variable = self.procesador_variables.procesar_variable(variable)
                    resolucion_variable = self.TIPO_VARIABLE[variable]
                    logger.info(f'Agregando variable {variable} con resolucion {resolucion_variable} a subsector {subsector}')

                    if resolucion_variable == 'Nacional':
                        if 'Escenario' not in df_subsector.columns:
                            df_subsector = pd.merge(df_subsector, df_variable, on=['A??o', 'Mes'])
                        else:
                            df_subsector = pd.merge(df_subsector, df_variable, on=['A??o', 'Mes', 'Escenario'])
                    else:
                        if resolucion_variable != resolucion_modelo:
                            diccionario = self.leer_diccionario(resolucion_modelo, resolucion_variable)
                            self.chequear_existencia_diccionario(diccionario, df_subsector, resolucion_modelo, resolucion_variable)
                            if resolucion_variable not in df_subsector.columns:
                                df_subsector = pd.merge(df_subsector, diccionario, on=[resolucion_modelo])
                            else:
                                df_subsector = pd.merge(df_subsector, diccionario, on=[resolucion_modelo, resolucion_variable])
                        if 'Escenario' not in df_subsector.columns:
                            df_subsector = pd.merge(df_subsector, df_variable, on=['A??o', 'Mes', resolucion_variable])
                        else:
                            df_subsector = pd.merge(df_subsector, df_variable,
                                                    on=['A??o', 'Mes', 'Escenario', resolucion_variable])
            self.df_compilados[subsector] = df_subsector

    def entregar_df_compilados(self) -> dict:
        """
        Funcion que entrega diccionario con el dataframe compilado respectivo para cada subsector
        :return: Diccionario de dataframes
        """
        return self.df_compilados

    @staticmethod
    def chequear_existencia_diccionario(diccionario: pd.DataFrame,
                                        df_subsector: pd.DataFrame, resolucion_modelo: str,
                                        resolucion_variable: str) -> None:
        """
        Metodo que revisa si falta alguna barra en el diccionario. Entrega un WARNING si es el caso
        :param diccionario:
        :param df_subsector:
        :param resolucion_modelo:
        :param resolucion_variable:
        """
        lista_subsector = list(df_subsector[resolucion_modelo].unique())
        lista_diccionario = list(diccionario[resolucion_modelo].unique())
        for elemento in lista_subsector:
            if elemento not in lista_diccionario:
                logger.warning(f'No se encuentra {resolucion_modelo} {elemento} en diccionario {resolucion_modelo}_{resolucion_variable}')

    def guardar_df(self, ruta_guardado: str):
        """
        Metodo que guarda los dataframes comp??lados para cada subsector. Con el subsector como nombre del archivo
        en formato csv
        :param ruta_guardado: ruta donde guardar los csv
        """
        for subsector, df_subsector in self.df_compilados.items():
            archivo_guardado = os.sep.join([ruta_guardado, f'{subsector}_parametros.csv'])
            df_subsector.to_csv(archivo_guardado, encoding='latin-1', index=False)
            logger.info(f'Guardando compilado de parametros en {archivo_guardado}')


def main():
    ruta_archivo_modelos = os.sep.join(['..', 'test', 'test_inputs', 'Modelos_test.xlsx'])
    ruta_archivo_diccionarios = os.sep.join(['..', 'test', 'test_inputs', 'Diccionarios.xlsx'])
    ruta_archivo_escenarios = os.sep.join(['..', 'test', 'test_inputs', 'Escenarios'])
    compilador = CompiladorEscenarios(ruta_archivo_modelos, ruta_archivo_escenarios, ruta_archivo_diccionarios)
    compilador.agregar_variables()
    print('end')


if __name__ == '__main__':
    main()
