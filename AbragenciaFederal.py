import pandas as pd
import requests
from io import BytesIO


#url = "https://datalake.psdb.org.br/eleicao2020/fichas2020.parquet"
#
## Baixar o arquivo ignorando SSL (apenas para testes)
#response = requests.get(url, verify=False)  
#df = pd.read_parquet(BytesIO(response.content))
#print(df.head())

# Carrega os dados de municípios
def municipio():
    response = requests.get('https://datalake.psdb.org.br/municipio.parquet', verify=False)  
    df_municipio = pd.read_parquet(BytesIO(response.content))
    df_municipio = df_municipio[['id','uf', 'nome', 'capital', 'no_regiao_brasil']].rename(columns={'nome' : 'municipio', 'id': 'id_municipio'})
    df_municipio = df_municipio[~df_municipio['uf'].str.startswith('ZZ')] # Remove linhas com UF ZZ

    return df_municipio

# Carrega os dados de votos e adiciona informações de municípios
def votacao():
    response = requests.get('https://datalake.psdb.org.br/eleicao2022/votomunicipio2022.parquet', verify=False)  
    df_votacao = pd.read_parquet(BytesIO(response.content))
    df_votacao = df_votacao[df_votacao['turno'] == 1]
    df_votacao = df_votacao[['nu_titulo_eleitor', 'municipio', 'votos']].rename(columns={'municipio': 'id_municipio'})

    df_votos_eleicao = pd.merge(
        df_votacao, 
        municipio(),
        on='id_municipio',
        how='inner'
        )

    return df_votos_eleicao

# Carrega as fichas dos candidatos e aplica filtros e ajustes
def fichas():
    response = requests.get('https://datalake.psdb.org.br/eleicao2022/fichas2022.parquet', verify=False)  
    df_fichas = pd.read_parquet(BytesIO(response.content))
    df_fichas = df_fichas[df_fichas['ds_sit_urna'] == 'Consta da urna']
    df_fichas = df_fichas[df_fichas['sit_partido'].isin (['Deferido', 'Deferido com recurso'])]
    df_fichas = df_fichas[df_fichas['sit_cand'].isin (['Deferido', 'Deferido com recurso'])]
    df_fichas['ds_eleicao'] = df_fichas['ds_eleicao'].replace({
        'Eleito por média': 'Eleito',
        'Eleito por QP': 'Eleito',
        'Suplente' : 'Não eleito',
        'Concorrendo' : 'Não eleito',
    })
    df_fichas['nm_cargo'] = df_fichas['nm_cargo'].replace({'Deputado Distrital': 'Deputado Estadual'})
    df_fichas['id_cand'] = df_fichas['id_cand'].astype(str)

    df_fichas.drop(columns=['ds_sit_urna', 'sit_partido', 'sit_cand', 'nu_cpf',
                            'st_reeleicao', 'dt_atualizacao', 'nm_partido', 'nu_partido',
                            'ds_coligacao', 'nu_urna', 'cd_sit_candidato', 'ds_sit_candidato', 
                            'ds_totalizacao', 'cd_cargo', 'ds_email', 'nu_cnpj', 'ds_composicao'], inplace=True)
    
    df_fichas['li_foto'] = df_fichas['li_foto'].str.replace('datarepo', 'datalake')
    df_fichas.loc[df_fichas['nu_titulo_eleitor'] == '026474760906', 'ds_eleicao'] = 'Eleito' #Incluir GEOVANIA DE SA na lista de eleitos
    
    return df_fichas

def fichas_valor():
    response = requests.get('https://datalake.psdb.org.br/eleicao2022/contas2022.parquet', verify=False)  
    df_valor = pd.read_parquet(BytesIO(response.content))
    df_valor["totalPartidos"] = df_valor["totalPartidos"].fillna(0)
    df_valor = df_valor[['id', 'totalPartidos']].rename(columns={'id': 'id_cand','totalPartidos' : 'FEFC'})
    #df_valor['FEFC'] = df_valor['FEFC'].apply(lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    df_fichas = pd.merge(
        fichas(),
        df_valor,
        on='id_cand',
        how='left'
    )


    return df_fichas

# Carrega as fichas dos candidatos com votos
def fichas_com_votos():
    votos = (
        votacao().groupby(['nu_titulo_eleitor'])['votos']
        .sum()
        .reset_index()
    )

    df_fichas_com_votos = pd.merge(
        fichas_valor(),
        votos,
        on='nu_titulo_eleitor',
        how='inner'
    )
    #df_fichas_com_votos["votos"] = pd.to_numeric(df_fichas_com_votos["votos"])
    #df_fichas_com_votos['votos'] = df_fichas_com_votos['votos'].apply(lambda x: f"{x:,.0f}".replace(",", "."))

    return df_fichas_com_votos

# Carrega as fichas dos candidatos com votos por município
def fichas_com_votos_municipio():
    df_fichas_com_votos_municipio = pd.merge(
        fichas(),
        votacao(),
        on='nu_titulo_eleitor',
        how='right'
    )

    return df_fichas_com_votos_municipio
