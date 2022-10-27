import logging
import os

import pandas as pd

from configuracion import *

logger = logging.getLogger('simple_example')


class LectorModelosEconometricos:
    """
    Clase que se encarga de leer el excel con los datos de los modelos econometricos y construye un dataframe para cada
    subsector que sera utilizado para realizar los calculos.
    """

    def __init__(self, direccion_archivo: str) -> None:
        self.archivo_excel = pd.ExcelFile(direccion_archivo)
        df_modelos_escogidos = pd.read_excel(self.archivo_excel,
                                             sheet_name=NOMBRE_HOJA_MODELOS_ESCOGIDOS)

        self.modelos_escogidos = df_modelos_escogidos.set_index('Subsector').to_dict()['Modelo']
        self.detalle_modelos = pd.read_excel(self.archivo_excel,
                                             sheet_name=NOMBRE_HOJA_DETALLE_MODELOS_ESCOGIDOS)
        self.agno_i = AGNO_INICIAL
        self.agno_f = AGNO_FINAL
        self.meses = MESES
        logger.info(f'Leyendo datos de modelos econometricos en {direccion_archivo}')
        logger.info(f'Preparando datos para proyectar entre {self.agno_i} y {self.agno_f}')

    def entregar_modelos_escogidos(self) -> dict:
        """
        Devuelve los modelos escogidos en un diccionario
        :return: Diccionario[Subsector] -> numero escogido
        """
        return self.modelos_escogidos

    def armar_df_proyecciones(self) -> dict[pd.DataFrame]:
        """
        Metodo para armar el dataframe que sera usado como base para realizar las proyecciones
        :return: entrega un diccionario con un dataframe para cada subsector economico
        """
        diccionario_datos_modelos = dict()
        df_temporal = self._armar_df_temporal()
        for subsector, modelo in self.modelos_escogidos.items():
            logger.info(f'Procesando coeficientes y efectos fijos del subsector: {subsector} modelo numero: {modelo}')
            resolucion_coef, resolucion_ef = self.obtener_resolucion_modelo(modelo, subsector)
            df_efectos_fijos = self._obtener_efectos_fijos(modelo, subsector, resolucion_ef)
            df_proyeccion_modelo = df_temporal.join(df_efectos_fijos, how='cross')
            dict_coeficientes = self._obtener_coeficientes(modelo, subsector)
            for variable, coeficiente in dict_coeficientes.items():
                df_proyeccion_modelo[f'Coef_{variable}'] = coeficiente
            try:
                dict_coeficientes_cuadrado = self._obtener_coeficientes_cuadrado(modelo, subsector)
                for variable, coeficiente in dict_coeficientes_cuadrado.items():
                    df_proyeccion_modelo[f'Coef2_{variable}'] = coeficiente
            except ValueError:
                logger.warning(f'Subsector {subsector} modelo numero: {modelo} no tiene datos de coeficientes con '
                               f'variables al cuadrado ( '
                               f'opcional)')
            diccionario_datos_modelos[subsector] = df_proyeccion_modelo
        return diccionario_datos_modelos

    def _armar_df_temporal(self) -> pd.DataFrame:
        """
        Metodo para construir un dataframe con resolucion mensual desde el año inicial al año final
        :return: dataframe con columnas [Año,Mes]
        """
        lista_agnos = self._armar_lista_agnos_proyeccion()
        df_agnos = pd.DataFrame(data={'Año': lista_agnos})
        lista_meses = self._armar_lista_meses_proyeccion()
        df_meses = pd.DataFrame(data={'Mes': lista_meses})
        df_temporal = df_agnos.join(df_meses, how='cross')
        return df_temporal

    def _armar_lista_agnos_proyeccion(self) -> list[int]:
        """
        Metodo para construir una lista con los años de la proyeccion
        :return: lista de años
        """
        lista_agnos = list(range(self.agno_i, self.agno_f + 1))
        return lista_agnos

    def _armar_lista_meses_proyeccion(self) -> list[int]:
        """
        Metodo para construir la lista de meses
        :return: lista de meses
        """
        lista_meses = list(range(1, self.meses + 1))
        return lista_meses

    def obtener_resolucion_modelo(self, modelo: int, subsector: str) -> tuple[str, str]:
        """
        Metodo que obtiene la resolucion de los efectos fijos y variables para cada modelo y subsector
        :param modelo: indice numerico del modelo a utilizar
        :param subsector: subsector economico
        :return: dos strings indicando las resoluciones relevantes del modelo
        """
        resolucion_coef = self.detalle_modelos.loc[(self.detalle_modelos['Subsector'] == subsector) &
                                                   (self.detalle_modelos[
                                                        'Indice_Modelo'] == modelo), 'Resolucion_Coef'].item()
        resolucion_ef = self.detalle_modelos.loc[(self.detalle_modelos['Subsector'] == subsector) &
                                                 (self.detalle_modelos[
                                                      'Indice_Modelo'] == modelo), 'Resolucion_EF'].item()
        #logger.debug(f'Modelo {modelo} {subsector}: Res_coef {resolucion_coef} y Res_EF {resolucion_ef}')
        return resolucion_coef, resolucion_ef

    def _obtener_efectos_fijos(self, modelo: int, subsector: str, resolucion_ef: str) -> pd.DataFrame:
        """
        Metodo que lee y procesa los efectos fijos y constante. Para ello asigna el efecto fijo como la suma del efecto
        fijo de cada elemento y lo suma a la constante leida tambien desde los datos de entrada.
        :param modelo: indice de modelo a utilizar
        :param subsector: subsector economico
        :param resolucion_ef: resolucion del efecto fijo. Ej: Barra, region, empresa, etc.
        :return: dataframe con cada elemento en cada fila con el efecto fijo + constante como valor asociado
        """
        nombre_hoja = f'{PREFIJO_EFECTOS_FIJOS}_{subsector}_{modelo}'
        df_efectos_fijos = pd.read_excel(self.archivo_excel,
                                         sheet_name=nombre_hoja)
        constante = df_efectos_fijos.loc[(df_efectos_fijos['Indice'] == 'Constante'), 'Total'].item()
        df_efectos_fijos.drop(df_efectos_fijos[df_efectos_fijos.Indice == 'Constante'].index, inplace=True)
        df_efectos_fijos.rename(columns={'Indice': resolucion_ef, 'Total': 'Efecto_Fijo'}, inplace=True)

        self._filtrar_elementos(df_efectos_fijos, resolucion_ef, subsector)

        df_efectos_fijos['Efecto_Fijo'] = df_efectos_fijos['Efecto_Fijo'] + constante
        df_efectos_fijos.reset_index(drop=True, inplace=True)
        return df_efectos_fijos

    def _filtrar_elementos(self, df_efectos_fijos, resolucion_ef, subsector):
        """
        Metodo que filtra elementos de la lista para proyectar. Va a buscar esta lista en hoja en el excel modelo
        que comienza por filtro Filtro_Barra por ejemplo
        :param df_efectos_fijos: dataframe de efectos fijos leidos
        :param resolucion_ef: resolucion de los efectos fijos
        :param subsector: subsector respectivo
        """
        try:
            nombre_filtro = f'{PREFIJO_FILTRO}_{resolucion_ef}'
            df_filtro = pd.read_excel(self.archivo_excel, sheet_name=nombre_filtro, usecols=[resolucion_ef, subsector])
            df_filtro[subsector] = df_filtro[subsector].astype(int)
            lista_filtro = list(df_filtro.loc[df_filtro[subsector] == 0, resolucion_ef].unique())
            df_efectos_fijos.drop(df_efectos_fijos[df_efectos_fijos[resolucion_ef].isin(lista_filtro)].index, inplace=True)
            logger.info(f'Filtrando {len(lista_filtro)} {resolucion_ef} para proyectar {subsector}')
        except ValueError:
            logger.warning(f'No se encuentra hoja {PREFIJO_FILTRO}_{resolucion_ef}, no se filtraran estos datos para el'
                           f' subsector {subsector}')

    def _obtener_coeficientes(self, modelo: int, subsector: str) -> dict[float]:
        """
        Metodo que extrae los coeficientes de las variables explicativas en un diccionario
        :param modelo: indice de modelo seleccionado
        :param subsector: subsector economico
        :return: diccionario[Nombre de Variabloe] -> Coeficiente de Variable
        """
        nombre_hoja = f'{PREFIJO_COEFICIENTES_VARIABLES}_{subsector}_{modelo}'
        df_coeficientes = pd.read_excel(self.archivo_excel, sheet_name=nombre_hoja)
        dict_coeficientes = df_coeficientes.set_index('Variable').to_dict()['Coeficiente']
        return dict_coeficientes

    def _obtener_coeficientes_cuadrado(self, modelo: int, subsector: str) -> dict[float]:
        """
        Metodo que extrae los coeficientes de las variables explicativas al cuadrado en un diccionario
        :param modelo: indice de modelo seleccionado
        :param subsector: subsector economico
        :return: diccionario[Nombre de Variabloe] -> Coeficiente de Variable
        """
        nombre_hoja = f'{PREFIJO_COEFICIENTES_VARIABLES_CUADRADO}_{subsector}_{modelo}'
        df_coeficientes = pd.read_excel(self.archivo_excel, sheet_name=nombre_hoja)
        dict_coeficientes = df_coeficientes.set_index('Variable').to_dict()['Coeficiente']
        return dict_coeficientes


def main():
    ruta = os.sep.join(['..', 'test', 'test_inputs', 'Modelos_test.xlsx'])
    procesador_modelos = LectorModelosEconometricos(ruta)
    procesador_modelos.armar_df_proyecciones()
    print('end')


if __name__ == '__main__':
    main()
