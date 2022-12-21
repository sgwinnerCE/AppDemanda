import os

import numpy as np
import pandas as pd

from configuracion import *
import logging

from src.ProcesadorVariables import ProcesadorVariables

logger = logging.getLogger('simple_example')


class ModelosIntensidad:

    def __init__(self,
                 ruta_archivo_modelos: str,
                 ruta_escenarios: str,
                 direccion_datos_historicos: str,
                 ruta_diccionarios: str):
        self.datos_modelos_intensidad = pd.read_excel(ruta_archivo_modelos, sheet_name=NOMBRE_HOJA_MODELOS_INTENSIDAD,
                                                      usecols=['Subsector', 'Intensidad', 'Variable'])
        excel_diccionarios = pd.ExcelFile(ruta_diccionarios)
        self.procesador_variables = ProcesadorVariables(ruta_escenarios)
        self.direccion_datos_historicos = direccion_datos_historicos
        self.lista_escenarios = self.procesador_variables.obtener_lista_escenarios()
        self.dicc_comuna = pd.read_excel(excel_diccionarios, sheet_name=f'Barra_Comuna', header=None)
        self.dicc_comuna.rename(columns={0: 'Barra', 1: 'Comuna'}, inplace=True)

        self.dicc_region = pd.read_excel(excel_diccionarios, sheet_name=f'Barra_Region', header=None)
        self.dicc_region.rename(columns={0: 'Barra', 1: 'Región'}, inplace=True)
        self.df_proyecciones_modelo_intensidad = pd.DataFrame()

    def calcular_proyecciones(self):
        for _, fila in self.datos_modelos_intensidad.iterrows():
            subsector = fila['Subsector']
            intensidad = fila['Intensidad']
            variable = fila['Variable']
            logger.info(f'Proyectando subsector {subsector} utilizando modelo de intensidad.')

            ruta_dato_historico = os.sep.join([self.direccion_datos_historicos, f'{subsector}.csv'])
            df_historico = pd.read_csv(ruta_dato_historico)
            df_desagrupacion = df_historico.loc[(df_historico['Año'] == AGNO_INICIAL-1) & (df_historico['Mes'] == 12)].copy()
            df_desagrupacion['Desagrupacion'] = df_desagrupacion[ENERGIA]/df_desagrupacion[ENERGIA].sum()
            df_desagrupacion.drop(labels=['Año', 'Mes', ENERGIA], axis=1, inplace=True)

            df_historico_escenarios = pd.DataFrame()
            for escenario in self.lista_escenarios:
                df_historico['Escenario'] = escenario
                df_historico_escenarios = pd.concat([df_historico_escenarios, df_historico], ignore_index=True)
            df_historico_escenarios['Origen'] = 'Dato Historico'

            df_subsector = self.procesador_variables.procesar_variable(variable)
            df_subsector[ENERGIA] = intensidad * df_subsector[f'{variable}']
            df_subsector = df_subsector.join(df_desagrupacion, how='cross')
            df_subsector[ENERGIA] = df_subsector[ENERGIA]*df_subsector['Desagrupacion']
            df_subsector.drop(labels=['Desagrupacion', variable], axis=1, inplace=True)

            df_subsector['Origen'] = 'Modelo Intensidad'
            df_subsector = pd.concat([df_historico_escenarios, df_subsector])

            df_subsector['Sector Económico'] = subsector
            df_subsector['Tipo de Cliente'] = DICC_TIPO[subsector]
            df_subsector['Energético'] = 'Electricidad'

            self.df_proyecciones_modelo_intensidad = pd.concat([self.df_proyecciones_modelo_intensidad, df_subsector])
        self.df_proyecciones_modelo_intensidad = pd.merge(self.df_proyecciones_modelo_intensidad, self.dicc_comuna, on='Barra')
        self.df_proyecciones_modelo_intensidad = pd.merge(self.df_proyecciones_modelo_intensidad, self.dicc_region, on='Barra')
        self.df_proyecciones_modelo_intensidad.replace({'Mes': DICC_MESES}, inplace=True)

    def agregar_proyeccion_modelo_intensidad(self, df_completo: pd.DataFrame) -> pd.DataFrame:
        df_completo = pd.concat([df_completo, self.df_proyecciones_modelo_intensidad])
        return df_completo
