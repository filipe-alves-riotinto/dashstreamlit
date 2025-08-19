from langchain_community.document_loaders import (WebBaseLoader,
                                                  YoutubeLoader, 
                                                  CSVLoader, 
                                                  PyPDFLoader, 
                                                  TextLoader)

#caminho = 'https://www.psdb.org.br/conheca/quem-e-quem/deputados-federais'
def carrega_site(url):
    loader = WebBaseLoader(url)
    lista_documentos = loader.load()
    documento = '\n\n'.join([doc.page_content for doc in lista_documentos])
    return documento

#caminho = 'nf5dM1w5PQY'
def carrega_youtube(video_id):
    loader = YoutubeLoader(video_id, add_video_info=False, language=['pt'])
    lista_documentos = loader.load()
    documento = '\n\n'.join([doc.page_content for doc in lista_documentos])
    return documento

#caminho = 'DocumentoTeste.csv'
def carrega_csv(caminho):
    loader = CSVLoader(caminho,
        csv_args={
            'delimiter': ';'
            }
        )
    lista_documentos = loader.load()
    documento = '\n\n'.join([doc.page_content for doc in lista_documentos])
    return documento

#caminho = 'Conexão Tucana.pdf'
def carrega_pdf(caminho):
    loader = PyPDFLoader(caminho)
    lista_documentos = loader.load()
    documento = '\n\n'.join([doc.page_content for doc in lista_documentos])
    return documento

#caminho = 'knowledge_base.txt'
def carrega_txt(caminho):
    loader = TextLoader(caminho)
    lista_documentos = loader.load()
    documento = '\n\n'.join([doc.page_content for doc in lista_documentos])
    return documento

