import os
import sys
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from rag_pipeline import rag_query, construir_prompt
from embeddings import gerar_embedding
from vector_store import conectar_pinecone, buscar

load_dotenv

def coletar_dados_avaliacao(pergunta_respota):
    """
    Roda o pipeline RAG para cada pergunta e coleta
    os dados necessários para o RAGAS avaliar
    """
    print("🔄 Coletando dados para avaliação...\n")

    pergunta = []
    reposta = []
    contexto = []
    ground_truth = []

    indice = conectar_pinecone()

    for item in pergunta_respota:
        pergunta = item['pergunta']
        ground_truth = item['resposta_esperada']

        # Busca chunks relevantes
        emb = gerar_embedding(pergunta)
        chunks = buscar(indice, emb, top_k=5)
        ctx = [c.metadata['text'] for c in chunks]

        # Gera resposta usando RAG
        resultado = rag_query(pergunta)

        pergunta.append(pergunta)
        reposta.append(resultado["resposta"])
        contexto.append(ctx)
        ground_truth.append(ground_truth)

        print(f"✅ Coletado: {pergunta[:60]}...")

    return {
        "pergunta": pergunta,
        "resposta": reposta,
        "contexto": contexto,
        "ground_truth": ground_truth
    }

def avaliar_com_ragas(dados):
    """Avalia o pipeline RAG usando as métricas do RAGAS"""
    from datasets import Dataset
    from ragas import evaluate
    from ragas.metrics import (
        faithfulness, # Verifica se a resposta é fiel ao contexto, ou se a resposta é inventada
        answer_relevance, # Verifica se a resposta é relevante para a pergunta, ou se a resposta é irrelevante
        context_precision, # Verifica se os chunks usados para gerar a resposta são relevantes, ou se os chunks são irrelevantes
        context_recall, # Verifica se faltaram chunks relevantes para gerar a resposta, ou se os chunks usados foram suficientes
    )

    print("\n📊 Rodando avaliação com RAGAS...")

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0) # Usamos o gpt-4o-mini para avaliação, pois é mais barato e rápido, e o RAGAS é projetado para ser robusto a modelos menores, definimos a temperatura como 0 para garantir consistência na avaliação
    embedding = OpenAIEmbeddings(model="text-embedding-3-small") # Usamos o text-embedding-3-small para avaliação, pois é mais barato e rápido, e o RAGAS é projetado para ser robusto a modelos de embedding menores