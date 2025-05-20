from dash import Dash, html, dcc, dash_table
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

# =======================
# 5 - Tabla: Primeras 10 filas del dataset
# =======================
tabla_head = dash_table.DataTable(
    id='tabla-head',
    columns=[{'name': col, 'id': col} for col in df.columns],
    data=df.head(10).to_dict('records'),
    page_size=10,
    style_table={'overflowX': 'auto'}
)

# =======================
# 6 - Histograma: Distribución de grupos de edad
# =======================
hist_edad = px.histogram(
    df,
    x='GRUPO_EDAD1',
    nbins=10,
    labels={'GRUPO_EDAD1': 'Grupo de edad', 'count': 'Frecuencia'},
    title='Distribución de grupos de edad'
)

# =======================
# 7 - Barras: Muertes por manera de muerte
# =======================
manera_counts = df['MANERA_MUERTE'].value_counts().reset_index(name='MUERTES')
manera_counts.rename(columns={'index': 'MANERA_MUERTE'}, inplace=True)

barras_manera = px.bar(
    manera_counts,
    x='MANERA_MUERTE',
    y='MUERTES',
    labels={'MANERA_MUERTE': 'Manera de muerte', 'MUERTES': 'Número de muertes'},
    title='Muertes por manera de muerte'
)

# =====================
# App Dash
# =====================
app = Dash(__name__)
server = app.server 

app.layout = html.Div(
    style={
        'backgroundColor': '#f5f5f5',  # Color de fondo general
        'padding': '20px',
        'margin': '20px',
        'borderRadius': '10px',
        'fontFamily': 'Arial, sans-serif'
    },
    children=[
        html.H1('Universidad de la Salle', style={'textAlign': 'center', 'color': '#333'}),
        html.H2('Maestría en IA', style={'textAlign': 'center', 'color': '#444'}),
        html.H3('Daniel Rubiano Rojas', style={'textAlign': 'center', 'color': '#666'}),
        html.H3('Nicolás Zuluaga Fontecha', style={'textAlign': 'center', 'color': '#666'}),

        html.H2(
            "Distribución de muertes por departamento en Colombia (2019)",
            style={'textAlign': 'center', 'marginTop': '40px'}
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

        html.H2("Variación mensual de muertes en Colombia", style={'textAlign': 'center', 'marginTop': '40px'}),
        dcc.Graph(id='lineas-mensuales', figure=px.line(
            muertes_por_mes,
            x='NOMBRE_MES',
            y='MUERTES',
            markers=True,
            labels={'NOMBRE_MES': 'Mes', 'MUERTES': 'Número de muertes'},
            title='Total de muertes por mes en Colombia - 2019'
        )),

        html.H2("Top 5 municipios con más homicidios", style={'textAlign': 'center', 'marginTop': '40px'}),
        dcc.Graph(id='barras-homicidios', figure=px.bar(
            top5_municipios_con_nombre,
            x='MUNICIPIO',
            y='MUERTES',
            labels={'MUNICIPIO': 'Municipio', 'HOMICIDIOS': 'Número de homicidios'},
            title='Top 5 municipios con más homicidios'
        )),

        html.H2("10 ciudades con menor índice de mortalidad", style={'textAlign': 'center', 'marginTop': '40px'}),
        dcc.Graph(id='pie-mortalidad-baja', figure=px.pie(
            menor10_municipios,
            names='MUNICIPIO',
            values='MUERTES',
            title='10 ciudades con menor índice de mortalidad',
            labels={'MUNICIPIO': 'Municipio', 'MUERTES': 'Número de muertes'}
        )),

        html.H2('Tabla: Primeras 10 filas del dataset', style={'textAlign': 'center', 'marginTop': '40px'}),
        tabla_head,

        html.H2('Histograma de distribución de grupos de edad', style={'textAlign': 'center', 'marginTop': '40px'}),
        dcc.Graph(id='histograma-edad', figure=hist_edad),

        html.H2('Muertes por manera de muerte', style={'textAlign': 'center', 'marginTop': '40px'}),
        dcc.Graph(id='barras-manera-muerte', figure=barras_manera),
        
        html.H3('Todos los derechos reservados', style={'textAlign': 'center', 'color': '#666'}),
    ]
)


if __name__ == '__main__':
    app.run_server(debug=True)
