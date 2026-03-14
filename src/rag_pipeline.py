import os
import sys
from dotenv import load_dotenv
from openai import OpenAI

# Adiciona o src ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from embeddings import gerar_embedding
from vector_store import conectar_pinecone, buscar

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def construir_prompt(pergunta, chunks_relevantes):
    """Monta o prompt com contexto dos chunks recuperados."""
    contexto = ""
    for i, chunk in enumerate(chunks_relevantes):
        arquivo = chunk.metadata['arquivo']
        pagina = chunk.metadata['pagina']
        texto = chunk.metadata['texto']
        contexto += f"\n[Fonte {i+1}: {arquivo}, página {pagina}]\n{texto}\n"

    prompt = f"""Você é um assistente especializado em responder perguntas sobre documentos técnicos.
Use APENAS as informações fornecidas no contexto abaixo para responder.
Se a resposta não estiver no contexto, diga: "Não encontrei essa informação nos documentos."
Sempre cite a fonte (arquivo e página) ao final da resposta.

CONTEXTO:
{contexto}

PERGUNTA: {pergunta}

RESPOSTA:"""
    return prompt


def rag_query(pergunta, top_k=5):
    """Pipeline RAG completo: busca + geração."""
    print(f"\n🔍 Pergunta: {pergunta}")
    print("─" * 60)

    # 1. Converte pergunta em embedding
    print("1️⃣  Gerando embedding da pergunta...")
    embedding_query = gerar_embedding(pergunta)

    # 2. Busca chunks relevantes no Pinecone
    print("2️⃣  Buscando chunks relevantes no Pinecone...")
    indice = conectar_pinecone()
    chunks_relevantes = buscar(indice, embedding_query, top_k=top_k)
    print(f"   {len(chunks_relevantes)} chunks encontrados")

    # 3. Monta o prompt com contexto
    print("3️⃣  Montando prompt com contexto...")
    prompt = construir_prompt(pergunta, chunks_relevantes)

    # 4. Gera resposta com GPT-4o-mini
    print("4️⃣  Gerando resposta com GPT-4o-mini...")
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1  # Baixo para respostas mais precisas
    )

    resposta = response.choices[0].message.content

    print("\n✅ RESPOSTA:")
    print("─" * 60)
    print(resposta)
    print("─" * 60)

    return {
        "pergunta": pergunta,
        "resposta": resposta,
        "chunks_usados": len(chunks_relevantes),
        "fontes": list(set([c.metadata['arquivo'] for c in chunks_relevantes]))
    }


if __name__ == "__main__":
    # Testa com 3 perguntas diferentes
    perguntas = [
        "O que é RAG e quais são seus componentes principais?",
        "Quais são as boas práticas de segurança em APIs REST?",
        "Como funciona o chunking em projetos de Data Science?"
    ]

    for pergunta in perguntas:
        resultado = rag_query(pergunta)
        print(f"\n📁 Fontes consultadas: {resultado['fontes']}")
        print("\n" + "═" * 60 + "\n")
        