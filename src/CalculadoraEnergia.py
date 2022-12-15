import os

import numpy as np
import pandas as pd

from configuracion import *
import logging

from src.LectorModelosEconometricos import LectorModelosEconometricos

logger = logging.getLogger('simple_example')


def hay_rezagos(df: pd.DataFrame)->bool:
    """
    Revisa si hay coeficientes de retardos en dataframe
    :param df: dataframe
    :return: bool si se cumple condicion
    """
    lista_columnas = list(df.columns)
    return any(item.startswith('Lag') for item in lista_columnas)


class CalculadoraEnergia:
    """
    Clase procesa los dataframes compilados y calcula la proyeccion de energia para cada subsector
    """

    def __init__(self, ruta_archivo_modelos: str, ruta_diccionarios: str):
        self.ruta_modelos = ruta_archivo_modelos
        self.df_proyecciones = None
        self.procesador_modelos = LectorModelosEconometricos(self.ruta_modelos, ruta_diccionarios)
        self.modelos_escogidos = self.procesador_modelos.entregar_modelos_escogidos()
        self.df_compilado = pd.DataFrame

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

    def calcular_proyeccion_energia(self, direccion_datos_historicos: str) -> None:
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

            if hay_rezagos(df_subsector):
                logger.info(f'Calculando demanda con rezagos para sector: {subsector}')
                df_subsector = self.adjuntar_datos_historicos_rezagos(direccion_datos_historicos, df_subsector,
                                                                      subsector)
                lista_rezagos = [int(item[-1]) for item in list(df_subsector.columns) if item.startswith('Lag')]
                for index, row in df_subsector.iterrows():
                    agno = row['Año']
                    if agno < AGNO_INICIAL:
                        continue
                    for rezago in lista_rezagos:
                        nombre_rezago = f'Lag_L{rezago}'
                        coef_rezago = row[nombre_rezago]
                        energia_retardo = df_subsector.loc[index - rezago, ENERGIA]
                        df_subsector.loc[index, ENERGIA] = df_subsector.loc[index, ENERGIA] + coef_rezago * np.log(
                            energia_retardo)
                    df_subsector.loc[index, ENERGIA] = np.exp(df_subsector.loc[index, ENERGIA])
                df_subsector.dropna(axis=0, inplace=True)
            else:
                # Exponencial para obtener energia en MWh
                """
    
                Energia = exp(ln(Energia))
                """
                df_subsector[ENERGIA] = np.exp(df_subsector[ENERGIA])
            df_subsector['Origen'] = 'Modelo Macroeconomico'
            self.df_proyecciones[subsector] = df_subsector

    def adjuntar_datos_historicos(self, direccion_datos_historicos: str) -> None:
        """
        Funcion que adjunta datos historicos a las proyecciones, manteniendo resolucion de proyeccion
        :param direccion_datos_historicos:
        """
        for subsector, df_subsector in self.df_proyecciones.items():
            df_historico_escenarios = pd.DataFrame()
            direccion_archivo = os.sep.join([direccion_datos_historicos, f'{subsector}.csv'])

            df_historico = pd.read_csv(direccion_archivo)
            lista_escenarios = self.df_proyecciones[subsector]['Escenario'].unique()
            for escenario in lista_escenarios:
                logger.info(f'Anexando datos historicos para el subsector {subsector}, escenario {escenario} '
                            f'desde {direccion_archivo}')
                df_historico['Escenario'] = escenario
                df_historico_escenarios = pd.concat([df_historico_escenarios, df_historico], ignore_index=True)
                df_historico_escenarios['Origen'] = 'Dato Historico'
            self.df_proyecciones[subsector] = pd.concat([df_historico_escenarios, df_subsector], ignore_index=True)
            self.df_proyecciones[subsector].dropna(axis=1, inplace=True)
            self.df_proyecciones[subsector]['Sector Económico'] = subsector
            self.df_proyecciones[subsector]['Energético'] = 'Electricidad'
            # self.df_proyecciones.sort_values(['Año', 'Mes'], ascending=[True, True], inplace=True)

    def adjuntar_datos_historicos_rezagos(self, direccion_datos_historicos: str,
                                          df_subsector: pd.DataFrame,
                                          subsector: str) -> pd.DataFrame:
        """
        Funcion que adjunta el ultimo año base para calculos de modelos con retardos
        :param subsector: nombre de subsector
        :param df_subsector: dataframe del subsector
        :param direccion_datos_historicos: ruta a datos historicos
        """
        df_historico_escenarios = pd.DataFrame()
        direccion_archivo = os.sep.join([direccion_datos_historicos, f'{subsector}.csv'])
        df_historico = pd.read_csv(direccion_archivo)
        df_historico = df_historico.loc[df_historico.Año == (AGNO_INICIAL - 1)]
        _, resolucion_modelo = self.procesador_modelos.obtener_resolucion_modelo(
            modelo=self.modelos_escogidos[subsector], subsector=subsector)
        if resolucion_modelo == 'Nacional':
            df_historico = df_historico.groupby(['Año', 'Mes']).sum()[ENERGIA].reset_index()
        lista_escenarios = df_subsector['Escenario'].unique()
        for escenario in lista_escenarios:
            logger.info(f'Anexando datos historicos para el subsector {subsector}, escenario {escenario} '
                        f'desde {direccion_archivo}')
            df_historico['Escenario'] = escenario
            df_historico_escenarios = pd.concat([df_historico_escenarios, df_historico], ignore_index=True)
        df_historico['Origen'] = 'Dato Historico'
        df_subsector = pd.concat([df_historico_escenarios, df_subsector], ignore_index=True)
        df_subsector['Sector Económico'] = subsector
        df_subsector['Energético'] = 'Electricidad'
        df_subsector.sort_values(['Año', 'Mes'], ascending=[True, True], inplace=True)
        return df_subsector

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
            elif resolucion_modelo == 'Nacional':
                logger.info(f'Desagrupando retiros del subsector {subsector} de {resolucion_modelo} a barras.')
                df_desagrupacion = pd.read_excel(self.ruta_modelos,
                                                 sheet_name=f'{PREFIJO_DESAGRUPACION}_{resolucion_modelo}',
                                                 usecols=['Barra', subsector])
                self.df_proyecciones[subsector] = self.df_proyecciones[subsector].join(df_desagrupacion, how='cross')
                self.df_proyecciones[subsector][ENERGIA] = self.df_proyecciones[subsector][ENERGIA] * \
                                                           self.df_proyecciones[subsector][subsector]
                self.df_proyecciones[subsector].drop(labels=[subsector], axis=1, inplace=True)

            else:
                logger.info(f'Desagrupando retiros del subsector {subsector} de {resolucion_modelo} a barras.')
                df_desagrupacion = pd.read_excel(self.ruta_modelos,
                                                 sheet_name=f'{PREFIJO_DESAGRUPACION}_{resolucion_modelo}',
                                                 usecols=[resolucion_modelo, 'Barra', subsector])
                self.df_proyecciones[subsector] = self.df_proyecciones[subsector].merge(df_desagrupacion,
                                                                                        on=[resolucion_modelo])
                self.df_proyecciones[subsector][ENERGIA] = self.df_proyecciones[subsector][ENERGIA] * \
                                                           self.df_proyecciones[subsector][subsector]
                self.df_proyecciones[subsector].drop(labels=[subsector], axis=1, inplace=True)

    def obtener_proyeccion_completa(self, direccion_datos_historicos: str) -> None:
        """
        Funcion para armar el archivo de proyeccion completo para cada subsector
        :param direccion_datos_historicos: ruta de datos historicos
        """

        self.calcular_proyeccion_energia(direccion_datos_historicos)
        self.desagrupar_retiros()
        self.adjuntar_datos_historicos(direccion_datos_historicos)

    @staticmethod
    def ajuste_historico_proyectado(df_compilado: pd.DataFrame) -> None:
        lista_subsectores = df_compilado['Sector Económico'].unique()
        lista_escenarios = df_compilado['Escenario'].unique()
        for subsector in lista_subsectores:
            lista_barras = df_compilado.loc[(df_compilado['Sector Económico'] == subsector), 'Barra'].unique()
            for barra in lista_barras:
                for escenario in lista_escenarios:
                    energia_historica = df_compilado.loc[(df_compilado['Sector Económico'] == subsector) &
                                                         (df_compilado['Escenario'] == escenario)
                                                         & (df_compilado['Barra'] == barra) &
                                                         (df_compilado['Año'] == (AGNO_INICIAL - 1)) &
                                                         (df_compilado['Mes'].isin((10, 11, 12)))][ENERGIA].sum()
                    energia_proyectada = df_compilado.loc[(df_compilado['Sector Económico'] == subsector) &
                                                          (df_compilado['Escenario'] == escenario)
                                                          & (df_compilado['Barra'] == barra) &
                                                          (df_compilado['Año'] == AGNO_INICIAL) &
                                                          (df_compilado['Mes'].isin((1, 2, 3)))][ENERGIA].sum()
                    if energia_proyectada == 0 or energia_historica == 0:
                        continue
                    tasa = energia_proyectada / energia_historica - 1
                    if tasa < -1 * TASA_MAXIMA:
                        logger.debug(f'Ajustando tasa de {barra} subsector {subsector} con tasa {tasa}')
                        multiplicador = energia_historica * (-1 * TASA_MAXIMA + 1) / energia_proyectada
                        df_compilado.loc[(df_compilado['Sector Económico'] == subsector) &
                                         (df_compilado['Escenario'] == escenario)
                                         & (df_compilado['Barra'] == barra) & (
                                                 df_compilado['Año'] >= AGNO_INICIAL), ENERGIA] *= multiplicador
                    elif tasa > TASA_MAXIMA:
                        logger.debug(f'Ajustando tasa de {barra} subsector {subsector} con tasa {tasa}')
                        multiplicador = energia_historica * (TASA_MAXIMA + 1) / energia_proyectada
                        df_compilado.loc[(df_compilado['Sector Económico'] == subsector) &
                                         (df_compilado['Escenario'] == escenario)
                                         & (df_compilado['Barra'] == barra) & (
                                                 df_compilado['Año'] >= AGNO_INICIAL), ENERGIA] *= multiplicador

    def guardar_proyecciones(self, ruta_guardado: str) -> None:
        """
        Metodo que guarda prediccion en archivos csv para cada subsector
        :param ruta_guardado: ruta donde guardar archivos
        """
        for subsector, df_subsector in self.df_proyecciones.items():
            archivo_guardado = os.sep.join([ruta_guardado, f'{subsector}_proyecciones.csv'])
            logger.info(f'Guardando proyeccion de subsector {subsector} en {archivo_guardado}')
            df_subsector.to_csv(archivo_guardado, encoding='utf-8-sig', index=False)

    def entregar_df_compilado(self):
        """
        Metodo que devuelve el dataframe compilado
        :return: dataframe compilado
        """
        return self.df_compilado

    def actualizar_proyeccion(self, df_actualizado: pd.DataFrame) -> None:
        """
        Actualiza el dataframe compilado
        :param df_actualizado: nuevo dataframe compilado
        """
        self.df_compilado = df_actualizado

    def compilar_proyecciones(self, ruta_diccionarios: str) -> None:
        """
        Metodo para armar dataframe con todas las proyecciones, incluyendo el ajuste con datos historicos.
        :param ruta_diccionarios: ruta donde se encuentra el diccionario para asignar comuna y region a cada barra.
        """
        df_compilado = pd.DataFrame()
        logger.info(f'Compilando proyecciones.')
        for subsector, df_subsector in self.df_proyecciones.items():
            df_compilado = pd.concat([df_compilado, df_subsector], ignore_index=True)
        dicc_comuna = pd.read_excel(ruta_diccionarios, sheet_name=f'Barra_Comuna', header=None)
        dicc_comuna.rename(columns={0: 'Barra', 1: 'Comuna'}, inplace=True)
        dicc_region = pd.read_excel(ruta_diccionarios, sheet_name=f'Barra_Region', header=None)
        dicc_region.rename(columns={0: 'Barra', 1: 'Región'}, inplace=True)
        df_compilado.drop(labels=['Comuna', 'Region'], axis=1, inplace=True, errors='ignore')
        df_compilado = df_compilado.astype({ENERGIA: 'float'})
        if AJUSTE:
            self.ajuste_historico_proyectado(df_compilado)
        df_compilado = pd.merge(df_compilado, dicc_comuna, on=['Barra'], how='left')
        df_compilado = pd.merge(df_compilado, dicc_region, on=['Barra'], how='left')
        df_compilado.replace({'Mes': DICC_MESES}, inplace=True)
        df_compilado['Tipo de Cliente'] = df_compilado['Sector Económico']
        df_compilado.replace({'Tipo de Cliente': DICC_TIPO}, inplace=True)
        df_compilado = df_compilado[df_compilado[ENERGIA] != 0].dropna()
        lista_columnas = list(df_compilado.columns)
        lista_columnas.remove(ENERGIA)
        df_compilado = df_compilado.groupby(lista_columnas).sum()[ENERGIA].reset_index()
        self.df_compilado = df_compilado

    def guardar_proyeccion_compilada(self, ruta_guardado: str) -> None:
        """
        Metodo para guardar el archivo compilado en un csv
        :param ruta_guardado: ruta donde se guarda el archivo
        """
        archivo_guardado = os.sep.join([ruta_guardado, f'Proyeccion_Demanda.csv'])
        logger.info(f'Guardando proyecciones en {archivo_guardado}')
        self.df_compilado.to_csv(archivo_guardado, encoding='utf-8-sig', index=False)

    def guardar_proyeccion_compilada_agrupada(self,
                                              ruta_guardado: str,
                                              ruta_diccionarios: str) -> None:
        """
        Metodo para guardar el archivo compilado en un csv
        :param ruta_diccionarios: ruta de diccionario
        :param ruta_guardado: ruta donde se guarda el archivo
        """
        for agrupacion in LISTA_AGRUPACION:
            dicc_agrupacion = pd.read_excel(ruta_diccionarios, sheet_name=f'Barra_{agrupacion}', header=None)
            dicc_agrupacion.rename(columns={0: 'Barra', 1: f'{agrupacion}'}, inplace=True)
            df_agrupado = pd.merge(self.df_compilado, dicc_agrupacion, on=['Barra'], how='left')
            df_agrupado.drop(['Barra'], inplace=True, axis=1)
            columnas = df_agrupado.columns
            columnas = set(columnas) - {f'{ENERGIA}'}
            df_agrupado = df_agrupado.groupby(list(columnas)).sum()[ENERGIA].reset_index()
            archivo_guardado = os.sep.join([ruta_guardado, f'Proyeccion_Demanda_{agrupacion}.csv'])
            logger.info(f'Guardando proyecciones agrupada en {archivo_guardado}')
            df_agrupado.to_csv(archivo_guardado, encoding='utf-8-sig', index=False)
