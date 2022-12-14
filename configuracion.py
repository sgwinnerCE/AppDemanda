# Configuracion temporal
AGNO_INICIAL = 2022
AGNO_FINAL = 2041
MESES = 12

# Flag si se quiere ajustar proyeccion a ultimo dato historico
AJUSTE = True

# Flag si se quiere utilizar informacion
USAR_ENCUESTAS = True
USAR_USOS_FINALES = True

# Deficion Nombres

NOMBRE_HOJA_MODELOS_ESCOGIDOS = 'Configuracion'
NOMBRE_HOJA_DETALLE_MODELOS_ESCOGIDOS = 'DetalleModelos'
PREFIJO_EFECTOS_FIJOS = 'EF'
PREFIJO_COEFICIENTES_VARIABLES = 'Var'
PREFIJO_COEFICIENTES_VARIABLES_CUADRADO = 'Var2'
PREFIJO_COEFICIENTES_REZAGOS = 'Lag'
PREFIJO_FILTRO = 'Filtro'
PREFIJO_EFECTOS_FIJOS_MES = 'EFMes'
PREFIJO_DESAGRUPACION = 'Desagregacion'
NOMBRE_HOJA_ELECTRIFICACION = 'Electricidad_barra_mes'
NOMBRE_HOJA_USOS_FINALES = 'Configuracion_UsosFinales'
NOMBRE_HOJA_MODELOS_INTENSIDAD = 'ModelosIntensidad'

# Deficion Nombres en Hojas Modelos
NOMBRE_HOJA_VARIABLES_NACIONALES = 'VarMensuales'

# Tipo de variable

DICCIONARIO_TIPO_VARIABLE = {
    'IMACEC': 'Nacional',
    'IMACEC_Industria': 'Nacional',
    'IMACEC_Industria_L1': 'Nacional',
    'Precio': 'Nacional',
    'Precio_L1': 'Nacional',
    'Poblacion': 'Comuna',
    'Vivienda': 'Comuna',
    'ProduccionCU': 'Empresa',
    'OCED6': 'Nacional',
    'EficienciaCU': 'Nacional',
    'ProcesadoCU': 'Empresa',
    'ProduccionAcero': 'Nacional',
    'ProduccionCemento': 'Nacional',
    'ProduccionHierro': 'Nacional',
    'ProduccionCelulosa': 'Nacional'
}

# Nombre Datos
ENERGIA = 'Demanda'

# Diccionario para pasar meses de numoro a plabra
DICC_MESES = {
    1: 'ENE',
    2: 'FEB',
    3: 'MAR',
    4: 'ABR',
    5: 'MAY',
    6: 'JUN',
    7: 'JUL',
    8: 'AGO',
    9: 'SEP',
    10: 'OCT',
    11: 'NOV',
    12: 'DIC'
}

DICC_TIPO = {
    'ReguladosLD': 'REGULADOS Y LD',
    'Cobre': 'LIBRE',
    'Acero': 'LIBRE',
    'Cemento': 'LIBRE',
    'IndustriasVarias': 'LIBRE',
    'Hierro': 'LIBRE',
    'Celulosa': 'LIBRE',
    'Comercial': 'LIBRE',
    'Salitre': 'LIBRE',
    'Petroquimica': 'LIBRE',
    'MinasVarias': 'LIBRE',
    'Maritimo': 'LIBRE',
    'Ferroviario': 'LIBRE',
    'Electricidad': 'LIBRE',
    'Gas Natural': 'LIBRE',
    'Petroleo': 'LIBRE'
}

TASA_MAXIMA = 0.08

LISTA_AGRUPACION = [
    'Subestacion'
]

DICC_CARPETA_DATOS = {
    'Delta': 'ModeloUsoFinal',
    'Electromovilidad': 'Electromovilidad',
    'Netbilling': 'Netbilling',
    'PMGD': 'PMGD'
}

DICC_DATOS_USOS = {
    'Delta': 'Electricidad_barra_mes',
    'Electromovilidad': 0,
    'Netbilling': 0,
    'PMGD': 0
}

DICC_ORIGEN_USOS = {
    'Delta': 'Modelo Usos Finales',
    'Electromovilidad': 'Proyeccion Electromovilidad',
    'Netbilling': 'Proyeccion Netbilling',
    'PMGD': 'Proyeccion PMGD'
}
