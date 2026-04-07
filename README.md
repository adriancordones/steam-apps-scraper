# Dataset: Steam Apps Metadata

Dataset de metadatos de aplicaciones publicadas en la tienda de Steam (store.steampowered.com), recopilado mediante web scraping con Scrapy. Incluye información comercial, técnica y de reseñas de juegos, DLCs y soundtracks disponibles en la plataforma.

### Tabla de contenidos

- [Descripción](#descripción)
- [Guía de uso](#guía-de-uso)
    - [Requisitos](#requisitos)
    - [Instrucciones](#instrucciones)
    - [Ejemplos](#ejemplos)
- [Integrantes del grupo](#intregantes-del-grupo)
- [Licencia](#licencia)
- [Referencias](#referencias)

## Descripción

El scraper opera en dos fases encadenadas. Primero, `LinksSpider` recorre las páginas de resultados de búsqueda de Steam y recopila los IDs de las aplicaciones listadas. A continuación, `AppsSpider` visita la página de cada aplicación y extrae sus metadatos, que se exportan al CSV final.

## Guía de uso

### Requisitos

Antes de ejecutar el script, es necesario instalar todas sus dependencias con:

```
pip install -r requirements.txt
```

### Instrucciones

El punto de entrada es `main.py`, que ejecuta ambos spiders de forma secuencial. La configuración del scraper (headers, throttling, ruta de salida, etc.) se gestiona desde `source/steam_apps_scraper/settings.py`.

Los parámetros que acepta la ejecución a través de `main.py` se controlan modificando la llamada a `runner.crawl` en dicho fichero:

**Parámetros de `LinksSpider`:**
- `srt_page` (int): Primera página de resultados de búsqueda a procesar (default: 1).
- `end_page` (int): Última página de resultados (inclusive) (default: 1).
- `labels` (str): Query string con filtros adicionales para la URL (default: ?hidef2p=1&ndl=1&l=es).

**Parámetros de `AppsSpider`:**
- `app_ids` (list o str): Lista de IDs de Steam a procesar (default: []).
- `labels` (str): Query string para la URL de cada app (default: ?l=es).

### Ejemplos

#### **Ejemplo 1.** Scraping con filtros predeterminados:

Se dejan los filtros por defecto: ordenar por relevancia, no incluir juegos F2P, idioma de página web en español y no elegir un idioma de juego por defecto.

Modificar `main.py`:
```python
await runner.crawl(crawler, srt_page=1, end_page=5)
```

Y ejecutar:
```bash
cd source
python main.py
```
Este ejemplo procesará las 5 primeras páginas de resultados ordenados por relevancia.

#### **Ejemplo 2.** Scraping filtrando para un tag concreto:

Modificar `main.py`:
```python
await runner.crawl(crawler, srt_page=1, end_page=3, labels="?tags=21&hidef2p=1&l=es")
```

Y ejecutar:
```bash
cd source
python main.py
```
Este ejemplo procesará las 3 primeras páginas de resultados para el tag de `Aventura`.

#### **Ejemplo 3.** Scraping de apps concretas por ID desde la CLI de Scrapy:

Alternativamente, `AppsSpider` puede ejecutarse de forma independiente desde la CLI de Scrapy, pasando los IDs como cadena separada por comas.

Ejemplo:
```bash
cd source
scrapy crawl apps -a app_ids="413150,391540"
```
Este ejemplo procesará Stardew Valley y Undertale.

## Integrantes del grupo

Esta práctica fue realizada por **Agustín Barbatelli Balboa** y **Adrián Cordones Martínez**.

## Licencia

Shield: [![CC BY-NC-SA 4.0][cc-by-nc-sa-shield]][cc-by-nc-sa]

Esta obra está bajo licencia [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International][cc-by-nc-sa].

[![CC BY-NC-SA 4.0][cc-by-nc-sa-image]][cc-by-nc-sa]

[cc-by-nc-sa]: https://creativecommons.org/licenses/by-nc-sa/4.0/deed.es
[cc-by-nc-sa-image]: https://licensebuttons.net/l/by-nc-sa/4.0/88x31.png
[cc-by-nc-sa-shield]: https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg

## Referencias

- Subirats Maté, L. y Calvo González, M. (2019) Web scraping. Barcelona: Editorial UOC.
- Lawson, R. (2015) Web Scraping with Python: Successfully scrape data from any website with the power of Python. Birmingham: Packt Publishing. ISBN: 9781782164364.
- Scrapy developers (2026) Scrapy documentation (versión 2.14.2). [En línea]. URL: https://docs.scrapy.org/en/latest/ [Consultado: abril de 2026].
- Valve Corporation (2026) Steam Store. [En línea]. URL: https://store.steampowered.com [Consultado: abril de 2026].