import os
import logging
import time

from configuracion import USAR_ENCUESTAS, USAR_USOS_FINALES
from src.CalculadoraEnergia import CalculadoraEnergia
from src.CompiladorEscenarios import CompiladorEscenarios
from src.ProcesadorModelosIntensidad import ModelosIntensidad
from src.ProcesadorUsosFinales import ProcesadorUsosFinales
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

    logger.info('Iniciando ejecucion de DEMPRO-GIS v1.0')
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

    modelos_intensidad = ModelosIntensidad(ruta_archivo_modelos, ruta_archivo_escenarios, direccion_datos_historicos, ruta_archivo_diccionarios)
    modelos_intensidad.calcular_proyecciones()
    df_compilado = calculador.entregar_df_compilado()
    df_compilado = modelos_intensidad.agregar_proyeccion_modelo_intensidad(df_compilado)
    calculador.actualizar_proyeccion(df_compilado)

    if USAR_ENCUESTAS:
        procesador_encuestas = ProcesadoraEncuestas(direccion_encuestas)
        df_compilado = calculador.entregar_df_compilado()
        procesador_encuestas.agregar_proyeccion(data_proyeccion=df_compilado)
        procesador_encuestas.eliminar_proyeccion_macroeconomica()
        procesador_encuestas.agregar_dato_encuesta()
        calculador.actualizar_proyeccion(procesador_encuestas.obtener_proyeccion_actualizada())

    if USAR_USOS_FINALES:
        direccion_usos_finales = os.sep.join(['input'])
        usos_finales = ProcesadorUsosFinales(ruta_archivo_modelos)
        usos_finales.procesar_usos_finales(direccion_usos_finales, ruta_archivo_diccionarios)
        df_compilado = calculador.entregar_df_compilado()
        df_compilado = usos_finales.agregar_proyeccion(data_proyeccion=df_compilado)
        calculador.actualizar_proyeccion(df_compilado)
    calculador.guardar_proyeccion_compilada(ruta_guardado)
    calculador.guardar_proyeccion_compilada_agrupada(ruta_guardado, ruta_archivo_diccionarios)

    logger.info(f'Ejecucion finalizada en {round(time.time() - start_time, 2)} segundos')


if __name__ == '__main__':
    main()
