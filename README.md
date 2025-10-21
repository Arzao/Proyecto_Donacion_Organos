## Contenido del Repositorio

La estructura del proyecto está organizada de la siguiente manera:

* `/data/`: Contiene los conjuntos de datos.
    * `dataset_sucio.csv`: La base de datos original, antes de cualquier modificación.
    * `donantes_organos_limpio.csv`: El dataset resultante tras el proceso de limpieza, listo para el análisis.
* `/reportes/`: Contiene los documentos PDF que resumen las fases del proyecto.
    * `01_Analisis_Exploratorio.pdf`: Es el reporte de **introducción y planificación**. Define el problema, los stakeholders, las hipótesis  y las preguntas clave .
    * `02_Limpieza_Datos.pdf`: Es el reporte de **limpieza y transformación**. Diagnostica, manipula y limpia los valores para obtener una base de datos limpia y lista para poder ser trabajada para un futuro análisis.
    * *(Próximamente) 03_Analisis_Hallazgos.pdf*: (Será el reporte futuro con las gráficas y conclusiones del análisis).
* `01_Analisis_Exploratorio.ipynb`: Es el Jupyter Notebook con todo el código Python. **Este archivo documenta la Fase 1: Limpieza y Transformación de Datos**.
* *(Próximamente) 02_Analisis_Visual.ipynb*: (Será el notebook futuro que contendrá la **Fase 2: Análisis Exploratorio (EDA), visualizaciones** y validación de hipótesis).
* `README.md`: Este archivo, que sirve como guía principal del repositorio.