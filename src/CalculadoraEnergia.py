import os

import numpy as np
import pandas as pd

from configuracion import *
import logging

from src.LectorModelosEconometricos import LectorModelosEconometricos

logger = logging.getLogger('simple_example')


class CalculadoraEnergia:
    """
    Clase procesa los dataframes compilados y calcula la proyeccion de energia para cada subsector
    """

    def __init__(self, ruta_archivo_modelos=str):
        self.ruta_modelos = ruta_archivo_modelos
        self.df_proyecciones = None
        self.procesador_modelos = LectorModelosEconometricos(self.ruta_modelos)
        self.modelos_escogidos = self.procesador_modelos.entregar_modelos_escogidos()

    def leer_df_compilados(self, df_compilados: dict) -> None:
        """
        Lee los dataframes compilados para cada subsector
        :param df_compilados:
        """
        if self.df_proyecciones is None:
            self.df_proyecciones = df_compilados
        else:
            pass

    @staticmethod
    def _obtener_variables(df_subsector: pd.DataFrame, prefijo: str) -> list:
        """
        Obtiene lista de variables de acuerdo al prefijo utilizado para identificarlas
        :param df_subsector: dataframe compilado del subsector
        :param prefijo: prefijo utilizado. Por ejemplo Coef_ para elasticidades de variables o Coef2_ cuando hay que
        elevar al cuadrado el logaritmo
        :return:lista de variables
        """
        lista_variables = list(df_subsector.columns)
        result = [i[len(prefijo):] for i in lista_variables if i.startswith(prefijo)]
        return result

    def calcular_proyeccion_energia(self) -> None:
        """
        Funcion que calcula los retiros de energia agregandola como columna al dataframe
        """
        for subsector, df_subsector in self.df_proyecciones.items():
            logger.info(f'Calculando retiros proyectados para el {subsector}')
            df_subsector[ENERGIA] = 0
            df_subsector[ENERGIA].drop_duplicates(inplace=True)
            # Calculo con elasticidades de variables explicativas
            variables = self._obtener_variables(df_subsector, 'Coef_')
            for variable in variables:
                """
                Energia = Energia + Suma(Coef * LN(Variable))
                """
                df_subsector[ENERGIA] = df_subsector[ENERGIA] + df_subsector[f'Coef_{variable}'] * np.log(
                    df_subsector[variable])
            # Calculo con elasticidades de variables explicativas al cuadrado
            variables = self._obtener_variables(df_subsector, 'Coef2_')
            for variable in variables:
                """
                Energia = Energia + Suma(Coef * LN(Variable)^2)
                """

                df_subsector[ENERGIA] = df_subsector[ENERGIA] + df_subsector[
                    f'Coef2_{variable}'] * np.log(df_subsector[variable]) ** 2
            # Suma Efecto Fijo
            """
            Efectos fijos ya tienen sumada la constante global
            Energia = Energia + Efecto_Fijo 
            """
            df_subsector[ENERGIA] = df_subsector[ENERGIA] + df_subsector['Efecto_Fijo']
            # Exponencial para obtener energia en MWh
            """
            
            Energia = exp(ln(Energia))
            """
            df_subsector[ENERGIA] = np.exp(df_subsector[ENERGIA])

    def adjuntar_datos_historicos(self, direccion_datos_historicos: str) -> None:
        """
        Funcion que adjunta datos historicos a las proyecciones, manteniendo resolucion de proyeccion
        :param direccion_datos_historicos:
        """
        df_historico_escenarios = pd.DataFrame()
        for subsector, df_subsector in self.df_proyecciones.items():
            direccion_archivo = os.sep.join([direccion_datos_historicos, f'{subsector}.csv'])
            logger.info(f'Anexando datos historicos para el subsector {subsector} desde {direccion_archivo}')
            df_historico = pd.read_csv(direccion_archivo)
            lista_escenarios = self.df_proyecciones[subsector]['Escenario'].unique()
            for escenario in lista_escenarios:
                df_historico['Escenario'] = escenario
                # if df_historico_escenarios.empty:
                #     df_historico_escenarios = df_historico
                # else:
                df_historico_escenarios = pd.concat([df_historico_escenarios, df_historico], ignore_index=True)
            self.df_proyecciones[subsector] = pd.concat([df_historico_escenarios, df_subsector], ignore_index=True)
            self.df_proyecciones[subsector].dropna(axis=1, inplace=True)

    def desagrupar_retiros(self):
        """
        Metodo que desagrupa demanda agrupada en la proyeccion. Por ejemplo para pasar de Empresa/Faena a barras de
        retiro
        """
        for subsector, df_subsector in self.df_proyecciones.items():
            _, resolucion_modelo = self.procesador_modelos.obtener_resolucion_modelo(
                modelo=self.modelos_escogidos[subsector], subsector=subsector)

            if resolucion_modelo == 'Barra':
                continue
            else:
                logger.info(f'Desagrupando retiros del subsector {subsector} de {resolucion_modelo} a barras.')
                df_desagrupacion = pd.read_excel(self.ruta_modelos, sheet_name=f'{PREFIJO_DESAGRUPACION}_{resolucion_modelo}',
                                                 usecols=[resolucion_modelo, 'Barra', subsector])
                self.df_proyecciones[subsector] = self.df_proyecciones[subsector].merge(df_desagrupacion, on=[resolucion_modelo])
                self.df_proyecciones[subsector]['Demanda'] = self.df_proyecciones[subsector]['Demanda']*self.df_proyecciones[subsector][subsector]
                self.df_proyecciones[subsector].drop(labels=[subsector], axis=1, inplace=True)


    def obtener_proyeccion_completa(self, direccion_datos_historicos):
        self.calcular_proyeccion_energia()
        self.desagrupar_retiros()
        self.adjuntar_datos_historicos(direccion_datos_historicos)

    def guardar_proyecciones(self, ruta_guardado):
        for subsector, df_subsector in self.df_proyecciones.items():
            archivo_guardado = os.sep.join([ruta_guardado, f'{subsector}_proyecciones.csv'])
            logger.info(f'Guardando proyeccion de subsector {subsector} en {archivo_guardado}')
            df_subsector.to_csv(archivo_guardado, encoding='latin-1', index=False)

    def guardar_proyeccion_compilada(self, ruta_guardado):
        for subsector, df_subsector in self.df_proyecciones.items():
            archivo_guardado = os.sep.join([ruta_guardado, f'{subsector}_proyecciones.csv'])
            logger.info(f'Guardando proyeccion de subsector {subsector} en {archivo_guardado}')
            df_subsector.to_csv(archivo_guardado, encoding='latin-1', index=False)
            print('test')
