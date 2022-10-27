import os

import numpy as np
import pandas as pd

from configuracion import *
import logging

logger = logging.getLogger('simple_example')


class CalculadoraEnergia:
    def __init__(self):
        self.df_proyecciones = None

    def leer_df_compilados(self, df_compilados: dict):
        if self.df_proyecciones is None:
            self.df_proyecciones = df_compilados
        else:
            pass

    @staticmethod
    def _obtener_variables(df_subsector, prefijo):
        lista_variables = list(df_subsector.columns)
        result = [i[len(prefijo):] for i in lista_variables if i.startswith(prefijo)]
        return result

    def calcular_proyeccion_energia(self):
        for subsector, df_subsector in self.df_proyecciones.items():
            df_subsector[ENERGIA] = 0
            df_subsector[ENERGIA].drop_duplicates(inplace=True)
            # Calculo con elasticidades de variables explicativas
            variables = self._obtener_variables(df_subsector, 'Coef_')
            for variable in variables:
                df_subsector[ENERGIA] = df_subsector[ENERGIA] + df_subsector[f'Coef_{variable}'] * np.log(
                    df_subsector[variable])
            # Calculo con elasticidades de variables explicativas al cuadrado
            variables = self._obtener_variables(df_subsector, 'Coef2_')
            for variable in variables:
                df_subsector[ENERGIA] = df_subsector[ENERGIA] + df_subsector[
                    f'Coef2_{variable}'] * np.log(df_subsector[variable]) * np.log(df_subsector[variable])
            # Suma Efecto Fijo
            df_subsector[ENERGIA] = df_subsector[ENERGIA] + df_subsector['Efecto_Fijo']
            # Exponencial para obtener energia en MWh
            df_subsector[ENERGIA] = np.exp(df_subsector[ENERGIA])
            print('test')

    def adjuntar_datos_historicos(self, direccion_datos_historicos):
        for subsector, df_subsector in self.df_proyecciones.items():
            df_historico = pd.read_csv(os.sep.join([direccion_datos_historicos, f'{subsector}.csv']))
            self.df_proyecciones[subsector] = pd.concat([df_historico, df_subsector], ignore_index=True)
            self.df_proyecciones[subsector].dropna(axis=1, inplace=True)

            print('test')

    def obtener_proyeccion_completa(self, direccion_datos_historicos):
        self.calcular_proyeccion_energia()
        self.adjuntar_datos_historicos(direccion_datos_historicos)

    def guardar_proyecciones(self, ruta_guardado):
        for subsector, df_subsector in self.df_proyecciones.items():
            archivo_guardado = os.sep.join([ruta_guardado, f'{subsector}_proyecciones.csv'])
            df_subsector.to_csv(archivo_guardado, encoding='latin-1', index=False)
            logger.info(f'Guardando compilado de parametros en {archivo_guardado}')
