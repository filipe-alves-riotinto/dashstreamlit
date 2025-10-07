import pandas as pd
from .fichas import fichas 
from .fefc import fefc
from .votos import votacao


def fichas_com_fefc(ano):
    df_fichas = pd.merge(
        fichas(ano),
        fefc(ano),
        on='id_cand',
        how='left'
    )

    return df_fichas

def fichas_com_votos(ano):
    votos = (
        votacao(ano).groupby(['nu_titulo_eleitor'])['votos']
        .sum()
        .reset_index()
    )

    df_fichas_com_votos = pd.merge(
        fichas(ano),
        votos,
        on='nu_titulo_eleitor',
        how='inner'
    )
    #df_fichas_com_votos["votos"] = pd.to_numeric(df_fichas_com_votos["votos"])
    #df_fichas_com_votos['votos'] = df_fichas_com_votos['votos'].apply(lambda x: f"{x:,.0f}".replace(",", "."))

    return df_fichas_com_votos

def fichas_com_votos_e_fefc(ano):
    df_temp = fichas_com_votos(ano)[['nu_titulo_eleitor', 'votos']]

    df_fichas_com_votos = pd.merge(
        fichas_com_fefc(ano),
        df_temp,
        on='nu_titulo_eleitor',
        how='inner'
    )
    #df_fichas_com_votos["votos"] = pd.to_numeric(df_fichas_com_votos["votos"])
    #df_fichas_com_votos['votos'] = df_fichas_com_votos['votos'].apply(lambda x: f"{x:,.0f}".replace(",", "."))
    print(ano)

    return df_fichas_com_votos
