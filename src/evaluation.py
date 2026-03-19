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
    "retrieved_contexts": contextos,
    "ground_truth": ground_truths
}

def avaliar_com_ragas(dados): # Define a função que executa a avaliação usando as métricas do RAGAS
    """ Avalia o pipeline RAG usando as métricas do RAGAS."""
    from datasets import Dataset
    from ragas import evaluate
    from ragas.metrics import (
        faithfulness, # Retorna métrica que medira a fidelidade da resposta é fiel ao contexto recuperado
        answer_relevancy, # Retorna métrica que avalia se a resposta é relevante para a pergunta feita
        context_precision, # Retorna métrica que avalia se o contexto utilizado para gerar a resposta é relevante
        context_recall # Retorna métrica para avaliar se o contexto recuperado é suficiente para responder a pergunta
    )

    print("\n📊 Rodando avaliação RAGAS...")

    # Configurando os modelos que o RAGAS usará para avaliar as repostas
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0) # Modelo definido para avaliar, com temperatura 0 para garantir respostas mais consistentes e objetivas
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small") # Modelo de embeddings já determinado para o projeto.

    dataset = Dataset.from_dict(dados) # Converte os dados coletados para o formato de dataset esperado pelo RAGAS

    resultado = evaluate(
        dataset = dataset,
        metrics = [
            faithfulness,
            answer_relevancy,
            context_precision,
            context_recall
        ],
        llm = llm,
        embeddings = embeddings, 
    )

    return resultado

def exibir_relatorio(resultado):
    """Exibe o relatório de avaliação de forma clara."""
    print("\n" + "═" * 60)
    print("📋 RELATÓRIO DE AVALIAÇÃO — IntelliDoc RAG")
    print("═" * 60)

    # Extrai os scores — RAGAS 0.4 retorna listas, então calculamos a média
    scores = {
        "Faithfulness":      sum(resultado["faithfulness"]) / len(resultado["faithfulness"]),
        "Answer Relevancy":  sum(resultado["answer_relevancy"]) / len(resultado["answer_relevancy"]),
        "Context Precision": sum(resultado["context_precision"]) / len(resultado["context_precision"]),
        "Context Recall":    sum(resultado["context_recall"]) / len(resultado["context_recall"]),
    }

    # Define os thresholds mínimos aceitáveis para cada métrica
    thresholds = {
        "Faithfulness":      0.80,
        "Answer Relevancy":  0.75,
        "Context Precision": 0.70,
        "Context Recall":    0.70,
    }

    for metrica, score in scores.items():
        threshold = thresholds[metrica]
        if score != score:  # Verifica se é NaN (NaN != NaN é sempre True)
            print(f"\n  ⚠️  {metrica:<20}: N/A  (timeout na avaliação)")
            continue
        status = "✅" if score >= threshold else "⚠️"
        barra  = "█" * int(score * 20)
        print(f"\n  {status} {metrica:<20}: {score:.4f}  [{barra:<20}]  (mín: {threshold})")

    # Calcula média ignorando NaN
    scores_validos = [s for s in scores.values() if s == s]
    media = sum(scores_validos) / len(scores_validos) if scores_validos else 0


    print(f"\n{'─' * 60}")
    print(f"  🎯 Score Médio Geral: {media:.4f}")
    print("═" * 60)

    # Salva o relatório em JSON para histórico e análise futura
    relatorio = {k: round(v, 4) for k, v in scores.items()}
    relatorio["media_geral"] = round(media, 4)
    with open("data/processed/relatorio_ragas.json", "w") as f:
        json.dump(relatorio, f, indent=2)
    print("\n💾 Relatório salvo em data/processed/relatorio_ragas.json")

    

if __name__ == "__main__":
    # Dataset de avaliação: 5 pares de pergunta e resposta esperada (gabarito)
    perguntas_respostas = [
        {
            "pergunta": "O que é RAG e quais são seus componentes principais?",
            "resposta_esperada": "RAG é Retrieval-Augmented Generation, uma arquitetura que combina busca de informação com geração de texto. Seus componentes são: ingestão de documentos, geração de embeddings, banco vetorial, recuperação por similaridade e geração de resposta com LLM."
        },
        {
            "pergunta": "Quais são as boas práticas de segurança em APIs REST?",
            "resposta_esperada": "As boas práticas incluem uso de JWT com tempo de expiração curto, princípio do menor privilégio, defesa em profundidade, validação e sanitização de inputs, uso de HTTPS, monitoramento de logs e proteção contra ataques como SQL Injection e CSRF."
        },
        {
            "pergunta": "O que são embeddings e como funcionam?",
            "resposta_esperada": "Embeddings são representações numéricas vetoriais de alta dimensão que capturam o significado semântico de um texto. Vetores semanticamente similares ficam próximos no espaço vetorial, permitindo busca por similaridade de significado."
        },
        {
            "pergunta": "Como o Git ajuda no desenvolvimento de software?",
            "resposta_esperada": "Git é um sistema de controle de versão que permite voltar a versões anteriores do código, trabalhar em branches paralelas, colaborar com outros desenvolvedores sem sobrescrever trabalho e rastrear quem fez cada mudança e quando."
        },
        {
            "pergunta": "Quais são as métricas de avaliação do RAGAS?",
            "resposta_esperada": "As métricas do RAGAS são: faithfulness, answer relevancy, context precision e context recall."
        },
    ]

    dados     = coletar_dados_avaliacao(perguntas_respostas) # Coleta os dados rodando o pipeline RAG para cada pergunta
    resultado = avaliar_com_ragas(dados)                     # Avalia com as métricas do RAGAS
    exibir_relatorio(resultado)                              # Exibe e salva o relatório final