import os

import numpy as np
import pandas as pd

from configuracion import *
import logging

logger = logging.getLogger('simple_example')


class ProcesadoraEncuestas:
    def __init__(self, direccion_encuestas: str):
        self.excel_encuestas = pd.ExcelFile(direccion_encuestas)
        self.lista_empresas = pd.read_excel(self.excel_encuestas, sheet_name='Lista')
        self.proyeccion = pd.DataFrame
        self.df_desagrupacion = pd.read_excel(self.excel_encuestas, sheet_name='Desagrupacion')

    def agregar_proyeccion(self, data_proyeccion: pd.DataFrame):
        self.proyeccion = data_proyeccion

    def eliminar_proyeccion_macroeconomica(self):
        for indice, fila in self.lista_empresas.iterrows():
            empresa = fila['Empresa']
            sector = fila['Sector']
            df_desagrupar_empresa = self.df_desagrupacion.loc[self.df_desagrupacion.Empresa == empresa].copy()
            df_desagrupar_empresa.drop('Empresa', axis=1, inplace=True)
            self.proyeccion = self.proyeccion.merge(df_desagrupar_empresa, on=['Barra'], how='left')
            self.proyeccion['Participacion'] = self.proyeccion['Participacion'].fillna(0)
            self.proyeccion[ENERGIA] = self.proyeccion.apply(lambda var: var[ENERGIA] * (1 - var['Participacion'])
            # TODO Revisar
            if (var['Sector Económico'] == sector) & (var['Año'] >= AGNO_INICIAL) else var[ENERGIA], axis=1)
            self.proyeccion.drop('Participacion', axis=1, inplace=True)

        # self.proyeccion.to_csv('test.csv')

    def agregar_dato_encuesta(self, ruta_guardado: str):
        archivo_guardado = os.sep.join([ruta_guardado, f'Proyeccion_Demanda.csv'])
        for indice, fila in self.lista_empresas.iterrows():
            empresa = fila['Empresa']
            sector = fila['Sector']
            logger.info(f'Agregando Encuesta de empresa {empresa}')
            df_encuesta = pd.read_excel(self.excel_encuestas, sheet_name=empresa)
            df_encuesta = pd.melt(df_encuesta, id_vars=['Año', 'Mes'], var_name='Barra', value_name='Demanda')
            df_encuesta.replace({'Mes': DICC_MESES}, inplace=True)
            barras_encuestas = list(df_encuesta['Barra'].unique())
            escenarios = list(self.proyeccion['Escenario'].unique())
            for barra_nueva in barras_encuestas:
                logger.info(f'Agregando Encuesta de empresa {empresa} para barra {barra_nueva}')
                df_barra = df_encuesta.loc[df_encuesta.Barra == barra_nueva].copy()
                try:
                    comuna = list(self.proyeccion.loc[self.proyeccion.Barra == barra_nueva, 'Comuna'].unique())[0]
                    region = list(self.proyeccion.loc[self.proyeccion.Barra == barra_nueva, 'Comuna'].unique())[0]
                except IndexError:
                    logger.warning(f'Barra {barra_nueva} no tiene datos historicos. Comuna y Region no identificados.')
                    comuna = np.nan
                    region = np.nan
                df_barra.loc[:, 'Sector Económico'] = sector
                df_barra.loc[:, 'Tipo de Cliente'] = DICC_TIPO[sector]
                df_barra.loc[:, 'Energético'] = 'Electricidad'
                df_barra.loc[:, 'Región'] = region
                df_barra.loc[:, 'Comuna'] = comuna
                df_barra.fillna(0, inplace=True)
                for escenario in escenarios:
                    df_barra['Escenario'] = escenario
                    self.proyeccion = pd.concat([self.proyeccion, df_barra])
        self.proyeccion.to_csv(archivo_guardado, encoding='utf-8-sig', index=False)


def main():
    ruta = os.sep.join(['..', 'input', 'Encuestas.xlsx'])
    procesador_encuestas = ProcesadoraEncuestas(ruta)
    print('end')


if __name__ == '__main__':
    main()
