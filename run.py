import os
import logging

from src.LectorModelosEconometricos import LectorModelosEconometricos

logger = logging.getLogger('simple_example')
logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)


def main():
    logger.info('Iniciando ejecucion de AppDemandaElectrica v0.1')
    ruta_modelo = os.sep.join(['input', 'Modelos.xlsx'])
    procesador_modelos = LectorModelosEconometricos(ruta_modelo)
    df_coeficientes = procesador_modelos.armar_df_proyecciones()
    logger.info('Ejecucion finalizada')


if __name__ == '__main__':
    main()
