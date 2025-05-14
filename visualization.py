import pandas as pd
import numpy as np
import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go
from datetime import datetime, timedelta
import streamlit as st
from data_utils import procesar_fecha, verificar_completado_por_fecha


def crear_gantt(df):
    """Crea un diagrama de Gantt a partir de los registros."""
    try:
        # Preparar los datos para el diagrama de Gantt
        gantt_data = []
        fecha_actual = datetime.now()

        for _, row in df.iterrows():
            try:
                # Verificar que las columnas existan
                if 'Cod' not in row or 'Nivel Información ' not in row:
                    continue

                cod = str(row['Cod'])
                nivel_info = str(row['Nivel Información '])[:30] + "..." if len(
                    str(row['Nivel Información '])) > 30 else str(row['Nivel Información '])

                # Usar nivel de información en lugar de entidad
                etiqueta = f"{cod} - {nivel_info}"

                # Hito 1: Acuerdo de compromiso
                if 'Suscripción acuerdo de compromiso' in row:
                    fecha_acuerdo = procesar_fecha(row['Suscripción acuerdo de compromiso'])
                    if fecha_acuerdo is not None and pd.notna(fecha_acuerdo):
                        fecha_fin_acuerdo = fecha_acuerdo + timedelta(days=7)  # Asumimos 1 semana de duración
                        gantt_data.append(dict(
                            Task=etiqueta,
                            Start=fecha_acuerdo,
                            Finish=fecha_fin_acuerdo,
                            Resource='Acuerdo de compromiso'
                        ))

                # Hito 2: Análisis y cronograma
                if 'Análisis y cronograma (fecha programada)' in row:
                    fecha_analisis = procesar_fecha(row['Análisis y cronograma (fecha programada)'])
                    if fecha_analisis is not None and pd.notna(fecha_analisis):
                        fecha_fin_analisis = fecha_analisis + timedelta(days=14)  # Asumimos 2 semanas
                        gantt_data.append(dict(
                            Task=etiqueta,
                            Start=fecha_analisis,
                            Finish=fecha_fin_analisis,
                            Resource='Análisis y cronograma'
                        ))

                # Hito 3: Estándares
                if 'Estándares (fecha programada)' in row:
                    fecha_estandares = procesar_fecha(row['Estándares (fecha programada)'])
                    if fecha_estandares is not None and pd.notna(fecha_estandares):
                        fecha_fin_estandares = fecha_estandares + timedelta(days=14)  # Asumimos 2 semanas
                        gantt_data.append(dict(
                            Task=etiqueta,
                            Start=fecha_estandares,
                            Finish=fecha_fin_estandares,
                            Resource='Estándares'
                        ))

                # Hito 4: Publicación
                if 'Fecha de publicación programada' in row:
                    fecha_publicacion = procesar_fecha(row['Fecha de publicación programada'])
                    if fecha_publicacion is not None and pd.notna(fecha_publicacion):
                        fecha_fin_publicacion = fecha_publicacion + timedelta(days=7)  # Asumimos 1 semana
                        gantt_data.append(dict(
                            Task=etiqueta,
                            Start=fecha_publicacion,
                            Finish=fecha_fin_publicacion,
                            Resource='Publicación'
                        ))
            except Exception as e:
                st.warning(f"Error al procesar registro para Gantt: {e}")
                continue

        # Crear el dataframe para el diagrama de Gantt
        gantt_df = pd.DataFrame(gantt_data)

        if not gantt_df.empty:
            # Colores para cada tipo de hito
            colors = {
                'Acuerdo de compromiso': '#1E40AF',
                'Análisis y cronograma': '#047857',
                'Estándares': '#B45309',
                'Publicación': '#BE185D'
            }

            # Crear el diagrama de Gantt
            fig = ff.create_gantt(
                gantt_df,
                colors=colors,
                index_col='Resource',
                show_colorbar=True,
                group_tasks=True,
                showgrid_x=True,
                showgrid_y=True,
                title='Cronograma de Hitos por Nivel de Información'
            )

            # Personalizar el diagrama
            fig.update_layout(
                height=600,
                margin=dict(l=50, r=50, t=80, b=50),
                font=dict(size=12),
                title=dict(
                    text='Cronograma de Hitos por Nivel de Información',
                    x=0.5,
                    font=dict(size=20, color='#2E3440')
                )
            )

            # Agregar línea vertical para la fecha actual
            fig.add_shape(
                type="line",
                x0=fecha_actual,
                y0=0,
                x1=fecha_actual,
                y1=1,
                yref="paper",
                line=dict(
                    color="red",
                    width=2,
                    dash="dash",
                ),
                name="Fecha Actual"
            )

            # Agregar anotación para la fecha actual
            fig.add_annotation(
                x=fecha_actual,
                y=1.05,
                yref="paper",
                text=f"Fecha Actual: {fecha_actual.strftime('%d/%m/%Y')}",
                showarrow=False,
                font=dict(
                    family="Arial",
                    size=12,
                    color="red"
                ),
                bgcolor="rgba(255, 255, 255, 0.8)",
                bordercolor="red",
                borderwidth=1
            )

            return fig
        else:
            return None
    except Exception as e:
        st.error(f"Error al crear el diagrama de Gantt: {e}")
        return None


def comparar_avance_metas(df, metas_nuevas_df, metas_actualizar_df):
    """Compara el avance actual con las metas establecidas."""
    try:
        # Obtener la fecha actual
        fecha_actual = datetime.now()

        # Encontrar la meta más cercana a la fecha actual
        fechas_metas = metas_nuevas_df.index
        fecha_meta_cercana = min(fechas_metas, key=lambda x: abs(x - fecha_actual))

        # Obtener los valores de las metas para esa fecha
        metas_nuevas_actual = metas_nuevas_df.loc[fecha_meta_cercana]
        metas_actualizar_actual = metas_actualizar_df.loc[fecha_meta_cercana]

        # Contar registros completados por hito y tipo (de manera segura)
        # Verificar si la columna TipoDato existe
        if 'TipoDato' not in df.columns:
            # Crear columnas necesarias si no existen
            df['TipoDato'] = 'No especificado'
            df['Acuerdo de compromiso'] = ''
            df['Análisis y cronograma'] = ''
            df['Estándares'] = ''
            df['Publicación'] = ''

        # Filtrar registros por tipo, asegurando que TipoDato exista y no sea NaN
        df['TipoDato'] = df['TipoDato'].fillna('').astype(str)
        registros_nuevos = df[df['TipoDato'].str.upper() == 'NUEVO']
        registros_actualizar = df[df['TipoDato'].str.upper() == 'ACTUALIZAR']

        # Para registros nuevos
        # Asegurar que la columna 'Acuerdo de compromiso' existe y no es NaN
        if 'Acuerdo de compromiso' not in df.columns:
            df['Acuerdo de compromiso'] = ''
        df['Acuerdo de compromiso'] = df['Acuerdo de compromiso'].fillna('').astype(str)
        
        completados_nuevos = {
            'Acuerdo de compromiso': len(registros_nuevos[registros_nuevos['Acuerdo de compromiso'].str.upper().isin(
                ['SI', 'SÍ', 'S', 'YES', 'Y', 'COMPLETO'])]),
            'Análisis y cronograma': contar_registros_completados_por_fecha(
                registros_nuevos, 'Análisis y cronograma (fecha programada)', 'Análisis y cronograma'),
            'Estándares': contar_registros_completados_por_fecha(
                registros_nuevos, 'Estándares (fecha programada)', 'Estándares'),
            'Publicación': contar_registros_completados_por_fecha(
                registros_nuevos, 'Fecha de publicación programada', 'Publicación')
        }

        # Para registros a actualizar
        completados_actualizar = {
            'Acuerdo de compromiso': len(registros_actualizar[
                                             registros_actualizar['Acuerdo de compromiso'].str.upper().isin(
                                                 ['SI', 'SÍ', 'S', 'YES', 'Y', 'COMPLETO'])]),
            'Análisis y cronograma': contar_registros_completados_por_fecha(
                registros_actualizar, 'Análisis y cronograma (fecha programada)', 'Análisis y cronograma'),
            'Estándares': contar_registros_completados_por_fecha(
                registros_actualizar, 'Estándares (fecha programada)', 'Estándares'),
            'Publicación': contar_registros_completados_por_fecha(
                registros_actualizar, 'Fecha de publicación programada', 'Publicación')
        }

        # Crear dataframes para la comparación
        comparacion_nuevos = pd.DataFrame({
            'Completados': completados_nuevos,
            'Meta': metas_nuevas_actual
        })

        comparacion_actualizar = pd.DataFrame({
            'Completados': completados_actualizar,
            'Meta': metas_actualizar_actual
        })

        # Calcular porcentajes de cumplimiento (manejando divisiones por cero)
        comparacion_nuevos['Porcentaje'] = comparacion_nuevos.apply(
            lambda row: (row['Completados'] / row['Meta'] * 100) if row['Meta'] > 0 else 0, 
            axis=1
        ).fillna(0).round(2)
        
        comparacion_actualizar['Porcentaje'] = comparacion_actualizar.apply(
            lambda row: (row['Completados'] / row['Meta'] * 100) if row['Meta'] > 0 else 0, 
            axis=1
        ).fillna(0).round(2)

        return comparacion_nuevos, comparacion_actualizar, fecha_meta_cercana
    except Exception as e:
        st.error(f"Error al comparar avance con metas: {e}")
        # Crear DataFrames de respaldo
        fecha_meta_cercana = datetime.now()

        completados_nuevos = {'Acuerdo de compromiso': 0, 'Análisis y cronograma': 0, 'Estándares': 0,
                              'Publicación': 0}
        completados_actualizar = {'Acuerdo de compromiso': 0, 'Análisis y cronograma': 0, 'Estándares': 0,
                                  'Publicación': 0}

        metas_nuevas_actual = pd.Series(
            {'Acuerdo de compromiso': 0, 'Análisis y cronograma': 0, 'Estándares': 0, 'Publicación': 0})
        metas_actualizar_actual = pd.Series(
            {'Acuerdo de compromiso': 0, 'Análisis y cronograma': 0, 'Estándares': 0, 'Publicación': 0})

        comparacion_nuevos = pd.DataFrame({
            'Completados': completados_nuevos,
            'Meta': metas_nuevas_actual,
            'Porcentaje': [0, 0, 0, 0]
        })

        comparacion_actualizar = pd.DataFrame({
            'Completados': completados_actualizar,
            'Meta': metas_actualizar_actual,
            'Porcentaje': [0, 0, 0, 0]
        })

        return comparacion_nuevos, comparacion_actualizar, fecha_meta_cercana


def contar_registros_completados_por_fecha(df, columna_fecha_programada, columna_fecha_completado):
    """
    Cuenta los registros que tienen una fecha de completado o cuya fecha programada ya pasó.
    """
    count = 0
    for _, row in df.iterrows():
        if columna_fecha_programada in row and row[columna_fecha_programada]:
            fecha_programada = row[columna_fecha_programada]

            # Verificar si hay una fecha de completado
            fecha_completado = None
            if columna_fecha_completado in row and row[columna_fecha_completado]:
                # Intentar procesar como fecha primero
                fecha_completado = procesar_fecha(row[columna_fecha_completado])
                # Si no es una fecha, verificar si es un valor booleano positivo
                if fecha_completado is None and str(row[columna_fecha_completado]).strip().upper() in ['SI', 'SÍ',
                                                                                                       'S', 'YES',
                                                                                                       'Y',
                                                                                                       'COMPLETO']:
                    fecha_completado = datetime.now()  # Usar fecha actual como completado

            if verificar_completado_por_fecha(fecha_programada, fecha_completado):
                count += 1

    return count