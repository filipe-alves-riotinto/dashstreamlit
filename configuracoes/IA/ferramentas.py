import os
from dotenv import load_dotenv
import pandas as pd
from IPython.display import Markdown, display
import matplotlib.pyplot as plt
import seaborn as sns
from langchain_groq import ChatGroq
from langchain_experimental.tools import PythonAstREPLTool
from langchain_core.output_parsers import StrOutputParser
from langchain.tools import tool
from langchain.agents import Tool
from langchain.prompts import PromptTemplate
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import matplotlib.colors as mcolors
import numpy as np

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Configurar llm
llm = ChatGroq(
    api_key = GROQ_API_KEY,
    model_name='llama3-70b-8192',
    temperature=0
)

# Relatório informações
@tool
def informacoes_dataframe(pergunta: str, df: pd.DataFrame) -> str:
    """Utilize esta ferramenta sempre que o usuário solicitar informações gerais sobre o DataFrame,
    incluindo número de colunas e linhas, nomes das colunas e seus tipos de dados, contagem de dados nulos
    e duplicados para dar um panorama geral sobre o arquivo."""

    shape = df.shape
    columns = df.dtypes
    nulos = df.isnull().sum()
    nans_str = df.apply(lambda col: col[~col.isna()].astype(str).str.strip().str.lower().eq('nan').sum())
    duplicados = df.duplicated().sum()

    template_resposta = PromptTemplate(
        template="""
            Você é um analista de dados encarregado de apresentar um resumo informativo sobre um DataFrame a partir de uma {pergunta} feita pelo usuário.

            A seguir, você encontrará as informações gerais da base de dados:
            ==================== INFORMAÇÕES DO DATAFRAME ====================
            Dimensões: {shape}

            Colunas e tipos de dados:
            {columns}

            Valores nulos por coluna:
            {nulos}

            Strings 'nan' (qualquer capitalização) por coluna:
            {nans_str}

            Linhas duplicadas: {duplicados}
            ==================================================================

            Com base nessas informações, escreva um resumo claro e organizado contendo:
            1. Um título: ## Relatório de Informações gerais sobre o dataset,
            2. A dimensão total do DataFrame,
            3. A descrição de cada coluna (incluindo nome, tipo de dado e o que aquela coluna é),
            4. As colunas que contém dados nulos, com a respectiva quantidade;
            5. As colunas que contém strings 'nan', com a respectiva quantidade;
            6. E a existência (ou não) de dados duplicados;
            7. Escreva um parágrafo sobre analises que podem ser feitas com esses dados;
            8. Escreva um parágrafo sobre tratamentos que podem ser feitos nos dados.
            """,
        input_variables=['pergunta', 'shape', 'columns', 'nulos', 'nans_str', 'duplicados']
    )

    cadeia = template_resposta | llm | StrOutputParser()

    resposta = cadeia.invoke({
        "pergunta" : pergunta,
        "shape" : shape,
        "columns": columns,
        "nulos": nulos,
        "nans_str": nans_str,
        "duplicados": duplicados
    })

    return resposta

# Relatório estatístico
@tool
def resumo_estatistico(pergunta: str, df: pd.DataFrame) -> str:
    """Utilize esta ferramenta sempre que o usuário solicitar um resumo estatístico completo
    e descritivo da base de dados, incluindo várias estatísticas (média, desvio padrão, mínimo, máximo etc.)."""
    
    estatisticas_descritivas = df.describe(include='number').transpose().to_string()

    template_resposta = PromptTemplate(
        template="""Você é um analista de dados encarregado de interpretar resultados estatísticos de uma base de dados
            a partir de uma {pergunta} feita pelo usuário.

            A seguir, você encontrará as estatísticas descritivas da base de dados:
            ============ESTATÍSTICAS DESCRITIVAS============
            {resumo}
            ================================================

            Com base nesses dados, elabore um resumo explicativo com linguagem clara, acessível e fluída, destacando
            os principais pontos dos resultados. Inclua:
            1. Um título: ## Relatório de estatísticas descritivas;
            2. Uma visão geral das estatísticas das colunas numéricas;
            3. Um parágrafo sobre cada uma das colunas, comentando informações sobre seus valores;
            4. Identificação de possíveis outliers com base nos valores mínimo e máximo;
            5. Recomendações de próximos passos na análise com base nos padrões identificados.
            """,
        input_variables=['pergunta', 'resumo']
    )

    cadeia = template_resposta | llm | StrOutputParser()

    resposta = cadeia.invoke({
        "pergunta" : pergunta,
        "resumo" : estatisticas_descritivas
    })

    return resposta

# Gerador de garficos
@tool
def gerar_grafico(pergunta: str, df: pd.DataFrame) -> None:
    """Utilize esta ferramenta para gerar gráficos Plotly a partir de um DataFrame."""
    
    colunas_info = "\n".join([f"- {col} ({dtype})" for col, dtype in df.dtypes.items()])
    amostra_dados = df.head(3).to_dict(orient='records')
    
    template_resposta = PromptTemplate(
        template="""
        Você é um especialista em visualização de dados. Sua tarefa é gerar *apenas o código Python**
        para plotar um gráfico com base na solicitação do usuário.

        ## Solicitação do usuário:
        "{pergunta}"

        ## Metadados do DataFrame:
        {colunas}

        ## Amostra dos dados (3 primeiras linhas):
        {amostra}

        ## Instruções obrigatórias:
        1. Use APENAS plotly.express (como `px`) para criar o gráfico;
        2. Certifique-se de que todas as colunas mencionadas existem no DataFrame chamado `df`;
        3. Escolha o tipo de gráfico adequado conforme a análise solicitada;
        4. Configure o layout para evitar sobreposição;
        5. Adicione título e rótulos apropriados;
        6. Ajuste a legenda para não sobrepor o gráfico;
        7. Atribua o gráfico a uma variável chamada `fig`;
        8. Não use plt.show() ou fig.show().

        Retorne APENAS o código Python, sem nenhum texto adicional ou explicação.

        Código Python:```
        """,
        input_variables=["pergunta", "colunas", "amostra"]
    )
    
    cadeia = template_resposta | llm | StrOutputParser()
    
    try:
        codigo_bruto = cadeia.invoke({
            "pergunta": pergunta,
            "colunas": colunas_info,
            "amostra": amostra_dados
        })
        
        # Limpar o código
        codigo_limpo = codigo_bruto.replace("```python", "").replace("```", "").strip()
        
        # Preparar ambiente de execução
        exec_globals = {
            "df": df,
            "px": px,
            "go": go,
            "pd": pd,
            "np": np
        }
        exec_locals = {}
        
        # Executar o código
        exec(codigo_limpo, exec_globals, exec_locals)
        
        # Obter a figura gerada
        if 'fig' in exec_locals:
            st.plotly_chart(exec_locals['fig'])
        else:
            st.error("O código não gerou uma figura Plotly. Verifique o código gerado.")
            st.code(codigo_limpo)
            
    except Exception as e:
        st.error(f"Erro ao gerar gráfico: {str(e)}")
        if 'codigo_limpo' in locals():
            st.code(codigo_limpo)


#Função para cirar ferramentas
def criar_ferrmantas(df):
    ferramenta_informacoes_dataframe = Tool(
        name = "Informações DataFrame",
        func = lambda pergunta:informacoes_dataframe.run({"pergunta":pergunta, "df":df}),  
        description = """Utilize esta ferramenta sempre que o usuário solicitar informações gerais sobre o dataframe,
                    incluindo número de colunas e linhas, nomes das colunas e seus tipos de dados, contagem de dados nulos e
                    duplicados para dar um panorama geral sobre o arquivo.""", return_direct=True
    )

    ferramenta_resumo_estatistico = Tool(
        name="Resumo Estatistico",
        func= lambda pergunta:resumo_estatistico.run({"pergunta":pergunta, "df":df}),
        description="""Utilize esta ferramenta sempre que o usuário solicitar um resumo estatístico completo
                    e descritivo da base de dados, incluindo várias estatísticas (média, desvio padrão, mínimo, máximo etc.).
                    Não utilize esta ferramenta para calcular uma única métrica como 'qual é a média de X' ou 
                    qual a correlação das variáveis'. Nesses casos, utilize a ferramenta_codigos_python.""", return_direct=True
    )

    ferramenta_gerar_grafico = Tool(
        name="Gerar Gráfico",
        func=lambda pergunta:gerar_grafico.run({"pergunta":pergunta, "df":df}),
        description="""Utilize esta ferramenta sempre que a pessoa usuária solicitar um gráfico a partir de um DataFrame Pandas (`df`),
                    com base em uma instrução do usuário. A instrução pode conter pedidos como: 'crie um gráfico de distribuição de valor investido' ou 'média de votos',
                    'plote a distribuição do tempo de entrega', ou 'plote a relação entre a classificação dos agentes e o tempo de entrega'.
                    Palavras-chave comuns que indicam o uso dessa ferramenta incluem: 'crie um gráfico', 'plote', 'visualize', 'faça um gráfico de', 
                    'mostre a distribuição', 'represente graficamente', entre outros.""", return_direct=True
        )

    ferramenta_codigos_python = Tool(
        name="Códigos Python",
        func=PythonAstREPLTool(locals={"df": df}),
        description="""Utilize esta ferramenta sempre que o usuário solicitar cálculos, consultas ou transformações
                    específicas usando Python diretamente sobre o DataFrame `df`.
                    Exemplos de uso incluem: "Qual é a média da coluna X?", "Quais são os valores únicos da coluna Y?",
                    "Qual a correlação entre A e B?". Evite utilizar esta ferramenta para solicitações mais amplas ou descritivas,
                    como informações gerais sobre o DataFrame, resumos estatísticos completos ou geração de gráficos - nesses casos,
                    use as ferramentas apropriadas."""
    )

    return [
        ferramenta_informacoes_dataframe,
        ferramenta_resumo_estatistico,
        ferramenta_gerar_grafico,
        ferramenta_codigos_python
    ]