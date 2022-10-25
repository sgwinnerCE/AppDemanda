import pandas as pd

from configuracion import *


class LectorModelosEconometricos:

    def __init__(self, direccion_archivo: str) -> None:
        self.archivo_excel = pd.ExcelFile(direccion_archivo)
        df_modelos_escogidos = pd.read_excel(self.archivo_excel,
                                             sheet_name=NOMBRE_HOJA_MODELOS_ESCOGIDOS)
        self.modelos_escogidos = df_modelos_escogidos.set_index('Subsector').to_dict()['Modelo']

    def entregar_modelos_escogidos(self) -> dict:
        return self.modelos_escogidos
