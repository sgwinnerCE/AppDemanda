import logging
import os

import pandas as pd

from configuracion import *

logger = logging.getLogger('simple_example')


class ProcesadorVariables:

    def __init__(self, direccion_archivos: str) -> None:
        self.direccion_archivos = direccion_archivos
        self.lista_escenarios = self.obtener_lista_escenarios()
        self.TIPO_VARIABLE = DICCIONARIO_TIPO_VARIABLE

    def obtener_lista_escenarios(self) -> list[str]:
        lista_escenarios = os.listdir(self.direccion_archivos)
        lista_escenarios = [archivo.split('.')[0] for archivo in lista_escenarios if archivo.endswith('.xlsx') and not
        archivo.startswith('~')]
        return lista_escenarios

    def procesar_variable(self, nombre_variable: str) -> pd.DataFrame:
        df_variable = pd.DataFrame()
        resolucion_variable = self.TIPO_VARIABLE[nombre_variable]
        if resolucion_variable == 'Nacional':
            for escenario in self.lista_escenarios:
                nombre_archivo = os.sep.join([self.direccion_archivos, f'{escenario}.xlsx'])
                df_variable_escenario = pd.read_excel(nombre_archivo, sheet_name=NOMBRE_HOJA_VARIABLES_NACIONALES)
                df_variable_escenario = df_variable_escenario[['Año', 'Mes', nombre_variable]]
                df_variable_escenario['Escenario'] = escenario
                df_variable = pd.concat([df_variable, df_variable_escenario], ignore_index=True)
        else:
            for escenario in self.lista_escenarios:
                nombre_archivo = os.sep.join([self.direccion_archivos, f'{escenario}.xlsx'])
                df_variable_escenario = pd.read_excel(nombre_archivo, sheet_name=nombre_variable)
                df_variable_escenario = pd.melt(df_variable_escenario,
                                                id_vars=['Año', 'Mes'],
                                                var_name=resolucion_variable,
                                                value_name=nombre_variable)
                df_variable_escenario['Escenario'] = escenario
                df_variable = pd.concat([df_variable, df_variable_escenario], ignore_index=True)
        return df_variable


def main():
    ruta = os.sep.join(['..', 'test', 'test_inputs', 'Escenarios'])
    procesador_variables = ProcesadorVariables(ruta)
    escenarios = procesador_variables.obtener_lista_escenarios()
    df_variable = procesador_variables.procesar_variable('Poblacion')
    print('end')


if __name__ == '__main__':
    main()
