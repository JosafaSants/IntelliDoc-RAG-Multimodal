import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def gerar_embedding(texto):
    """Gera embedding de um texto usando OpenAI."""
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=texto
    )
    return response.data[0].embedding


def gerar_embeddings_chunks(caminho_chunks="data/processed/chunks.json"):
    """Carrega os chunks e gera embeddings para cada um."""
    with open(caminho_chunks, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    print(f"📦 {len(chunks)} chunks carregados")
    print("🔢 Gerando embeddings...\n")

    chunks_com_embeddings = []

    for i, chunk in enumerate(chunks):
        embedding = gerar_embedding(chunk["texto"])
        chunks_com_embeddings.append({
            "id": chunk["metadata"]["chunk_id"],
            "values": embedding,
            "metadata": {
                "texto": chunk["texto"],
                "arquivo": chunk["metadata"]["arquivo"],
                "pagina": chunk["metadata"]["pagina"]
            }
        })

        # Progresso a cada 10 chunks
        if (i + 1) % 10 == 0 or (i + 1) == len(chunks):
            print(f"   ✅ {i + 1}/{len(chunks)} embeddings gerados")

    print(f"\n🎉 Todos os embeddings prontos!")
    print(f"   Dimensão do vetor: {len(chunks_com_embeddings[0]['values'])}")
    return chunks_com_embeddings


if __name__ == "__main__":
    chunks_com_embeddings = gerar_embeddings_chunks()
    print(f"\n📋 Exemplo:")
    print(f"   ID     : {chunks_com_embeddings[0]['id']}")
    print(f"   Vetor  : {chunks_com_embeddings[0]['values'][:5]}...")
    print(f"   Arquivo: {chunks_com_embeddings[0]['metadata']['arquivo']}")