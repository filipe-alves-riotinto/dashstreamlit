import pandas as pd
import requests
from io import BytesIO
from dotenv import load_dotenv
import os

load_dotenv()
DATALAKE = os.getenv("DATALAKE")

def fefc(ano):
    response = requests.get(f'{DATALAKE}/eleicao{ano}/contas{ano}.parquet', verify=False)  
    df_fefc = pd.read_parquet(BytesIO(response.content))
    df_fefc["totalPartidos"] = df_fefc["totalPartidos"].fillna(0)
    df_fefc = df_fefc[['id', 'totalPartidos']].rename(columns={'id': 'id_cand','totalPartidos' : 'FEFC'})
    #df_fefc['FEFC'] = df_fefc['FEFC'].apply(lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    
    return df_fefc