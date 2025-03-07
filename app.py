import streamlit as st
import pandas as pd
import numpy as np
import folium
from folium.plugins import HeatMap
from streamlit_folium import folium_static

@st.cache_data
def get_data():
    df = pd.read_excel('Projeto organização biometano.xlsm')
    df = df[4:]
    df.columns = df.iloc[0]  # Primeira linha vira o nome das colunas
    df = df.drop(df.index[0])  # Remover a primeira linha, agora redundante
    df.columns = df.columns.str.replace('\n', ' ', regex=True)  # Remover quebra de linha
    df['POTENCIAL DE CO2 NO UPGRADING (tCO2/ano)'] = df['POTENCIAL DE CO2 NO UPGRADING (tCO2/ano)'].replace(0, np.nan)
    df['CAPACIDADE  (Nm³/d)'] = pd.to_numeric(df['CAPACIDADE  (Nm³/d)'], errors='coerce')
    df = df.dropna(how='all')
    return df

st.set_page_config(page_title="Biometano", layout="wide")

data = get_data()

with st.sidebar:
    st.title('Biometano')
    st.header('Filtros')

    # Filtros
    estado = st.multiselect('Estado', data['UF'].unique(),placeholder='Selecione os estados')
    municipio = st.multiselect('Município', data['MUNICÍPIO'].unique(),placeholder='Selecione os municípios')	
    materia_prima = st.multiselect('Matéria Prima', data['MATÉRIA-PRIMA'].unique(),placeholder='Selecione a matéria prima')
    capacidade = st.slider('Capacidade', 
                           min_value=data['CAPACIDADE  (Nm³/d)'].min(),
                           max_value=data['CAPACIDADE  (Nm³/d)'].max(),
                           value=data['CAPACIDADE  (Nm³/d)'].max())

# Aplicar os filtros no DataFrame
filtered_data = data.copy()

# Filtrar por Estado
if estado:
    filtered_data = filtered_data[filtered_data['UF'].isin(estado)]

# Filtrar por Município
if municipio:
    filtered_data = filtered_data[filtered_data['MUNICÍPIO'].isin(municipio)]

# Filtrar por Matéria Prima
if materia_prima:
    filtered_data = filtered_data[filtered_data['MATÉRIA-PRIMA'].isin(materia_prima)]

# Filtrar por Capacidade
filtered_data = filtered_data[filtered_data['CAPACIDADE  (Nm³/d)'] <= capacidade]

# Exibir o DataFrame filtrado
st.dataframe(filtered_data)

# Dividir a tela entre o mapa e o heatmap
col_map, col_heatmap = st.columns([1, 1], gap="medium")  # Garantir que ambas as colunas tenham o mesmo tamanho

with col_map:

    _ , col_title_map , _ = st.columns([4, 10, 4])
    with col_title_map:
        st.subheader('Localizações das Empresas')

    # Verificar se há colunas de latitude e longitude no DataFrame filtrado
    if 'LATITUDE' in filtered_data.columns and 'LONGITUDE' in filtered_data.columns:
        # Filtrar as linhas que têm valores válidos de latitude e longitude
        map_data = filtered_data[['LATITUDE', 'LONGITUDE']].dropna()

        # Plotar o mapa com os locais das empresas
        if not map_data.empty:
            st.map(map_data)
        else:
            st.write("Não há dados de localização disponíveis para as empresas selecionadas.")
    else:
        st.write("As colunas de LATITUDE e LONGITUDE não foram encontradas no DataFrame.")

with col_heatmap:

    _ , col_title_heatmap , _ = st.columns([2, 10, 2])
    with col_title_heatmap:
        st.subheader('Heatmap do Potencial de CO2')

    # Verificar se há dados para o potencial de CO2
    if 'POTENCIAL DE CO2 NO UPGRADING (tCO2/ano)' in filtered_data.columns:
        heatmap_data = filtered_data[['LATITUDE', 'LONGITUDE', 'POTENCIAL DE CO2 NO UPGRADING (tCO2/ano)']].dropna()

        if not heatmap_data.empty:
            # Inicializar o mapa com folium
            m = folium.Map(location=[heatmap_data['LATITUDE'].mean(), heatmap_data['LONGITUDE'].mean()], zoom_start=5)

            # Preparar os dados para o HeatMap
            heat_data = [[row['LATITUDE'], row['LONGITUDE'], row['POTENCIAL DE CO2 NO UPGRADING (tCO2/ano)']] for index, row in heatmap_data.iterrows()]

            # Adicionar o HeatMap ao mapa
            HeatMap(heat_data, radius=15, max_zoom=13).add_to(m)

            # Exibir o mapa no Streamlit
            folium_static(m)
        else:
            st.write("Não há dados disponíveis para o heatmap.")
    else:
        st.write("A coluna de POTENCIAL DE CO2 NO UPGRADING (tCO2/ano) não foi encontrada.")
