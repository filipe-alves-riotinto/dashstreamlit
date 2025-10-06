import streamlit as st
import pandas as pd
from datetime import datetime
#import plotly.express as px
#import matplotlib.colors as mcolors
#import random
import AbragenciaFederal
#import assistente
import graficos



#Carregar dados
eleicao2022 = AbragenciaFederal.Eleicao2022.fichas_com_votos()
st.session_state["data"] = eleicao2022

### Configurações do Streamlit
st.set_page_config(layout='wide')
st.sidebar.markdown("## Filtros")

##FILTROS

#filtro UF
selecionar_uf = eleicao2022['uf_cand'].unique().tolist()
filtro_uf = st.sidebar.multiselect(
    'Selecione as UFs',
    selecionar_uf,
    help="Selecione as UFs para filtrar os dados.",
    #default=selecionar_uf
)
eleicao2022 = eleicao2022[eleicao2022['uf_cand'].isin(filtro_uf)] if filtro_uf else eleicao2022

#Partido
selecionar_partido = eleicao2022['sg_partido'].unique().tolist()
filtro_partido = st.sidebar.multiselect(
    "Selecione os partidos",
    selecionar_partido,
    help="Selecione os partidos para filtrar os dados.",
    default = graficos.filtro_top_partido(eleicao2022),
)


eleicao2022 = eleicao2022[eleicao2022['sg_partido'].isin(filtro_partido)] if filtro_partido else eleicao2022
eleicao2022metric = eleicao2022[['ds_eleicao', 'nm_cargo']]

#Resultado
opcoes_resultado = ["Eleito", "Não eleito"]
filto_resultado = st.sidebar.pills("Resultado", opcoes_resultado, selection_mode="single", default="Eleito")

if filto_resultado is not None:
    eleicao2022 = eleicao2022[eleicao2022['ds_eleicao'] == filto_resultado]

####Montar pagina
st.markdown("# GRAFICO DE DADOS DOS CANDIDATOS FEDERAIS! 🇧🇷")

# Montar Abas
Presidente, Governador, Senador, DepFederal, DepEstadual = st.tabs(['Presidente','Governador', 'Senador',  'Dep. Federal',  'Dep. Estadual'])

with Presidente:
    st.markdown("## Presidente")
    st.dataframe(eleicao2022[eleicao2022['nm_cargo'] == 'Presidente'])

with Governador:
    st.markdown("## Governador")
    #grafico_linha_uf(eleicao2022, filtro='Governador')
    #st.plotly_chart(dados, use_container_width=True)
    st.markdown("### Gráfico de valores por partido")
    graficos.grafico_valor_partido(eleicao2022, filtro='Governador')
    graficos.tabela_dados(eleicao2022, filtro='Governador')

with Senador:
    st.markdown("## Senador")
    st.dataframe(eleicao2022[eleicao2022['nm_cargo'] == 'Senador'])

# Criar tabelas e gráficos para Deputado Federal
with DepFederal:
    options = ["Resumo", "2022", "2018", "2014"]
    selection = st.pills("",options, label_visibility='collapsed', selection_mode="single", default= "2022")

    st.markdown(f"## Deputado Federal - {selection}")
 
    if selection == "2022":
        col1 , col2, col3 = st.columns(3)
        with col1:
            graficos.card_resultado(eleicao2022metric, filtro='Deputado Federal', texto='Eleito')
        with col2:
            graficos.card_resultado(eleicao2022metric, filtro='Deputado Federal', texto='Não eleito')
        with col3:
            graficos.card_resultado(eleicao2022metric, filtro='Deputado Federal', texto='Candidatos')
        
        #st.divider()
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Gráfico de Partidos")
            graficos.grafico_barra(eleicao2022, filtro='Deputado Federal')        
        with col2:
            st.markdown("### Gráfico de UF")
            graficos.grafico_linha_uf(eleicao2022, filtro='Deputado Federal')

        #st.write("Tipo da coluna:", eleicao2022["FEFC"].dtype)  # Deve ser int64
        #st.divider

    st.markdown("### Gráfico de valores por partido")
    col1, col2 = st.columns(2)
    with col1:
        graficos.grafico_valor_partido(eleicao2022, filtro='Deputado Federal')
    with col2:
        graficos.grafico_pizza(eleicao2022, filtro='Deputado Federal')
    graficos.tabela_dados(eleicao2022, filtro='Deputado Federal')

    #assistente.assistente(eleicao2022, filtro='Deputado Federal')
# Criar tabelas e gráficos para Deputado Estadual
with DepEstadual:   
    st.markdown("## Deputado Estadual")
 
    col1 , col2, col3 = st.columns(3)
    with col1:
        graficos.card_resultado(eleicao2022metric, filtro='Deputado Estadual', texto='Eleito')
    with col2:
        graficos.card_resultado(eleicao2022metric, filtro='Deputado Estadual', texto='Não eleito')
    with col3:
        graficos.card_resultado(eleicao2022metric, filtro='Deputado Estadual', texto='Candidatos')
    
    #st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Gráfico de Partidos")
        graficos.grafico_barra(eleicao2022, filtro='Deputado Estadual')
    with col2:
        st.markdown("### Gráfico de UF")
        graficos.grafico_linha_uf(eleicao2022, filtro='Deputado Estadual')

    #st.write("Tipo da coluna:", eleicao2022["FEFC"].dtype)  # Deve ser int64
    #st.divider

    st.markdown("### Gráfico de valores por partido")
    col1, col2 = st.columns(2)
    with col1:
        graficos.grafico_valor_partido(eleicao2022, filtro='Deputado Estadual')
    with col2:
        graficos.grafico_pizza(eleicao2022, filtro='Deputado Estadual')
    graficos.tabela_dados(eleicao2022, filtro='Deputado Estadual')

