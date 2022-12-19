import os

import pandas as pd
from configuracion import *


class ProcesadorUsosFinales:
    def __init__(self, direccion_modelos: str):
        excel_modelos = pd.ExcelFile(direccion_modelos)
        self.df_configuracion_usos_finales = pd.read_excel(excel_modelos, sheet_name=NOMBRE_HOJA_USOS_FINALES,
                                                           usecols=['Item', 'Escenario', 'Subsector'])
        self.df_usos_finales = pd.DataFrame()

    def procesar_usos_finales(self, ruta_archivos_usos_finales: str, ruta_diccionarios: str):
        for _, row in self.df_configuracion_usos_finales.iterrows():
            item = row['Item']
            escenario = row['Escenario']
            subsector = row['Subsector']
            nombre_archivo = f'{item}_{escenario}.xlsx'
            ruta_archivo = os.sep.join([ruta_archivos_usos_finales, nombre_archivo])
            df_uso_final = pd.read_excel(ruta_archivo, sheet_name=NOMBRE_HOJA_ELECTRIFICACION)
            df_uso_final = df_uso_final[(df_uso_final['Año'] >= AGNO_INICIAL) & (df_uso_final['Año'] <= AGNO_FINAL)]

            dicc_comuna = pd.read_excel(ruta_diccionarios, sheet_name=f'Barra_Comuna', header=None)
            dicc_comuna.rename(columns={0: 'Barra', 1: 'Comuna'}, inplace=True)

            dicc_region = pd.read_excel(ruta_diccionarios, sheet_name=f'Barra_Region', header=None)
            dicc_region.rename(columns={0: 'Barra', 1: 'Región'}, inplace=True)

            df_uso_final = pd.merge(df_uso_final, dicc_comuna, on=['Barra'], how='left')
            df_uso_final = pd.merge(df_uso_final, dicc_region, on=['Barra'], how='left')
            df_uso_final.replace({'Mes': DICC_MESES}, inplace=True)
            df_uso_final['Sector Económico'] = subsector
            df_uso_final['Energético'] = 'Electricidad'
            df_uso_final['Origen'] = 'Modelo Usos Finales'
            df_uso_final['Tipo de Cliente'] = df_uso_final['Sector Económico']
            df_uso_final.replace({'Tipo de Cliente': DICC_TIPO}, inplace=True)
            self.df_usos_finales = pd.concat([self.df_usos_finales, df_uso_final], ignore_index=True)

    def agregar_proyeccion(self, data_proyeccion: pd.DataFrame):
        escenarios = list(data_proyeccion['Escenario'].unique())
        for escenario in escenarios:
            df_uso_escanario = self.df_usos_finales.copy()
            df_uso_escanario['Escenario'] = escenario
            data_proyeccion = pd.concat([data_proyeccion, df_uso_escanario], ignore_index=True)
        return data_proyeccion
