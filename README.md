# Tesis - UPDATE 27/04
Tesis Rodrigo Velazquez - Optimizador de crucero + Modelo de viento 3D WS//WD

# Archivos subidos - comentarios y descripción

El análisis se divide en dos partes, con sendos prefijos:

- CRU: Archivos asociados al optimizador y cálculo de crucero
- META: Archivos asociados a la generación del MetaModel de viento

A continuación se presenta cada uno, de manera breve.

### CRU_main_crucero

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
optimizame()
```
Función auxiliar que solamente devuelve el consumo de *simulador_crucero*. Se la definió siguiendo el código de la tesis ejemplo, pero seguramente se la quite, tomando output[0] (que es el consumo) directamente dentro del optimizador.

```
res_import_export()
```
Función general para ploteo y guardado de figuras, más prolijo y completo que el built-in del simulador. También exporta e importa usando Pickle las distintas clases de la simulación.
