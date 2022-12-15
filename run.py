import os
import logging
import time

from configuracion import USAR_ENCUESTAS
from src.CalculadoraEnergia import CalculadoraEnergia
from src.CompiladorEscenarios import CompiladorEscenarios
from src.LectorModelosEconometricos import LectorModelosEconometricos
from src.ProcesadoraEncuestas import ProcesadoraEncuestas

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
    start_time = time.time()

    logger.info('Iniciando ejecucion de AppDemandaElectrica v0.1')
    ruta_archivo_modelos = os.sep.join(['input', 'Modelos.xlsx'])
    ruta_archivo_diccionarios = os.sep.join(['input', 'Diccionarios.xlsx'])
    ruta_archivo_escenarios = os.sep.join(['input', 'Escenarios'])
    direccion_datos_historicos = os.sep.join(['input', 'Datos Historicos'])
    direccion_encuestas = os.sep.join(['input', 'Encuestas.xlsx'])
    ruta_guardado = os.sep.join(['output'])

    compilador = CompiladorEscenarios(ruta_archivo_modelos, ruta_archivo_escenarios, ruta_archivo_diccionarios)
    compilador.agregar_variables()
    compilador.guardar_df(ruta_guardado)
    calculador = CalculadoraEnergia(ruta_archivo_modelos, ruta_archivo_diccionarios)
    calculador.leer_df_compilados(compilador.entregar_df_compilados())
    calculador.obtener_proyeccion_completa(direccion_datos_historicos)
    calculador.guardar_proyecciones(ruta_guardado)
    calculador.compilar_proyecciones(ruta_archivo_diccionarios)

    if USAR_ENCUESTAS:
        procesador_encuestas = ProcesadoraEncuestas(direccion_encuestas)
        df_compilado = calculador.entregar_df_compilado()
        procesador_encuestas.agregar_proyeccion(data_proyeccion=df_compilado)
        procesador_encuestas.eliminar_proyeccion_macroeconomica()
        procesador_encuestas.agregar_dato_encuesta(ruta_guardado)
        calculador.actualizar_proyeccion(procesador_encuestas.obtener_proyeccion_actualizada())
    calculador.guardar_proyeccion_compilada(ruta_guardado)
    calculador.guardar_proyeccion_compilada_agrupada(ruta_guardado, ruta_archivo_diccionarios)

    logger.info(f'Ejecucion finalizada en {round(time.time() - start_time, 2)} segundos')


if __name__ == '__main__':
    main()
