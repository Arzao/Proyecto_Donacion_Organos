"""
Dashboard Interactivo - Análisis de Donación de Órganos en México
Proyecto Final - Introducción a Ciencia de Datos
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime

# Configurar matplotlib para gráficas con fondo blanco
plt.style.use('default')
plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['axes.facecolor'] = 'white'
plt.rcParams['savefig.facecolor'] = 'white'
plt.rcParams['text.color'] = 'black'
plt.rcParams['axes.labelcolor'] = 'black'
plt.rcParams['xtick.color'] = 'black'
plt.rcParams['ytick.color'] = 'black'
plt.rcParams['axes.edgecolor'] = 'black'

# Configuración de la página
st.set_page_config(
    page_title="Dashboard - Donación de Órganos México",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado para mejorar la apariencia
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #E57373;
        text-align: center;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #888;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    .author-name {
        font-size: 1rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
        font-style: italic;
    }
</style>
""", unsafe_allow_html=True)

# Paleta de colores personalizada
COLORES = ['#E57373', '#D4A574', '#A5C77F', '#7ECFC0', '#81A1C1', '#C895BF']

# Función para cargar los datos
@st.cache_data
def cargar_datos():
    """Carga y prepara el dataset limpio"""
    df = pd.read_csv('data/donantes_organos_limpio.csv')
    
    # Convertir fecha a datetime
    df['FECHA'] = pd.to_datetime(df['FECHA_PROCURACION'], errors='coerce')
    
    # Calcular total de órganos (sumando todas las columnas de órganos)
    columnas_organos = [
        'RINON_IZQUIERDO', 'RINON_DERECHO', 'RINON_BLOCK',
        'PULMON_IZQUIERDO', 'PULMON_DERECHO', 'CORAZON',
        'HIGADO', 'PANCREAS', 'INTESTINO',
        'CORNEA_IZQUIERDA', 'CORNEA_DERECHA',
        'PIEL', 'HUESOS', 'CORAZON_TEJIDOS'
    ]
    df['TOTAL_ORGANOS'] = df[columnas_organos].sum(axis=1)
    
    # Crear columnas adicionales
    df['ANIO'] = df['FECHA'].dt.year
    df['MES'] = df['FECHA'].dt.month
    df['RANGO_EDAD'] = pd.cut(
        df['EDAD_ANIOS'],
        bins=[0, 18, 30, 50, 150],
        labels=['0-18 (Niño/Joven)', '19-30 (Adulto Joven)', '31-50 (Adulto)', '51+ (Adulto Mayor)']
    )
    
    # Indicador de multiorgano
    df['ES_MULTIORGANO'] = (df['TOTAL_ORGANOS'] >= 3).astype(int)
    
    # Renombrar columna MUERTE a CAUSA_MUERTE
    df['CAUSA_MUERTE'] = df['MUERTE']
    
    return df

# Cargar datos
try:
    df = cargar_datos()
    
    # ========================================
    # SIDEBAR - Filtros
    # ========================================
    st.sidebar.markdown("## Filtros de datos")
    
    # Filtro por años
    anios_disponibles = sorted(df['ANIO'].dropna().unique())
    anios_seleccionados = st.sidebar.multiselect(
        "Seleccionar años:",
        options=anios_disponibles,
        default=anios_disponibles
    )
    
    # Filtro por tipo de donante
    tipos_donante = ['TODOS'] + list(df['TIPO_DONANTE'].unique())
    tipo_seleccionado = st.sidebar.selectbox(
        "Tipo de donante:",
        options=tipos_donante
    )
    
    # Filtro por entidad federativa (excluir DESCONOCIDO)
    entidades_validas = df[df['ENTIDAD_FEDERATIVA'] != 'DESCONOCIDO']['ENTIDAD_FEDERATIVA'].unique()
    entidades = ['TODAS'] + sorted(entidades_validas)
    entidad_seleccionada = st.sidebar.selectbox(
        "Entidad federativa:",
        options=entidades
    )
    
    # Filtro por rango de edad
    rangos_edad = ['TODOS'] + list(df['RANGO_EDAD'].dropna().unique())
    rango_edad_seleccionado = st.sidebar.selectbox(
        "Rango de edad:",
        options=rangos_edad
    )
    
    # Aplicar filtros
    df_filtrado = df.copy()
    
    if anios_seleccionados:
        df_filtrado = df_filtrado[df_filtrado['ANIO'].isin(anios_seleccionados)]
    
    if tipo_seleccionado != 'TODOS':
        df_filtrado = df_filtrado[df_filtrado['TIPO_DONANTE'] == tipo_seleccionado]
    
    if entidad_seleccionada != 'TODAS':
        df_filtrado = df_filtrado[df_filtrado['ENTIDAD_FEDERATIVA'] == entidad_seleccionada]
    
    if rango_edad_seleccionado != 'TODOS':
        df_filtrado = df_filtrado[df_filtrado['RANGO_EDAD'] == rango_edad_seleccionado]
    
    # ========================================
    # HEADER PRINCIPAL
    # ========================================
    st.markdown('<h1 class="main-header">Dashboard - Donación de Órganos en México</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Análisis Exploratorio de Datos | Proyecto Final</p>', unsafe_allow_html=True)
    st.markdown('<p class="author-name">Por: Jonathan Araiza Guzmán</p>', unsafe_allow_html=True)
    
    # ========================================
    # MÉTRICAS PRINCIPALES
    # ========================================
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total de donaciones",
            value=f"{len(df_filtrado):,}",
            delta=f"{len(df_filtrado)/len(df)*100:.1f}% del total"
        )
    
    with col2:
        promedio_organos = df_filtrado['TOTAL_ORGANOS'].mean()
        st.metric(
            label="Promedio de órganos",
            value=f"{promedio_organos:.2f}",
            delta="órganos/donante"
        )
    
    with col3:
        edad_promedio = df_filtrado['EDAD_ANIOS'].mean()
        st.metric(
            label="Edad promedio",
            value=f"{edad_promedio:.1f} años",
            delta="del donante"
        )
    
    with col4:
        multiorgano_pct = (df_filtrado['ES_MULTIORGANO'].sum() / len(df_filtrado)) * 100
        st.metric(
            label="Donaciones multi-órgano",
            value=f"{multiorgano_pct:.1f}%",
            delta="3+ órganos"
        )
    
    st.markdown("---")
    
    # ========================================
    # TABS PARA ORGANIZAR VISUALIZACIONES
    # ========================================
    tab1, tab2, tab3, tab4 = st.tabs([
        "Análisis general",
        "Análisis geográfico",
        "Instituciones",
        "Validación de hipótesis"
    ])
    
    # ========================================
    # TAB 1: ANÁLISIS GENERAL
    # ========================================
    with tab1:
        st.header("Análisis general de donaciones")
        
        # Fila 1: Distribución por tipo de donante
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Distribución por tipo de donante")
            tipo_counts = df_filtrado['TIPO_DONANTE'].value_counts()
            
            fig, ax = plt.subplots(figsize=(8, 6))
            colors = COLORES[:len(tipo_counts)]
            wedges, texts, autotexts = ax.pie(
                tipo_counts.values,
                labels=tipo_counts.index,
                autopct='%1.1f%%',
                startangle=90,
                colors=colors
            )
            ax.set_title('Porcentaje de donaciones por tipo de donante', fontsize=14, fontweight='bold', color='black')
            
            for autotext in autotexts:
                autotext.set_color('black')
                autotext.set_fontsize(12)
                autotext.set_fontweight('bold')
            
            for text in texts:
                text.set_color('black')
            
            plt.legend(tipo_counts.index, title="Tipo de donante", loc="best", 
                      labelcolor='black', title_fontsize='10', framealpha=0.7)
            st.pyplot(fig)
            plt.close()
        
        with col2:
            st.subheader("Promedio de órganos por edad y tipo")
            
            df_grafico = df_filtrado[df_filtrado['RANGO_EDAD'].notna()].copy()
            
            fig, ax = plt.subplots(figsize=(8, 6))
            sns.barplot(
                data=df_grafico,
                x='RANGO_EDAD',
                y='TOTAL_ORGANOS',
                hue='TIPO_DONANTE',
                estimator=np.mean,
                errorbar=('ci', 95),
                palette=COLORES,
                ax=ax
            )
            ax.set_title('Promedio de órganos donados por rango de edad y tipo de donante', 
                        fontweight='bold', color='black')
            ax.set_xlabel('Rango de edad del donante', fontweight='bold', color='black')
            ax.set_ylabel('Promedio de órganos/tejidos donados', fontweight='bold', color='black')
            ax.tick_params(colors='black')
            plt.xticks(rotation=15, ha='right')
            legend = plt.legend(title='Tipo de donante', loc='upper right')
            plt.setp(legend.get_texts(), color='black')
            plt.setp(legend.get_title(), color='black')
            
            # Añadir valores sobre las barras
            for container in ax.containers:
                ax.bar_label(container, fmt='%.2f', padding=3)
            
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()
        
        # Fila 2: Distribución de edades
        st.subheader("Distribución de edades de donantes")
        
        df_edad_valida = df_filtrado[df_filtrado['EDAD_ANIOS'] > 0].copy()
        
        fig, ax = plt.subplots(figsize=(14, 6))
        
        # Histograma
        n, bins, patches = ax.hist(
            df_edad_valida['EDAD_ANIOS'],
            bins=50,
            color=COLORES[0],
            alpha=0.7,
            edgecolor='black'
        )
        
        # Curva de densidad
        from scipy import stats
        density = stats.gaussian_kde(df_edad_valida['EDAD_ANIOS'])
        xs = np.linspace(df_edad_valida['EDAD_ANIOS'].min(), df_edad_valida['EDAD_ANIOS'].max(), 200)
        ys = density(xs)
        ax2 = ax.twinx()
        ax2.plot(xs, ys, color=COLORES[1], linewidth=2.5, label='Densidad')
        ax2.set_ylabel('Densidad', fontweight='bold', fontsize=12)
        
        # Línea de promedio
        promedio_edad = df_edad_valida['EDAD_ANIOS'].mean()
        ax.axvline(promedio_edad, color='red', linestyle='--', linewidth=2, 
                   label=f'Promedio: {promedio_edad:.1f} años')
        
        ax.set_xlabel('Edad del donante (Años)', fontweight='bold', fontsize=12, color='black')
        ax.set_ylabel('Frecuencia (total de donaciones)', fontweight='bold', fontsize=12, color='black')
        ax.set_title('Distribución de edades de donantes válidas (edad > 0)', 
                    fontweight='bold', fontsize=14, color='black')
        ax.tick_params(colors='black')
        ax2.tick_params(colors='black')
        legend = ax.legend(loc='upper right')
        plt.setp(legend.get_texts(), color='black')
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
        
        st.info(f"**Edad promedio de donantes:** {promedio_edad:.1f} años | **Total de registros válidos:** {len(df_edad_valida):,}")
    
    # ========================================
    # TAB 2: ANÁLISIS GEOGRÁFICO
    # ========================================
    with tab2:
        st.header("Análisis geográfico de donaciones")
        
        # Filtrar registros con entidad federativa desconocida para análisis geográfico
        df_geo = df_filtrado[df_filtrado['ENTIDAD_FEDERATIVA'] != 'DESCONOCIDO'].copy()
        
        # Top 10 entidades
        st.subheader("Top 10 entidades con más donaciones")
        
        top_10_entidades = df_geo['ENTIDAD_FEDERATIVA'].value_counts().head(10)
        
        fig, ax = plt.subplots(figsize=(12, 6))
        bars = ax.barh(range(len(top_10_entidades)), top_10_entidades.values, color=COLORES[0])
        ax.set_yticks(range(len(top_10_entidades)))
        ax.set_yticklabels(top_10_entidades.index)
        ax.invert_yaxis()
        ax.set_xlabel('Total de donaciones registradas', fontweight='bold', fontsize=12, color='black')
        ax.set_title('Top 10 entidades por número de donaciones', fontweight='bold', fontsize=14, color='black')
        ax.tick_params(colors='black')
        ax.grid(axis='x', alpha=0.3)
        
        # Añadir valores
        for i, (bar, value) in enumerate(zip(bars, top_10_entidades.values)):
            ax.text(value + 50, i, str(value), va='center', fontweight='bold')
        
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
        
        # Proporción de tipos de donante por entidad
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Bottom 5 entidades")
            
            bottom_5_entidades = df_geo['ENTIDAD_FEDERATIVA'].value_counts().tail(5)
            
            fig, ax = plt.subplots(figsize=(8, 5))
            bars = ax.bar(range(len(bottom_5_entidades)), bottom_5_entidades.values, color=COLORES[0])
            ax.set_xticks(range(len(bottom_5_entidades)))
            ax.set_xticklabels(bottom_5_entidades.index, rotation=45, ha='right')
            ax.set_ylabel('Total de donaciones registradas', fontweight='bold', color='black')
            ax.set_title('Las 5 entidades con menos donaciones', fontweight='bold', color='black')
            ax.tick_params(colors='black')
            ax.grid(axis='y', alpha=0.3)
            
            for bar, value in zip(bars, bottom_5_entidades.values):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       str(value), ha='center', va='bottom', fontweight='bold')
            
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()
        
        with col2:
            st.subheader("Tipo de donante por entidad (Top 10)")
            
            df_top10 = df_geo[df_geo['ENTIDAD_FEDERATIVA'].isin(top_10_entidades.index)]
            
            proporcion = df_top10.groupby(['ENTIDAD_FEDERATIVA', 'TIPO_DONANTE']).size().unstack(fill_value=0)
            proporcion_norm = proporcion.div(proporcion.sum(axis=1), axis=0)
            
            fig, ax = plt.subplots(figsize=(8, 5))
            proporcion_norm.plot(kind='barh', stacked=True, ax=ax, color=COLORES)
            ax.set_xlabel('Proporción (0.0 = 0%, 1.0 = 100%)', fontweight='bold', color='black')
            ax.set_ylabel('Entidad federativa', fontweight='bold', color='black')
            ax.set_title('Proporción de tipo de donante en las top 10 entidades', 
                        fontweight='bold', color='black')
            ax.tick_params(colors='black')
            legend = ax.legend(title='Tipo de donante', bbox_to_anchor=(1.05, 1), loc='upper left')
            plt.setp(legend.get_texts(), color='black')
            plt.setp(legend.get_title(), color='black')
            ax.grid(axis='x', alpha=0.3)
            
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()
    
    # ========================================
    # TAB 3: INSTITUCIONES
    # ========================================
    with tab3:
        st.header("Análisis por instituciones")
        
        st.subheader("Top 10 instituciones por número de donaciones")
        
        top_instituciones = df_filtrado['INSTITUCION'].value_counts().head(10)
        
        fig, ax = plt.subplots(figsize=(12, 8))
        bars = ax.barh(range(len(top_instituciones)), top_instituciones.values, color=COLORES[0])
        ax.set_yticks(range(len(top_instituciones)))
        ax.set_yticklabels(top_instituciones.index)
        ax.invert_yaxis()
        ax.set_xlabel('Total de donaciones registradas', fontweight='bold', fontsize=12, color='black')
        ax.set_title('Top 10 instituciones por número de donaciones', 
                    fontweight='bold', fontsize=14, color='black')
        ax.tick_params(colors='black')
        ax.grid(axis='x', alpha=0.3)
        
        for i, (bar, value) in enumerate(zip(bars, top_instituciones.values)):
            ax.text(value + 100, i, str(value), va='center', fontweight='bold')
        
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
        
        # Comparación IMSS vs PRIVADO
        st.subheader("Comparación: IMSS vs. PRIVADO")
        
        df_comparacion = df_filtrado[df_filtrado['INSTITUCION'].isin(['IMSS', 'PRIVADO'])]
        
        col1, col2 = st.columns(2)
        
        with col1:
            edad_por_inst = df_comparacion.groupby('INSTITUCION')['EDAD_ANIOS'].mean()
            
            fig, ax = plt.subplots(figsize=(6, 5))
            bars = ax.bar(edad_por_inst.index, edad_por_inst.values, color=COLORES[0])
            ax.set_ylabel('Edad promedio (Años)', fontweight='bold', fontsize=12, color='black')
            ax.set_xlabel('Institución', fontweight='bold', fontsize=12, color='black')
            ax.set_title('Edad promedio de donantes: IMSS vs. PRIVADO', 
                        fontweight='bold', fontsize=13, color='black')
            ax.tick_params(colors='black')
            ax.grid(axis='y', alpha=0.3)
            
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.1f}', ha='center', va='bottom', fontweight='bold', fontsize=12)
            
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()
        
        with col2:
            st.metric("IMSS - Edad promedio", f"{edad_por_inst['IMSS']:.1f} años")
            st.metric("PRIVADO - Edad promedio", f"{edad_por_inst['PRIVADO']:.1f} años")
            diferencia = edad_por_inst['IMSS'] - edad_por_inst['PRIVADO']
            st.metric("Diferencia", f"{diferencia:.1f} años", 
                     delta="IMSS es mayor" if diferencia > 0 else "PRIVADO es mayor")
    
    # ========================================
    # TAB 4: HIPÓTESIS
    # ========================================
    with tab4:
        st.header("Validación de hipótesis")
        
        # ==========================================
        # HIPÓTESIS 1: Muerte Encefálica vs. Paro Cardiorrespiratorio
        # Pregunta: ¿La muerte encefálica permite procurar más órganos que el paro cardiorrespiratorio?
        # ==========================================
        st.subheader("H1: Muerte encefálica vs. paro cardiorrespiratorio")
        
        # Filtrar solo las dos causas de muerte a comparar
        df_h1 = df_filtrado[
            (df_filtrado['CAUSA_MUERTE'].isin(['MUERTE ENCEFÁLICA', 'PARO CARDIORESPIRATORIO'])) &
            (df_filtrado['RANGO_EDAD'].notna())
        ]
        
        fig, ax = plt.subplots(figsize=(12, 6))
        sns.barplot(
            data=df_h1,
            x='RANGO_EDAD',
            y='TOTAL_ORGANOS',
            hue='CAUSA_MUERTE',
            estimator=np.mean,
            errorbar=('ci', 95),
            palette=COLORES,
            ax=ax
        )
        ax.set_title('Promedio de órganos donados: Muerte Encefálica vs. Paro Cardiorrespiratorio',
                    fontweight='bold', fontsize=14, color='black')
        ax.set_xlabel('Rango de edad del donante', fontweight='bold', color='black')
        ax.set_ylabel('Promedio de órganos/tejidos donados', fontweight='bold', color='black')
        ax.tick_params(colors='black')
        legend = ax.legend(title='Causa de muerte', loc='upper right')
        plt.setp(legend.get_texts(), color='black')
        plt.setp(legend.get_title(), color='black')
        plt.xticks(rotation=15, ha='right')
        
        for container in ax.containers:
            ax.bar_label(container, fmt='%.2f', padding=3)
        
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
        
        st.success("✅ **Conclusión:** Hipótesis TOTALMENTE VALIDADA. La muerte encefálica permite procurar, en promedio, el doble (o más) de órganos que el paro cardiorrespiratorio en TODOS los rangos de edad. El pico se alcanza en el rango 19-30 años (Adulto Joven) con muerte encefálica: 4.05 órganos por donación.")
        
        # ==========================================
        # HIPÓTESIS 2: Donación Multi-Órgano por Edad e Institución
        # Pregunta: ¿El éxito de donación multi-órgano (3+ órganos) está correlacionado
        # con edad menor a 50 años y el tipo de institución (IMSS, ISSSTE, PRIVADO)?
        # ==========================================
        st.subheader("H2: Donación multi-órgano por edad e institución")
        
        # Filtrar por las 3 instituciones principales
        df_h2 = df_filtrado[df_filtrado['INSTITUCION'].isin(['IMSS', 'ISSSTE', 'PRIVADO'])]
        df_h2['RANGO_EDAD_H1'] = pd.cut(df_h2['EDAD_ANIOS'], bins=[0, 50, 150], labels=['Menor a 50', '50 o más'])
        
        tasa_multiorgano = df_h2.groupby(['INSTITUCION', 'RANGO_EDAD_H1'])['ES_MULTIORGANO'].apply(
            lambda x: (x.sum() / len(x)) * 100
        ).reset_index()
        tasa_multiorgano.columns = ['INSTITUCION', 'RANGO_EDAD_H1', 'TASA']
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Preparar datos para gráfica de barras agrupadas
        instituciones = tasa_multiorgano['INSTITUCION'].unique()
        rangos = tasa_multiorgano['RANGO_EDAD_H1'].unique()
        x = np.arange(len(instituciones))
        width = 0.35  # Ancho de cada barra
        
        # Graficar una barra por cada rango de edad
        for i, rango in enumerate(rangos):
            data = tasa_multiorgano[tasa_multiorgano['RANGO_EDAD_H1'] == rango]
            ax.bar(x + i*width, data['TASA'], width, label=rango, color=COLORES[i])
        
        ax.set_xlabel('Institución', fontweight='bold', fontsize=12, color='black')
        ax.set_ylabel('Tasa de éxito (porcentaje)', fontweight='bold', fontsize=12, color='black')
        ax.set_title('Tasa de donación multi-órgano (3+) por institución y edad', 
                    fontweight='bold', fontsize=14, color='black')
        ax.set_xticks(x + width / 2)
        ax.set_xticklabels(instituciones)
        ax.tick_params(colors='black')
        legend = ax.legend(title='RANGO_EDAD_H1', loc='upper right')
        plt.setp(legend.get_texts(), color='black')
        plt.setp(legend.get_title(), color='black')
        ax.grid(axis='y', alpha=0.3)
        
        # Añadir valores
        for container in ax.containers:
            ax.bar_label(container, fmt='%.1f%%', padding=3)
        
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
        
        st.warning("⚠️ **Conclusión:** Hipótesis VALIDADA PARCIALMENTE. El factor institución SÍ está correlacionado con la tasa de donación multi-órgano (ISSSTE tiene la más alta: 16.5% en mayores de 50 años). Sin embargo, el factor edad es RECHAZADO: en 2 de 3 instituciones principales (ISSSTE y PRIVADO), la tasa de éxito es MAYOR en donantes de 50+ años, contrario a lo hipotetizado.")
        
        # ==========================================
        # HIPÓTESIS 3: Tendencia Mensual en Periodos Vacacionales
        # Pregunta: ¿La muerte encefálica muestra incremento significativo durante
        # periodos vacacionales (diciembre y verano) comparado con otras causas?
        # ==========================================
        st.subheader("H3: Tendencia mensual de muerte encefálica en periodos vacacionales")
        
        # Filtrar las dos causas principales para comparación
        df_h3 = df_filtrado[df_filtrado['CAUSA_MUERTE'].isin(['MUERTE ENCEFÁLICA', 'PARO CARDIORESPIRATORIO'])].copy()
        
        # Contar donaciones por mes y causa
        df_h3_conteo = df_h3.groupby(['MES', 'CAUSA_MUERTE']).size().reset_index(name='CONTEO')
        
        # Crear el gráfico de líneas
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Usar seaborn lineplot con los datos pre-contados
        sns.lineplot(
            data=df_h3_conteo,
            x='MES',
            y='CONTEO',
            hue='CAUSA_MUERTE',
            marker='o',
            linewidth=2.5,
            palette=COLORES[:2],
            ax=ax
        )
        
        ax.set_xlabel('Mes del año', fontweight='bold', fontsize=12, color='black')
        ax.set_ylabel('Total de donaciones registradas', fontweight='bold', fontsize=12, color='black')
        ax.set_title('Tendencia mensual: Muerte Encefálica vs. Paro Cardiorrespiratorio', 
                    fontweight='bold', fontsize=14, color='black')
        ax.set_xticks(range(1, 13))
        ax.set_xticklabels(['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 
                           'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'])
        ax.tick_params(colors='black')
        ax.grid(axis='y', alpha=0.3)
        legend = ax.legend(loc='upper right')
        plt.setp(legend.get_texts(), color='black')
        plt.setp(legend.get_title(), color='black')
        
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
        
        st.error("❌ **Conclusión:** Hipótesis RECHAZADA. Muerte encefálica NO muestra incremento en periodos vacacionales (diciembre es su punto más bajo). Además, ambas causas siguen un patrón estacional casi idéntico con pico en marzo y baja en diciembre, lo que sugiere que factores externos (no la causa de muerte) influyen en las donaciones.")
    
    # ========================================
    # FOOTER
    # ========================================
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p><strong>Proyecto Final - Introducción a Ciencia de Datos</strong></p>
        <p>Dashboard Interactivo | Análisis de Donación de Órganos en México</p>
        <p>Autor: Jonathan Araiza Guzmán | Datos: CENATRA</p>
        <p style='font-size: 0.85rem; color: #888;'>Noviembre 2025</p>
    </div>
    """, unsafe_allow_html=True)

except FileNotFoundError:
    st.error("⚠️ No se encontró el archivo 'data/donantes_organos_limpio.csv'. Por favor, verifica que el archivo existe en la carpeta 'data'.")
except Exception as e:
    st.error(f"❌ Error al cargar los datos: {str(e)}")
    st.info("Asegúrate de que el archivo CSV está en la ubicación correcta y tiene el formato esperado.")
