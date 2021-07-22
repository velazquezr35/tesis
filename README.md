# Tesis - Current version: 20 05 21
Tesis Rodrigo Velazquez - Optimizador de crucero + Modelo de viento 3D WS//WD. 

El código en general requiere las siguientes librerías:
```
- Numpy
- Scipy
- Matplotlib
- Pickle
- Cartopy (para ploteos de mapas)
- Shapely
- Openturns
- Time
- os
- pyproj
- SCIKIT AERO https://pypi.org/project/scikit-aero/
- IGRA https://pypi.org/project/igra/
```

## Archivos subidos - comentarios y descripción

El análisis se divide en dos partes, con sendos prefijos:

- CRU: Archivos asociados al optimizador y cálculo de crucero
- META: Archivos asociados a la generación del MetaModel de viento

A continuación se presenta cada uno, de manera breve.

### CRU_main_crucero
Archivo principal.

Código principal para el cálculo de crucero y su optimización. Importa y utiliza otros módulos.

#### Funciones
```
simulador_crucero():
```
Función principal que calcula el consumo de combustible para un perfil dado. Contiene algunas opciones extras para ploteo rápido de figuras (no definitivo seguramente). Calcula utilizando las ecuaciones de vuelo, preserva las distintas variables y penaliza de manera previa al *return*. Devuelve consumo y perfiles de variables principales.

#### Extras del archivo

Contiene una función para comparar consumo vs N y algunas líneas comentadas al cierre. En proceso de limpieza / mejora.

### CRU_penal
Archivo principal.

Código para penalizar el perfil de vuelo post cálculo del consumo. Evalúa los perfiles de ciertas variables y suma combustible según corresponda.

#### Funciones
```
penalización():
```
Función única del código, que realiza lo anterior.

### CRU_extra_funcs
Archivo principal.

Contiene la info del modelo atmosférico ISA, manejo y generación del 'avión' (modelos de motor, parámetros, modelo de polar, etc.) de OpenAP.


### CRU_wind_eval
Archivo principal.

Función única. Determina rumbo (por ahora ejemplo fijo, se actualizará considerando rutas variables), obtiene magnitud y dirección del viento. Devuelve la componente proyectada local.

**Devuelve en FT/S** (ver si cambiar)

### CRU_nav_module
Archivo auxiliar. 

Permite plotear estaciones y ruta genérica sobre un mapa del lugar.

Funciones para cálculo de distancias, cabeceo y ruta paso a paso mediante Cartopy/Pyproj. Waypoints definidos por [LATs], [LONGs]. Se utiliza Geoide WGS84.

### CRU_data_manag
Archivo principal.

Manejo de archivos BIN para exportar e importar perfiles (inputs, parámetros y resultados), con Pickle.
Funciones de generación de perfiles __dicts__ 
Manejo de archivos de texto para guardar/cargar perfiles de vuelo en un array dentro de un .txt.

### CRU_plot_module
Archivo auxiliar.

Ploteo de perfiles de vuelo.
Ploteo de gráficas comparativas para corridas multi-N.

### META_main
Archivo principal.

Archivo para comandar la generación, manejo y testeo de los MetaModels

### META_handler
Archivo principal.

Este archivo contiene las funciones principales que verificarn estaciones, descargan desde IGRAA, leen, filtran y generan inputos para alimentar modelos Krg. Funciones extras para manejo de datos.

### META_quatests
Archivo secundario.

Archivo planteado para incluir tests que las estaciones deben aprobar para ser incluidas en los META. Esto evita la generación de valores no físicos en la evaluación de los metamodels. Generalmente ocurre por disponer información hasta cotas bajas.

### META_plots
Archivo principal.

Contiene funciones varias para plotear de manera genérica datos y evaluaciones de modelos.

### META_krg_factory
Archivo principal.

Contiene la función para generar el MetaModel con OpenTurns. Además, permite su exportación e importación en formato .XML. Función extra para evaluar punto a punto o sobre arrays.
