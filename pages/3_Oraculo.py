import streamlit as st
from langchain.memory import ConversationBufferMemory

from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq


st.set_page_config(layout='centered')

#OPENAI_API_KEY=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

TIPOS_ARQUIVOS_VALIDOS = [
    'Site', 'Youtube', 'Pdf', 'Csv', 'Txt'
]

CONFIG_MODELOS = {'Groq': 
                        {'modelos': ['deepseek-r1-distill-llama-70b', 'llama-3.1-8b-instant', 'gemma2-9b-it'],
                         'chat': ChatGroq},
                  'OpenAI': 
                        {'modelos': ['gpt-4.1-nano-2025-04-14','GPT-4.1 mini'],
                         'chat': ChatOpenAI}}

MEMORIA = ConversationBufferMemory()

def carrega_modelo(provedor, modelo, api_key):
    chat = CONFIG_MODELOS[provedor]['chat'](model=modelo, api_key=api_key)
    st.session_state['chat'] = chat

def pagina_chat():
    st.header('🤖Bem-vindo ao Oráculo', divider=True)

    chat_model = st.session_state.get('chat')
    memoria = st.session_state.get('memoria', MEMORIA)
    for mensagem in memoria.buffer_as_messages:
        chat = st.chat_message(mensagem.type)
        chat.markdown(mensagem.content)

    input_usuario = st.chat_input('Fale com o oráculo')
    if input_usuario:
        chat = st.chat_message('human')
        chat.markdown(input_usuario)

        chat = st.chat_message('ai')
        resposta = chat.write_stream(chat_model.stream(input_usuario))
        
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
        carrega_modelo(provedor, modelo, api_key)


def main():
    pagina_chat()
    with st.sidebar:
        sidebar()


if __name__ == '__main__':
    main()