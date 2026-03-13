import ssl
import certifi
import os

os.environ['SSL_CERT_FILE'] = certifi.where()
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
ssl._create_default_https_context = ssl.create_default_context

from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv
from embeddings import gerar_embeddings_chunks

load_dotenv()


def conectar_pinecone():
    """Conecta ao Pinecone e retorna o índice."""
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    nome_indice = os.getenv("PINECONE_INDEX_NAME", "intellidoc")

    # Cria o índice se não existir
    indices_existentes = [i.name for i in pc.list_indexes()]

    if nome_indice not in indices_existentes:
        print(f"📦 Criando índice '{nome_indice}'...")
        pc.create_index(
            name=nome_indice,
            dimension=1536,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1")
        )
        print(f"✅ Índice criado!")
    else:
        print(f"✅ Índice '{nome_indice}' já existe")

    return pc.Index(nome_indice)


def inserir_chunks(indice, chunks_com_embeddings, batch_size=50):
    """Insere os chunks com embeddings no Pinecone em lotes."""
    print(f"\n📤 Enviando {len(chunks_com_embeddings)} vetores ao Pinecone...")

    for i in range(0, len(chunks_com_embeddings), batch_size):
        lote = chunks_com_embeddings[i:i + batch_size]
        indice.upsert(vectors=lote)
        print(f"   ✅ Lote {i // batch_size + 1} enviado ({len(lote)} vetores)")

    print(f"\n🎉 Todos os vetores inseridos!")


def buscar(indice, embedding_query, top_k=5):
    """Busca os chunks mais similares a uma query."""
    resultado = indice.query(
        vector=embedding_query,
        top_k=top_k,
        include_metadata=True
    )
    return resultado.matches


if __name__ == "__main__":
    # 1. Gera embeddings
    chunks_com_embeddings = gerar_embeddings_chunks()

    # 2. Conecta ao Pinecone
    indice = conectar_pinecone()

    # 3. Insere os vetores
    inserir_chunks(indice, chunks_com_embeddings)

    # 4. Testa uma busca
    from embeddings import gerar_embedding
    print("\n🔍 Testando busca semântica...")
    query = "O que é RAG e como funciona?"
    embedding_query = gerar_embedding(query)
    resultados = buscar(indice, embedding_query, top_k=3)

    print(f"\n📋 Top 3 resultados para: '{query}'")
    for i, r in enumerate(resultados):
        print(f"\n  [{i+1}] Score: {r.score:.4f}")
        print(f"       Arquivo: {r.metadata['arquivo']}")
        print(f"       Página : {r.metadata['pagina']}")
        print(f"       Texto  : {r.metadata['texto'][:120]}...")