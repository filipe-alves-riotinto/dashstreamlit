import streamlit as st
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate

from configuracoes.IA.loaders import *

import tempfile



st.set_page_config(layout='centered')

api_key='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'

TIPOS_ARQUIVOS_VALIDOS = [
    'Site', 'Youtube', 'Pdf', 'Csv', 'Txt'
]

CONFIG_MODELOS = {'OpenAI': 
                        {'modelos': ['gpt-4.1-nano-2025-04-14'],
                         'chat': ChatOpenAI}}

MEMORIA = ConversationBufferMemory()

def carrega_arquivo(tipo_arquivo, arquivo):
    if tipo_arquivo == 'Site':
        documento = carrega_site(arquivo)
    if tipo_arquivo == 'Youtube':
        documento = carrega_youtube(arquivo)
    if tipo_arquivo == 'Pdf':
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp:
            temp.write(arquivo.read())
            nome_temp = temp.name
        documento = carrega_pdf(nome_temp)
    if tipo_arquivo == 'Csv':
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as temp:
            temp.write(arquivo.read())
            nome_temp = temp.name
        documento = carrega_csv(nome_temp)
    if tipo_arquivo == 'Txt':
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as temp:
            temp.write(arquivo.read())
            nome_temp = temp.name
        documento = carrega_txt(nome_temp)
    return documento


def carrega_modelo(provedor, modelo, api_key, tipo_arquivo, arquivo):
    documento = carrega_arquivo(tipo_arquivo, arquivo)

    system_message = '''Você é um assistente em um partido politico amigável.
    Você possui acesso às seguintes informações vindas 
    de um documento {}: 

    ####
    {}
    ####

    Utilize as informações fornecidas para basear as suas respostas.

    Sempre que houver $ na sua saída, substita por S.

    Se a informação do documento for algo como "Just a moment...Enable JavaScript and cookies to continue" 
    sugira ao usuário carregar novamente o Oráculo!'''.format(tipo_arquivo, documento)

    template = ChatPromptTemplate.from_messages([
        ('system', system_message),
        ('placeholder', '{chat_history}'),
        ('user', '{input}')
    ])

    chat = CONFIG_MODELOS[provedor]['chat'](model=modelo, api_key=api_key)
    chain = template | chat
    st.session_state['chain'] = chain

def pagina_chat():
    st.header('🤖Bem-vindo ao Oráculo', divider=True)

    chain = st.session_state.get('chain')
    if chain is None:
        st.error("Carrege o assistente")
        st.stop()

    memoria = st.session_state.get('memoria', MEMORIA)
    for mensagem in memoria.buffer_as_messages:
        chat = st.chat_message(mensagem.type)
        chat.markdown(mensagem.content)

    input_usuario = st.chat_input('Fale com o oráculo')
    if input_usuario:
        chat = st.chat_message('human')
        chat.markdown(input_usuario)

        chat = st.chat_message('ai')
        resposta = chat.write_stream(chain.stream({
            'input':input_usuario,
            'chat_history': memoria.buffer_as_messages
        }))
        
        memoria.chat_memory.add_user_message(input_usuario)
        memoria.chat_memory.add_ai_message(resposta)
        st.session_state['memoria'] = memoria


def sidebar():
    tabs = st.tabs(['Upload de Arquivos', 'Seleção de Modelos'])
    with tabs[0]:
        tipo_arquivo = st.selectbox('Selecione o tipo de arquivo', TIPOS_ARQUIVOS_VALIDOS)
        if tipo_arquivo == 'Site':
            arquivo = st.text_input('Digite a url do site')
        if tipo_arquivo == 'Youtube':
            arquivo = st.text_input('Digite a url do vídeo')
        if tipo_arquivo == 'Pdf':
            arquivo = st.file_uploader('Faça o upload do arquivo pdf', type=['.pdf'])
        if tipo_arquivo == 'Csv':
            arquivo = st.file_uploader('Faça o upload do arquivo csv', type=['.csv'])
        if tipo_arquivo == 'Txt':
            arquivo = st.file_uploader('Faça o upload do arquivo txt', type=['.txt'])
    with tabs[1]:
        provedor = st.selectbox('Selecione o provedor dos modelo', CONFIG_MODELOS.keys())
        modelo = st.selectbox('Selecione o modelo', CONFIG_MODELOS[provedor]['modelos'])
        api_key = st.text_input(
            f'Adicione a api key para o provedor {provedor}',
            value=st.session_state.get(f'api_key_{provedor}'))

        st.session_state[f'api_key_{provedor}'] = api_key
    
    if st.button('Inicializar Oráculo', use_container_width=True):
        carrega_modelo(provedor, modelo, api_key, tipo_arquivo, arquivo)
    if st.button('Apagar historico de conversa', use_container_width=True):
        st.session_state['memoria'] = MEMORIA


def main():
    with st.sidebar:
        sidebar()
    pagina_chat()


if __name__ == '__main__':
    main()