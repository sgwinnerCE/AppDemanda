# Configuracion tempral
AGNO_INICIAL = 2022
AGNO_FINAL = 2041
MESES = 12

# Deficion Nombres en Hojas Modelos

NOMBRE_HOJA_MODELOS_ESCOGIDOS = 'Configuracion'
NOMBRE_HOJA_DETALLE_MODELOS_ESCOGIDOS = 'DetalleModelos'
PREFIJO_EFECTOS_FIJOS = 'EF'
PREFIJO_COEFICIENTES_VARIABLES = 'Var'
PREFIJO_COEFICIENTES_VARIABLES_CUADRADO = 'Var2'
PREFIJO_FILTRO = 'Filtro'
PREFIJO_EFECTOS_FIJOS_MES = 'EFMes'
PREFIJO_DESAGRUPACION = 'Desagregacion'

# Deficion Nombres en Hojas Modelos
NOMBRE_HOJA_VARIABLES_NACIONALES = 'VarMensuales'

# Tipo de variable

DICCIONARIO_TIPO_VARIABLE = {
    'IMACEC': 'Nacional',
    'Precio': 'Nacional',
    'Poblacion': 'Comuna',
    'Vivienda': 'Comuna',
    'ProduccionCU': 'Empresa',
    'OCED6': 'Nacional',
    'EficienciaCU': 'Nacional',
    'ProcesadoCU': 'Empresa',
    'ProduccionAcero': 'Nacional',
    'ProduccionCemento': 'Nacional'
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
    'ReguladosLD': 'AMBOS',
    'Cobre': 'LIBRE',
    'Acero': 'LIBRE',
    'Cemento': 'LIBRE',
    'IndustriasVarias': 'LIBRE'
}

TASA_MAXIMA = 0.05

