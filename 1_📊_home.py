import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import matplotlib.colors as mcolors
import random
import AbragenciaFederal

#Carregar dados
eleicao2022 = AbragenciaFederal.fichas_com_votos()
st.session_state["data"] = eleicao2022

### Configurações do Streamlit
st.set_page_config(layout='wide')
st.sidebar.markdown("## Filtros")



def cores_partidos():
    # Gerar cores aleatórias para os partidos
    cores = {}
    for partido in eleicao2022['sg_partido'].unique():
        if partido == 'PSDB':
            cores[partido] = 'blue'  # Definindo PSDB como azul
        elif partido == 'PT':
            cores[partido] = 'red'  # Definindo PT como vermelho
        else:
            # Gera uma cor RGB aleatória (excluindo tons muito claros para melhor visibilidade)
            rgb = [random.random() for _ in range(3)]  # 0.8 para evitar cores muito claras
            cores[partido] = mcolors.rgb2hex(rgb)  # Converte RGB para formato hexadecimal
    return cores

cores = cores_partidos()

def grafico_barra_partido(base, filtro):
    df_dados = base[base['nm_cargo'] == filtro]
    total_por_partido = df_dados.groupby(['sg_partido']).size().reset_index(name=f'Total {filtro} por Partido')

    fig_grafico_barra = px.bar(
        total_por_partido, 
        x='sg_partido', 
        y=f'Total {filtro} por Partido', 
        color='sg_partido',
        color_discrete_map=cores,
        labels={
            'sg_partido': 'Partido',
            f'Total {filtro} por Partido': f'Total {filtro} por Partido'
        },
        category_orders={"sg_partido": sorted(total_por_partido['sg_partido'].unique())}
    )
    fig_grafico_barra.update_layout(
        legend=dict(
            title='Partidos',
            orientation='h',
            yanchor='bottom',
            y= 1.0,
            xanchor='right',
            x=1
        ))
    fig_grafico_barra.update_traces(texttemplate='%{y}', textposition='outside')
    
    st.plotly_chart(fig_grafico_barra)

def grafico_linha_uf(base, filtro = None):
    ##TABELAS
    df_dados = base[base['nm_cargo'] == filtro]
    total_por_uf = df_dados.groupby(['uf_cand', 'sg_partido']).size().reset_index(name=f'Total {filtro} por UF')

    ## GRAFICOS
    fig_grafico_linha = px.line(
        total_por_uf, 
        x='uf_cand', 
        y=f'Total {filtro} por UF', 
        color='sg_partido',
        color_discrete_map=cores,
        markers=True,
        #title='Deputado Federal',
        labels={
            'uf_cand': 'UF',
            f'Total {filtro} por UF': f'Total {filtro} por UF',
            'sg_partido': 'Partido'
        },
        category_orders={"uf_cand": sorted(total_por_uf['uf_cand'].unique())}
    )

    fig_grafico_linha.update_layout(
        hovermode='x unified',
        legend=dict(
            title='Partidos',
            orientation='h',
            yanchor='bottom',
            y= 1.0,
            xanchor='right',
            x=1
        )
    )
    st.plotly_chart(fig_grafico_linha, use_container_width=True)

def grafico_valor_partido(base, filtro):
    df_valor = base[base['nm_cargo'] == filtro]
    total_por_partido = df_valor.groupby(['sg_partido'])['FEFC'].sum().reset_index()
    #total_por_partido['FEFC'] = total_por_partido['FEFC'].apply(lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")) 
    #total_por_partido['FEFC'] = total_por_partido['FEFC'].apply(lambda x: format(x, '.2f'))

    #total_uf_partido = df_valor.groupby('sg_partido').agg({
    #    'nm_cand': 'count',
    #    'FEFC': 'sum'
    #}).reset_index()


    fig_grafico_barra = px.bar(
            total_por_partido, 
            x='sg_partido', 
            y='FEFC',
            text = total_por_partido['FEFC'].apply(lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")),
            color='sg_partido',
            #title='Gráfico FEFC',
            color_discrete_map=cores,
            #labels={'FEFC': 'Valor'},
            text_auto='.2s',
            #category_orders={"sg_partido": sorted(total_por_partido['sg_partido'].unique())}
        )

    fig_grafico_barra.update_layout(
        legend=dict(
            title='Partidos',
            orientation='h',
            yanchor='bottom',
            y= 1.0,
            xanchor='right',
            x=1
        )
    )

    st.plotly_chart(fig_grafico_barra, use_container_width=True)

def grafico_pizza(base, filtro):
    df_base = base[base['nm_cargo'] == filtro]

    pizza = px.pie(
        df_base,
        names='sg_partido',
        values='FEFC',
        title='Distribuição de FEFC por Partido',
        color='sg_partido',
        color_discrete_map=cores,
        hole=0.3,
        labels={'sg_partido': 'Partido', 'FEFC': 'Valor FEFC'}
    )
    pizza.update_traces(textposition='inside')
    pizza.update_layout(uniformtext_minsize=12,uniformtext_mode='hide')
    pizza.update_layout(
        legend=dict(
            title='Partidos',
            orientation='v',  # Vertical (padrão)
            yanchor='top',    # Ancora no topo
            xanchor='left',   # Ancora à esquerda (dentro da área da legenda)
            #x=1.5,           # Posiciona fora do gráfico (valores >1 ou <0 permitem ajuste fino)
            y=1,             # Alinha ao topo do gráfico
            itemsizing='constant',  # Mantém tamanho consistente dos itens
            tracegroupgap=10,       # Espaço entre grupos (útil se houver subgrupos)
            itemwidth=30,           # Largura de cada item (ajuste conforme necessário)
            font=dict(size=12),     # Tamanho da fonte (opcional)
            # Se quiser múltiplas colunas, use:
            entrywidthmode='fraction',  # Define largura proporcional
            entrywidth=0.5,             # Largura de cada entrada (ajuste conforme necessário)
        ),
        margin=dict(r=180)  # Aumenta a margem direita para caber a legenda
    )

    st.plotly_chart(pizza, use_container_width=True)

def card_resultado(base, filtro, texto):
    total_candidatos = base[base['nm_cargo'] == filtro].shape[0]
    total_candidatos_eleitos = AbragenciaFederal.fichas()[(AbragenciaFederal.fichas()['nm_cargo'] == filtro) & (AbragenciaFederal.fichas()['ds_eleicao'] == 'Eleito')].shape[0]

    if texto == "Eleito":
        candidatosEleitos = base[(base['ds_eleicao'] == 'Eleito') & (base['nm_cargo'] == filtro)].shape[0]
        percentual = (candidatosEleitos / total_candidatos_eleitos) * 100 if total_candidatos_eleitos > 0 else 0
        percentual = round(percentual, 2)
        candidatosEleitos = "{:,.0f}".format(candidatosEleitos).replace(",", ".")

        st.metric(texto, candidatosEleitos, f'{percentual} %', border=True)

    elif texto == "Não eleito":
        candidatosNaoEleitos = base[(base['ds_eleicao'] == 'Não eleito') & (base['nm_cargo'] == filtro)].shape[0]
        percentual = (candidatosNaoEleitos / total_candidatos) * 100 if total_candidatos > 0 else 0
        candidatosNaoEleitos = "{:,.0f}".format(candidatosNaoEleitos).replace(",", ".")

        st.metric(texto, candidatosNaoEleitos, f'-{percentual:.3}%', border=True)

    else:
        candidatosEleitos = base[(base['ds_eleicao'] == 'Eleito') & (base['nm_cargo'] == filtro)].shape[0]  
        candidatosTotal = base[base['nm_cargo'] == filtro].shape[0]
        percentual = (candidatosEleitos / candidatosTotal) * 100 if candidatosTotal > 0 else 0
        candidatosTotal = "{:,.0f}".format(candidatosTotal).replace(",", ".")

        st.metric(texto, candidatosTotal,f'{percentual:.3}%', border=True)
        
def tabela_dados(base, filtro = None):
    colunas = ['uf_cand', 'nm_cand', 'sg_partido', 'ds_eleicao', 'nm_cargo', 'li_foto', 'votos','FEFC']
    base = base[base['nm_cargo'] == filtro]
    base = base.sort_values("votos", ascending=False)
    st.dataframe (base[colunas],
                  column_config={
                        'uf_cand': st.column_config.TextColumn("UF"),
                        'nm_cand': st.column_config.TextColumn("Nome do Candidato"),
                        'sg_partido': st.column_config.TextColumn("Partido"),
                        'ds_eleicao': st.column_config.TextColumn("Resultado"),
                        'nm_cargo': st.column_config.TextColumn("Cargo"),
                        'li_foto': st.column_config.ImageColumn("Foto", help="Foto do candidato"),
                        "votos": st.column_config.NumberColumn("Votos", format="localized" ),
                        'FEFC': st.column_config.NumberColumn("FFEC", format="dollar", help="Valor de recursos FEFC"),
                  }, hide_index=True)

def filtro_top_partido(base):
    top_5_siglas = (
        base[
            (base['nm_cargo'] == 'Deputado Federal') & 
            (base['ds_eleicao'] == 'Eleito')
        ]
        .groupby('sg_partido')
        .size()
        .nlargest(4) # Top partidos por número de eleitos + PSDB
        .index
        .tolist()
    )

    if 'PSDB' not in top_5_siglas:
        top_5_siglas.append('PSDB')
    return top_5_siglas

def filtro_base_uf(base, filtro):
    if filtro is not None:
        base = base[base['uf_cand'] == filtro]
        return base
    return base

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
    default= filtro_top_partido(eleicao2022),
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
aba1, aba2, aba3, aba4, aba5 = st.tabs(['Presidente','Governador', 'Senador',  'Dep. Federal',  'Dep. Estadual'])

with aba1:
    st.markdown("## Presidente")
    st.dataframe(eleicao2022[eleicao2022['nm_cargo'] == 'Presidente'])
with aba2:
    st.markdown("## Governador")
    #grafico_linha_uf(eleicao2022, filtro='Governador')
    #st.plotly_chart(dados, use_container_width=True)
    st.markdown("### Gráfico de valores por partido")
    grafico_valor_partido(eleicao2022, filtro='Governador')
    tabela_dados(eleicao2022, filtro='Governador')

with aba3:
    st.markdown("## Senador")
    st.dataframe(eleicao2022[eleicao2022['nm_cargo'] == 'Senador'])

# Criar tabelas e gráficos para Deputado Federal
with aba4:   
    st.markdown("## Deputado Federal")
 
    col1 , col2, col3 = st.columns(3)
    with col1:
        card_resultado(eleicao2022metric, filtro='Deputado Federal', texto='Eleito')
    with col2:
        card_resultado(eleicao2022metric, filtro='Deputado Federal', texto='Não eleito')
    with col3:
        card_resultado(eleicao2022metric, filtro='Deputado Federal', texto='Candidatos')
    
    #st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Gráfico de Partidos")
        grafico_barra_partido(eleicao2022, filtro='Deputado Federal')
    with col2:
        st.markdown("### Gráfico de UF")
        grafico_linha_uf(eleicao2022, filtro='Deputado Federal')

    #st.write("Tipo da coluna:", eleicao2022["FEFC"].dtype)  # Deve ser int64
    #st.divider

    st.markdown("### Gráfico de valores por partido")
    col1, col2 = st.columns(2)
    with col1:
        grafico_valor_partido(eleicao2022, filtro='Deputado Federal')
    with col2:
        grafico_pizza(eleicao2022, filtro='Deputado Federal')
    tabela_dados(eleicao2022, filtro='Deputado Federal')

# Criar tabelas e gráficos para Deputado Estadual
with aba5:   
    st.markdown("## Deputado Estadual")
 
    col1 , col2, col3 = st.columns(3)
    with col1:
        card_resultado(eleicao2022metric, filtro='Deputado Estadual', texto='Eleito')
    with col2:
        card_resultado(eleicao2022metric, filtro='Deputado Estadual', texto='Não eleito')
    with col3:
        card_resultado(eleicao2022metric, filtro='Deputado Estadual', texto='Candidatos')
    
    #st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Gráfico de Partidos")
        grafico_barra_partido(eleicao2022, filtro='Deputado Estadual')
    with col2:
        st.markdown("### Gráfico de UF")
        grafico_linha_uf(eleicao2022, filtro='Deputado Estadual')

    #st.write("Tipo da coluna:", eleicao2022["FEFC"].dtype)  # Deve ser int64
    #st.divider

    st.markdown("### Gráfico de valores por partido")
    col1, col2 = st.columns(2)
    with col1:
        grafico_valor_partido(eleicao2022, filtro='Deputado Estadual')
    with col2:
        grafico_pizza(eleicao2022, filtro='Deputado Estadual')
    tabela_dados(eleicao2022, filtro='Deputado Estadual')

