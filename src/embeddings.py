import os # Biblioteca para acessar as variáveis de ambiente do sistema operacional
import json # Biblioteca para manipulação dos JSONs que armazenam os chunks e embeddings
from openai import OpenAI # Biblioteca oficial da OpenAI para interagir com a API de embeddings
from dotenv import load_dotenv # Biblioteca para carregar as variáveis de ambiente de um arquivo .env

load_dotenv() # Carrega as variáveis de ambiente do arquivo .env, incluindo a chave da API da OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY")) # Busca a chave da API da OpenAI das variáveis de ambiente e inicializa o cliente para fazer chamadas à API


def gerar_embedding(texto): 
    """Gera embedding de um texto usando OpenAI."""
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=texto
    )
    return response.data[0].embedding # Coração do projeto, basicamente essa função vai utilizar a API da OpenAI para gerar um vetor de embedding a partir do texto do chunk, que depois será armazenado junto com o metadata para facilitar as buscas semânticas


def gerar_embeddings_chunks(caminho_chunks="data/processed/chunks.json"):
    """Carrega os chunks e gera embeddings para cada um."""
    with open(caminho_chunks, "r", encoding="utf-8") as f:
        chunks = json.load(f) # Carrega os chunks do arquivo JSON gerado na etapa de ingestão, onde cada chunk é um pedaço de texto extraído dos PDFs, junto com seu metadata (arquivo, página e ID do chunk). Esses chunks serão usados para gerar os embeddings que serão armazenados em um banco vetorial para buscas semânticas.

    print(f"📦 {len(chunks)} chunks carregados")
    print("🔢 Gerando embeddings...\n")

    chunks_com_embeddings = [] # Cria uma nova lista para armazenar os chunks junto com seus embeddings gerados. Cada item dessa lista será um dicionário contendo o ID do chunk, o vetor de embedding e o metadata (texto, arquivo e página) para facilitar as buscas semânticas posteriormente.

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
        }) # Popula a lista de chunks_com_embeddings com um dicionário para cada chunk, contendo o ID do chunk, o vetor de embedding gerado e o metadata (texto, arquivo e página) para facilitar as buscas semânticas posteriormente.

        # Progresso a cada 10 chunks
        if (i + 1) % 10 == 0 or (i + 1) == len(chunks):
            print(f"   ✅ {i + 1}/{len(chunks)} embeddings gerados")

    print(f"\n🎉 Todos os embeddings prontos!")
    print(f"   Dimensão do vetor: {len(chunks_com_embeddings[0]['values'])}")
    return chunks_com_embeddings


if __name__ == "__main__": # Trecho destinado para teste de execução do módulo, onde ao rodar o script diretamente, ele irá carregar os chunks do arquivo JSON, gerar os embeddings para cada chunk e imprimir um exemplo do resultado.
    chunks_com_embeddings = gerar_embeddings_chunks()
    print(f"\n📋 Exemplo:")
    print(f"   ID     : {chunks_com_embeddings[0]['id']}")
    print(f"   Vetor  : {chunks_com_embeddings[0]['values'][:5]}...")
    print(f"   Arquivo: {chunks_com_embeddings[0]['metadata']['arquivo']}")