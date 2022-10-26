import os

import pandas as pd

from configuracion import *


class LectorModelosEconometricos:

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

    def entregar_modelos_escogidos(self) -> dict:
        return self.modelos_escogidos

    def armar_df_proyecciones(self) -> dict[pd.DataFrame]:
        diccionario_datos_modelos = dict()
        df_temporal = self._armar_df_temporal()
        for subsector, modelo in self.modelos_escogidos.items():
            resolucion_coef, resolucion_ef = self._obtener_resolucion_modelo(modelo, subsector)
            df_efectos_fijos = self._obtener_efectos_fijos(modelo, subsector, resolucion_ef)
            df_proyeccion_modelo = df_temporal.join(df_efectos_fijos, how='cross')
            dict_coeficientes = self._obtener_coeficientes(modelo, subsector)
            for variable, coeficiente in dict_coeficientes.items():
                df_proyeccion_modelo[f'Coef_{variable}'] = coeficiente
            diccionario_datos_modelos[subsector] = df_proyeccion_modelo
        return diccionario_datos_modelos

    def _armar_df_temporal(self) -> pd.DataFrame:
        lista_agnos = self._armar_lista_agnos_proyeccion()
        df_agnos = pd.DataFrame(data={'Año': lista_agnos})
        lista_meses = self._armar_lista_meses_proyeccion()
        df_meses = pd.DataFrame(data={'Mes': lista_meses})
        df_temporal = df_agnos.join(df_meses, how='cross')
        return df_temporal

    def _armar_lista_agnos_proyeccion(self):
        lista_agnos = list(range(self.agno_i, self.agno_f + 1))
        return lista_agnos

    def _armar_lista_meses_proyeccion(self):
        lista_meses = list(range(1, self.meses + 1))
        return lista_meses

    def _obtener_resolucion_modelo(self, modelo, subsector):
        resolucion_coef = self.detalle_modelos.loc[(self.detalle_modelos['Subsector'] == subsector) &
                                                   (self.detalle_modelos[
                                                        'Indice_Modelo'] == modelo), 'Resolucion_Coef'].item()
        resolucion_ef = self.detalle_modelos.loc[(self.detalle_modelos['Subsector'] == subsector) &
                                                 (self.detalle_modelos[
                                                      'Indice_Modelo'] == modelo), 'Resolucion_EF'].item()
        return resolucion_coef, resolucion_ef

    def _obtener_efectos_fijos(self, modelo, subsector, resolucion_ef):
        nombre_hoja = f'{PREFIJO_EFECTOS_FIJOS}_{subsector}_{modelo}'
        df_efectos_fijos = pd.read_excel(self.archivo_excel,
                                         sheet_name=nombre_hoja)
        constante = df_efectos_fijos.loc[(df_efectos_fijos['Indice'] == 'Constante'), 'Total'].item()
        df_efectos_fijos.drop(df_efectos_fijos[df_efectos_fijos.Indice == 'Constante'].index, inplace=True)
        df_efectos_fijos.rename(columns={'Indice': resolucion_ef, 'Total': 'Efecto_Fijo'}, inplace=True)
        df_efectos_fijos['Efecto_Fijo'] = df_efectos_fijos['Efecto_Fijo'] + constante
        df_efectos_fijos.reset_index(drop=True, inplace=True)
        return df_efectos_fijos

    def _obtener_coeficientes(self, modelo, subsector):
        nombre_hoja = f'{PREFIJO_COEFICIENTES_VARIABLES}_{subsector}_{modelo}'
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
