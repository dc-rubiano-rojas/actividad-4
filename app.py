from dash import Dash, html, dcc
import plotly.express as px
import pandas as pd
import requests

# Leer archivos de Excel
archivo = 'Anexo1.NoFetal2019_CE_15-03-23.xlsx'
df = pd.read_excel(archivo, engine='openpyxl')

archivo_codigos_muertes = 'Anexo2.CodigosDeMuerte_CE_15-03-23.xlsx'
df_codigos = pd.read_excel(archivo_codigos_muertes)

archivo_nombres = 'Anexo3.Divipola_CE_15-03-23.xlsx'
df_codigos_departmentos_municipios = pd.read_excel(
    archivo_nombres, engine='openpyxl'
)

# =======================
# 1 - Mapa: Muertes por departamento
# =======================
muertes_por_departamento = (
    df.groupby('COD_DEPARTAMENTO')
    .size()
    .reset_index(name='MUERTES')
)
muertes_por_departamento['COD_DEP'] = (
    muertes_por_departamento['COD_DEPARTAMENTO']
    .astype(str)
    .str.zfill(2)
)

muertes_por_departamento = muertes_por_departamento.merge(
    df_codigos_departmentos_municipios[
        ['COD_DEPARTAMENTO', 'DEPARTAMENTO']
    ],
    on='COD_DEPARTAMENTO',
    how='left'
)

# GeoJSON para el mapa
url_geojson = (
    "https://gist.githubusercontent.com/john-guerra/"
    "43c7656821069d00dcbc/raw/be6a6e239cd5b5b803c6e7c2ec405b793a9064dd/"
    "Colombia.geo.json"
)
geojson = requests.get(url_geojson).json()

# =====================
# 2 - Línea: Muertes por mes
# =====================
muertes_por_mes = df.groupby('MES').size().reset_index(name='MUERTES')

# Diccionario para nombres de meses
nombres_meses = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}
muertes_por_mes['NOMBRE_MES'] = muertes_por_mes['MES'].map(nombres_meses)

# Ordenar meses para graficar en orden cronológico
muertes_por_mes = muertes_por_mes.sort_values(by='MES')

# =======================================
# 3 - Barras: Top 5 municipios con más homicidios
# =======================================
muertes_por_municipio = (
    df.groupby(['COD_DEPARTAMENTO', 'COD_MUNICIPIO'])
    .size()
    .reset_index(name='MUERTES')
)

top5_municipios_muertes = (
    muertes_por_municipio
    .sort_values(by='MUERTES', ascending=False)
    .head(5)
)

top5_municipios_muertes['COD_DEPARTAMENTO'] = (
    top5_municipios_muertes['COD_DEPARTAMENTO'].astype(str).str.zfill(2)
)
top5_municipios_muertes['COD_MUNICIPIO'] = (
    top5_municipios_muertes['COD_MUNICIPIO'].astype(str).str.zfill(3)
)
top5_municipios_muertes['COD_COMPLETO'] = (
    top5_municipios_muertes['COD_DEPARTAMENTO'] +
    top5_municipios_muertes['COD_MUNICIPIO']
)

df_codigos_departmentos_municipios['COD_DEPARTAMENTO'] = (
    df_codigos_departmentos_municipios['COD_DEPARTAMENTO'].astype(str).str.zfill(2)
)
df_codigos_departmentos_municipios['COD_MUNICIPIO'] = (
    df_codigos_departmentos_municipios['COD_MUNICIPIO'].astype(str).str.zfill(3)
)
df_codigos_departmentos_municipios['COD_COMPLETO'] = (
    df_codigos_departmentos_municipios['COD_DEPARTAMENTO'] +
    df_codigos_departmentos_municipios['COD_MUNICIPIO']
)

top5_municipios_con_nombre = top5_municipios_muertes.merge(
    df_codigos_departmentos_municipios[['COD_COMPLETO', 'MUNICIPIO']],
    on='COD_COMPLETO',
    how='left'
)

# =================================================
# 4 - Circular: 10 ciudades con menor índice de mortalidad
# =================================================
muertes_por_municipio = (
    df.groupby(['COD_DEPARTAMENTO', 'COD_MUNICIPIO'])
    .size()
    .reset_index(name='MUERTES')
)

muertes_por_municipio['COD_DEPARTAMENTO'] = (
    muertes_por_municipio['COD_DEPARTAMENTO'].astype(str).str.zfill(2)
)
muertes_por_municipio['COD_MUNICIPIO'] = (
    muertes_por_municipio['COD_MUNICIPIO'].astype(str).str.zfill(3)
)
muertes_por_municipio['COD_COMPLETO'] = (
    muertes_por_municipio['COD_DEPARTAMENTO'] +
    muertes_por_municipio['COD_MUNICIPIO']
)

df_codigos_departmentos_municipios['COD_DEPARTAMENTO'] = (
    df_codigos_departmentos_municipios['COD_DEPARTAMENTO'].astype(str).str.zfill(2)
)
df_codigos_departmentos_municipios['COD_MUNICIPIO'] = (
    df_codigos_departmentos_municipios['COD_MUNICIPIO'].astype(str).str.zfill(3)
)
df_codigos_departmentos_municipios['COD_COMPLETO'] = (
    df_codigos_departmentos_municipios['COD_DEPARTAMENTO'] +
    df_codigos_departmentos_municipios['COD_MUNICIPIO']
)

muertes_con_nombre = muertes_por_municipio.merge(
    df_codigos_departmentos_municipios[['COD_COMPLETO', 'MUNICIPIO']],
    on='COD_COMPLETO',
    how='left'
)

# Eliminar municipios sin nombre
muertes_con_nombre = muertes_con_nombre.dropna(subset=['MUNICIPIO'])

menor10_municipios = (
    muertes_con_nombre.sort_values(by='MUERTES', ascending=True)
    .head(10)
)

# =====================
# App Dash
# =====================
app = Dash(__name__)

app.layout = html.Div([
    html.H1(
        "Universidad de la Salle",
        style={'textAlign': 'center'}
    ),

    html.H2(
        "Distribución de muertes por departamento en Colombia (2019)",
        style={'textAlign': 'center'}
    ),
    dcc.Graph(
        id='mapa-muertes',
        figure=px.choropleth(
            muertes_por_departamento,
            geojson=geojson,
            locations='COD_DEP',
            color='MUERTES',
            hover_name='DEPARTAMENTO',
            color_continuous_scale='Reds',
            featureidkey='properties.DPTO',
            labels={'MUERTES': 'Muertes', 'DEPARTAMENTO': 'Departamento'},
            title='Mapa: Total de muertes por departamento'
        ).update_geos(fitbounds="locations", visible=False)
        .update_layout(margin={"r": 0, "t": 50, "l": 0, "b": 0})
    ),

    html.H2(
        "Variación mensual de muertes en Colombia (2019)",
        style={'textAlign': 'center'}
    ),
    dcc.Graph(
        id='lineas-mensuales',
        figure=px.line(
            muertes_por_mes,
            x='NOMBRE_MES',
            y='MUERTES',
            markers=True,
            labels={'NOMBRE_MES': 'Mes', 'MUERTES': 'Número de muertes'},
            title='Total de muertes por mes en Colombia - 2019'
        )
    ),

    html.H2(
        "Top 5 municipios con más homicidios (2019)",
        style={'textAlign': 'center'}
    ),
    dcc.Graph(
        id='barras-homicidios',
        figure=px.bar(
            top5_municipios_con_nombre,
            x='MUNICIPIO',
            y='MUERTES',
            labels={'MUNICIPIO': 'Municipio', 'HOMICIDIOS': 'Número de homicidios'},
            title='Top 5 municipios con más homicidios'
        )
    ),

    html.H2(
        "10 ciudades con menor índice de mortalidad (2019)",
        style={'textAlign': 'center'}
    ),
    dcc.Graph(
        id='pie-mortalidad-baja',
        figure=px.pie(
            menor10_municipios,
            names='MUNICIPIO',
            values='MUERTES',
            title='10 ciudades con menor índice de mortalidad',
            labels={'MUNICIPIO': 'Municipio', 'MUERTES': 'Número de muertes'}
        )
    ),
])

if __name__ == '__main__':
    app.run_server(debug=True)
