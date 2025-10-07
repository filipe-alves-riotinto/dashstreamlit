import streamlit as st
import pandas as pd
from datetime import datetime
from dados.processamento import fichas_com_votos_e_fefc
import graficosBase


# Inicializar session state
if 'ano_selecionado' not in st.session_state:
    st.session_state.ano_selecionado = "2022"

if 'base_dados' not in st.session_state:
    st.session_state.base_dados = fichas_com_votos_e_fefc(st.session_state.ano_selecionado)

#@st.cache_data
def atualizar_dados(ano):
    """Atualiza os dados quando o ano muda"""
    st.session_state.ano_selecionado = ano
    st.session_state.base_dados = fichas_com_votos_e_fefc(ano)
    #st.rerun()

base = st.session_state.base_dados

### Configurações do Streamlit
st.set_page_config(layout='wide')
st.sidebar.markdown("## Filtros")

##FILTROS

#filtro UF
selecionar_uf = base['uf_cand'].unique().tolist()
filtro_uf = st.sidebar.multiselect(
    'Selecione as UFs',
    selecionar_uf,
    help="Selecione as UFs para filtrar os dados.",
    #default=selecionar_uf
)
base = base[base['uf_cand'].isin(filtro_uf)] if filtro_uf else base

#Partido
selecionar_partido = base['sg_partido'].unique().tolist()
filtro_partido = st.sidebar.multiselect(
    "Selecione os partidos",
    selecionar_partido,
    help="Selecione os partidos para filtrar os dados.",
    default = graficosBase.filtro_top_partido(base),
)


base = base[base['sg_partido'].isin(filtro_partido)] if filtro_partido else base
basemetric = base[['ds_eleicao', 'nm_cargo']]

#Resultado
opcoes_resultado = ["Eleito", "Não eleito"]
filto_resultado = st.sidebar.pills("Resultado", opcoes_resultado, selection_mode="single", default="Eleito")

if filto_resultado is not None:
    base = base[base['ds_eleicao'] == filto_resultado]

####Montar pagina
st.markdown("# GRAFICO DE DADOS DOS CANDIDATOS FEDERAIS! 🇧🇷")

# Montar Abas
DepFederal, DepEstadual = st.tabs(['Dep. Federal',  'Dep. Estadual'])

# Criar tabelas e gráficos para Deputado Federal
with DepFederal:
    options = ["Resumo", "2022", "2018", "2014"]
    selection = st.pills(
        "", 
        options, 
        label_visibility='collapsed', 
        selection_mode="single", 
        default=st.session_state.ano_selecionado,
        key='pills_ano',
        on_change=lambda: atualizar_dados(st.session_state.pills_ano)
    )

    st.markdown(f"## Deputado Federal - {selection}")
    
    #if selection == "2022":
    col1 , col2, col3 = st.columns(3)
    with col1:
        graficosBase.card_resultado(basemetric, filtro='Deputado Federal', texto='Eleito')
    with col2:
        graficosBase.card_resultado(basemetric, filtro='Deputado Federal', texto='Não eleito')
    with col3:
        graficosBase.card_resultado(basemetric, filtro='Deputado Federal', texto='Candidatos')
        
    #st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Gráfico de Partidos")
        graficosBase.grafico_barra(base, filtro='Deputado Federal')        
    with col2:
        st.markdown("### Gráfico de UF")
        graficosBase.grafico_linha_uf(base, filtro='Deputado Federal')

    #st.write("Tipo da coluna:", base["FEFC"].dtype)  # Deve ser int64
    #st.divider

    st.markdown("### Gráfico de valores por partido")
    col1, col2 = st.columns(2)
    with col1:
        graficosBase.grafico_valor_partido(base, filtro='Deputado Federal')
    with col2:
        graficosBase.grafico_pizza(base, filtro='Deputado Federal')
    graficosBase.tabela_dados(base, filtro='Deputado Federal')

    #assistente.assistente(base, filtro='Deputado Federal')
# Criar tabelas e gráficos para Deputado Estadual
with DepEstadual:   
    st.markdown("## Deputado Estadual")
 
    col1 , col2, col3 = st.columns(3)
    with col1:
        graficosBase.card_resultado(basemetric, filtro='Deputado Estadual', texto='Eleito')
    with col2:
        graficosBase.card_resultado(basemetric, filtro='Deputado Estadual', texto='Não eleito')
    with col3:
        graficosBase.card_resultado(basemetric, filtro='Deputado Estadual', texto='Candidatos')
    
    #st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Gráfico de Partidos")
        graficosBase.grafico_barra(base, filtro='Deputado Estadual')
    with col2:
        st.markdown("### Gráfico de UF")
        graficosBase.grafico_linha_uf(base, filtro='Deputado Estadual')

    #st.write("Tipo da coluna:", base["FEFC"].dtype)  # Deve ser int64
    #st.divider

    st.markdown("### Gráfico de valores por partido")
    col1, col2 = st.columns(2)
    with col1:
        graficosBase.grafico_valor_partido(base, filtro='Deputado Estadual')
    with col2:
        graficosBase.grafico_pizza(base, filtro='Deputado Estadual')
    graficosBase.tabela_dados(base, filtro='Deputado Estadual')

