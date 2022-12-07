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

    def agregar_dato_encuesta(self, ruta_guardado: str):
        archivo_guardado = os.sep.join([ruta_guardado, f'Proyeccion_Demanda.csv'])
        for indice, fila in self.lista_empresas.iterrows():
            empresa = fila['Empresa']
            sector = fila['Sector']
            df_encuesta = pd.read_excel(self.excel_encuestas, sheet_name=empresa)
            df_encuesta = pd.melt(df_encuesta, id_vars=['Año', 'Mes'], var_name='Barra', value_name='Demanda Encuesta')
            df_encuesta.replace({'Mes': DICC_MESES}, inplace=True)
            barras_encuestas = list(df_encuesta['Barra'].unique())
            barras_bbdd = list(self.proyeccion['Barra'].unique())
            barras_nuevas = set(barras_encuestas) - set(barras_bbdd)
            escenarios = list(self.proyeccion['Escenario'].unique())
            self.proyeccion = pd.merge(self.proyeccion, df_encuesta, on=['Año', 'Mes', 'Barra'], how='left')
            self.proyeccion.fillna(0, inplace=True)
            self.proyeccion[ENERGIA] = self.proyeccion[ENERGIA] + self.proyeccion['Demanda Encuesta']
            self.proyeccion.drop(['Demanda Encuesta'], axis=1, inplace=True)
            for barra_nueva in barras_nuevas:
                df_barra = df_encuesta.loc[df_encuesta.Barra == barra_nueva]
                df_barra = df_barra.rename(columns={'Demanda Encuesta': ENERGIA})
                df_barra['Sector Económico'] = sector
                df_barra['Tipo de Cliente'] = DICC_TIPO[sector]
                df_barra['Energético'] = 'Electricidad'
                df_barra.fillna(0, inplace=True)
                for escenario in escenarios:
                    df_barra['Escenario'] = escenario
                    self.proyeccion = pd.concat([self.proyeccion, df_barra])
                    print('test')



            # TODO procesar datos de barras que no existen
        self.proyeccion.to_csv(archivo_guardado, encoding='utf-8-sig', index=False)


def main():
    ruta = os.sep.join(['..', 'input', 'Encuestas.xlsx'])
    procesador_encuestas = ProcesadoraEncuestas(ruta)
    print('end')


if __name__ == '__main__':
    main()
