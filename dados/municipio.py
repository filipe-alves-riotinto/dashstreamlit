import pandas as pd
import requests
from io import BytesIO
from dotenv import load_dotenv
import os

load_dotenv()
DATALAKE = os.getenv("DATALAKE")

def municipio():
    response = requests.get(f'https://datalake.psdb.org.br/municipio.parquet', verify=False)  
    df_municipio = pd.read_parquet(BytesIO(response.content))
    df_municipio = df_municipio[['id','uf', 'nome', 'capital', 'no_regiao_brasil']].rename(columns={'nome' : 'municipio', 'id': 'id_municipio'})
    df_municipio = df_municipio[~df_municipio['uf'].str.startswith('ZZ')] # Remove linhas com UF ZZ

    return df_municipio
