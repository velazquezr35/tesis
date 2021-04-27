# Tesis - UPDATE 27/04
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
```

## Archivos subidos - comentarios y descripción

El análisis se divide en dos partes, con sendos prefijos:

- CRU: Archivos asociados al optimizador y cálculo de crucero
- META: Archivos asociados a la generación del MetaModel de viento

A continuación se presenta cada uno, de manera breve.

### CRU_main_crucero
Archivo principal.

Código principal para el cálculo de crucero y su optimización. Importa y utiliza otros módulos.
#### Clases

```
class export_opts()
```
Clase para opciones de exportación de perfiles de vuelo y figuras: Define nombres y carpetas.

```
class res_SIM()
```
Clase para guardar (y luego exportar con Pickle) los perfiles principales resultado de la simulación (h, X, V, ts, N), el consumo y los parámetros que devuelve el optimizador (número de iteraciones, tolerancia, etc.).

```
class otp_i()
```
Clases para definir forma de cálculo de la función principal. Contiene flags.


```
class input_profile()
```
Clase para definir perfiles de vuelo de entrada (sea un guess o un cálculo 'manual').


#### Funciones
```
simulador_crucero():
```
Función principal que calcula el consumo de combustible para un perfil dado. Contiene algunas opciones extras para ploteo rápido de figuras (no definitivo seguramente). Calcula utilizando las ecuaciones de vuelo, preserva las distintas variables y penaliza de manera previa al *return*. Devuelve consumo y perfiles de variables principales.

```
optimizame():
```
Función auxiliar que solamente devuelve el consumo de *simulador_crucero*. Se la definió siguiendo el código de la tesis ejemplo, pero seguramente se la quite, tomando output[0] (que es el consumo) directamente dentro del optimizador.

```
res_import_export():
```
Función general para ploteo y guardado de figuras, más prolijo y completo que el built-in del simulador. También exporta e importa usando Pickle las distintas clases de la simulación.

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

Contiene la info del modelo atmosférico, el modelo del motor (copiado de la tesis ejemplo), el modelo de CD0 de la polar del avión y los datos del avión (S, peso inicial, AR, Oswald). Contiene algunas líneas comentadas que se usaron originalmente para plotear curvas del motor. Se las va a quitar.

#### Funciones
```
CD0_model():
```
```
planedata():
```
```
turbofan():
```
```
isa_ATM():
```

### CRU_wind_eval
Archivo principal.

Función única. Determina rumbo (por ahora ejemplo fijo, se actualizará considerando rutas variables), obtiene magnitud y dirección del viento. Devuelve la componente proyectada local.

**Devuelve en FT/S** (ver si cambiar)

### CRU_nav_module
Archivo auxiliar. Permite plotear estaciones y ruta genérica sobre un mapa del lugar. 

Código en desarrollo, para calcular distancias entre dos puntos [LAT,LON] usando Cartopy (define un Geoide WGS84), lo que debería mejorar la aproximación respecto a obtenerla y cargarla manualmente desde Google, por ejemplo. 

### CRU_extra_text
Archivo auxiliar.

Manejo de archivos de texto para guardar/cargar perfiles de vuelo en un array dentro de un .txt. Actualmente se está agregando para trabajar directamente con Pickle (y guardar clases enteras con más info).

## 
### META_main_kringing
Archivo principal.

Genera el metamodel utilizando los perfiles input proovistos. Además toma el tiempo que tarda su ejecución. Devuelve el modelo terminado.

### META_generador_datos
Archivo principal.

Este archivo contiene una función que provee M líneas de un archivo de texto .txt que contiene las lecturas de la magnitud y dirección del viento f(h). Además, filtra y ordena, debido a que la información se presenta en "bloques" y no todas las líneas son utilizables. La restricción de M líneas viene del tamaño máximo del array que puede alimentarse a #main_kringing (error bad_alloc).

Además contiene opciones de impresión y ploteo built-in.


### META_test_evaluador
Archivo temporal.

Archivo temporal que se utiliza para obtener modelos intermedios y definitivos, sacar gráficas, comparar y probar el análisis de viento. Idealmente este archivo no va a formar parte de la tesis, sino que sus funciones más importantes se guardarían en #mods_utiles p/ej.

### META_OS_module
Archivo auxiliar.

Generado para leer las estaciones que hay disponibles en una carpeta de "datos". Posibilidad de incluir funciones-filtro.


### META_mods_utiles
Archivo principal.

Contiene funciones varias para generar, evaluar, probar, plotear y filtrar los modelos-meta.

#### Funciones de interés

```
generar_input():
```
Función que genera el perfil que se alimenta a #main_kringing para la generación del modelo de viento. Esta función lee estación por estación la info y la agrupa en un array 'global'. Sirve para generar perfiles de Magnitud y de Dirección.
```
exp_imp_meta
```
Función que guarda/carga el estudio del META en formato .XML de modo que se disponga del mismo para posteriores corridas con el optimizador / simulador. 
