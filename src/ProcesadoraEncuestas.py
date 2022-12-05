import os

import numpy as np
import pandas as pd

from configuracion import *


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
            df_desagrupar_empresa = self.df_desagrupacion.loc[self.df_desagrupacion.Empresa == empresa]
            df_desagrupar_empresa.drop('Empresa', axis=1, inplace=True)
            self.proyeccion = self.proyeccion.merge(df_desagrupar_empresa, on=['Barra'], how='left')
            self.proyeccion['Participacion'] = self.proyeccion['Participacion'].fillna(0)
            # self.proyeccion.loc[(self.proyeccion['Sector Económico'] == sector) &
            #                     (self.proyeccion['Año'] >= AGNO_INICIAL), [ENERGIA]] = self.proyeccion[ENERGIA] * (
            #             1 - self.proyeccion['Participacion'])
            self.proyeccion[ENERGIA] = self.proyeccion.apply(lambda var: var[ENERGIA] * (1 - var['Participacion'])
            if (var['Sector Económico'] == sector) & (var['Año'] >= AGNO_INICIAL) else var[ENERGIA], axis=1)
            self.proyeccion.drop('Participacion', axis=1, inplace=True)

            print(empresa)

        # self.proyeccion.to_csv('test.csv')

    def agregar_dato_encuesta(self):
        for indice, fila in self.lista_empresas.iterrows():
            empresa = fila['Empresa']
            df_encuesta = pd.read_excel(self.excel_encuestas, sheet_name=empresa)
            df_encuesta = pd.melt(df_encuesta, id_vars=['Año', 'Mes'], var_name='Barra', value_name='Demanda Encuesta')
            df_encuesta.replace({'Mes': DICC_MESES}, inplace=True)

            self.proyeccion = pd.merge(self.proyeccion, df_encuesta, on=['Año', 'Mes', 'Barra'], how='left')
            # TODO procesar datos de barras que no existen

            print('test')
        self.proyeccion.to_csv('test.csv')


def main():
    ruta = os.sep.join(['..', 'input', 'Encuestas.xlsx'])
    procesador_encuestas = ProcesadoraEncuestas(ruta)
    print('end')


if __name__ == '__main__':
    main()
