import os # Importa a biblioteca os para manipulação de arquivos e variáveis de ambiente
import sys
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from rag_pipeline import rag_query, construir_prompt
from embeddings import gerar_embedding
from vector_store import conectar_pinecone, buscar

load_dotenv()

def coletar_dados_avaliacao(pergunta_resposta): # Define a função para coletar dados de avaliação
    """
    Roda o pipeline RAG para cada pergunta e coleta
    os dado necessários para o RAGAS avaliar.
    """

    print("Coletando dados para avaliação...\n")

    # Inicia a lista de variaveis que serão utilizadas para validar a qualidade das respostas geradas.
    perguntas = []
    respostas = []
    contextos = []
    ground_truths = []

    indice = conectar_pinecone()

    for item in pergunta_resposta:
        pergunta = item["pergunta"] # Busca na lista de entrada da funçã a pergunta a ser respondida
        ground_truth = item["resposta_esperada"] # Busca na lista de entrada da função as respostas esperadas para a pergunta, que serão usadas como referência para avaliação.

        # Busca chunks relevantes usando o Pinecone para essa pergunta
        emb = gerar_embedding(pergunta) # Gera os embeddings das perguntas que foram buscada da lista pergunta_resposta
        chunks = buscar(indice, emb, top_k=5) # Busca os chunks mais relevantes no Pinecone usando os embeddings gerados, retornando os top_k resultados mais relevantes.
        ctx = [c.metadata["texto"] for c in chunks] # Extrai o texto dos chunks retornados para usar como contexto na geração da resposta.

        # Gera a resposta usando o pipeline RAG
        resultado = rag_query(pergunta)

        # Acumula os dados para avaliação
        perguntas.append(pergunta)
        respostas.append(resultado["resposta"])
        contextos.append(ctx)
        ground_truths.append(ground_truth)

        print(f" Coletando: {pergunta[:60]}... \n")

        #Retorna os dados no formato esperado pelo RAGAS
    return {
        "question": perguntas,
        "answer": respostas,
        "context":contextos,
        "ground_truth": ground_truths
    }