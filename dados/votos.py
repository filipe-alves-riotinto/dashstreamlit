import pandas as pd
import requests
from io import BytesIO
from dotenv import load_dotenv
import os
from .municipio import municipio

load_dotenv()
DATALAKE = os.getenv("DATALAKE")

def votacao(ano):
    response = requests.get(f'{DATALAKE}/eleicao{ano}/votomunicipio{ano}.parquet', verify=False)  
    df_votacao = pd.read_parquet(BytesIO(response.content))
    df_votacao = df_votacao[df_votacao['turno'] == 1]
    df_votacao = df_votacao[['nu_titulo_eleitor', 'municipio', 'votos']].rename(columns={'municipio': 'id_municipio'})

    df_votos_eleicao = pd.merge(
        df_votacao, 
        municipio(),
        on='id_municipio',
        how='inner'
        )
    print('===================')
    print(response.url)

    return df_votos_eleicao
