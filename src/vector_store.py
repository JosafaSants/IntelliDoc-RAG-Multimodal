import ssl # Biblioteca importada para lidar com conexões corporativas que podem ter problemas de certificado SSL, garantindo que as conexões HTTPS funcionem corretamente ao interagir com a API do Pinecone.
import certifi # Biblioteca que fornece certificados SSL atualizados, usada para resolver problemas de certificado em conexões HTTPS, especialmente em ambientes corporativos onde os certificados podem ser desatualizados ou personalizados.
import os

os.environ['SSL_CERT_FILE'] = certifi.where() # Define a variável de ambiente SSL_CERT_FILE para apontar para o arquivo de certificados fornecido pelo certifi, garantindo que as conexões HTTPS usem os certificados corretos e atualizados, o que é crucial para evitar erros de certificado ao se conectar ao Pinecone ou outras APIs externas.
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where() # Define a variável de ambiente REQUESTS_CA_BUNDLE para apontar para o mesmo arquivo de certificados do certifi, garantindo que a biblioteca requests (usada internamente pelo Pinecone e outras bibliotecas) também utilize os certificados corretos para conexões HTTPS, evitando erros de certificado em ambientes corporativos.
ssl._create_default_https_context = ssl.create_default_context # Cria um contexto SSL padrão usando a função create_default_context do módulo ssl, garantindo que as conexões HTTPS usem as configurações de segurança adequadas, o que é especialmente importante em ambientes corporativos onde os certificados podem ser personalizados ou desatualizados. Essa linha é uma medida adicional para garantir que as conexões HTTPS funcionem corretamente ao interagir com a API do Pinecone ou outras APIs externas, mesmo em ambientes com configurações de segurança mais rigorosas.

from pinecone import Pinecone, ServerlessSpec # Busca na biblioteca oficial do Pinecone as classes necessárias para se conectar e interagir com o serviço de banco vetorial, onde Pinecone é a classe principal para criar clientes e índices, e ServerlessSpec é usada para especificar as configurações do índice, como a nuvem e região onde ele será criado.
from dotenv import load_dotenv 
from embeddings import gerar_embeddings_chunks # Importa a função gerar_embeddings_chunks do script embeddings.py, que é responsável por carregar os chunks de texto processados e gerar os embeddings usando a API da OpenAI. Esses embeddings serão usados para inserir os vetores no banco vetorial do Pinecone e realizar buscas semânticas posteriormente.

load_dotenv()


def conectar_pinecone(): # Define a função conectar_pinecone, que é responsável por estabelecer a conexão com o serviço de banco vetorial do Pinecone e garantir que o índice necessário para armazenar os embeddings esteja criado. Essa função verifica se o índice já existe e, se não existir, cria um novo índice com as especificações adequadas (dimensão do vetor, métrica de similaridade e configurações de nuvem e região). O índice é essencial para armazenar os vetores de embedding gerados a partir dos chunks de texto e permitir buscas semânticas eficientes posteriormente.
    """Conecta ao Pinecone e retorna o índice."""
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    nome_indice = os.getenv("PINECONE_INDEX_NAME", "intellidoc")

    # Cria o índice se não existir
    indices_existentes = [i.name for i in pc.list_indexes()] # Busca a lista de índices existentes no Pinecone usando o método list_indexes do cliente Pinecone, e extrai apenas os nomes dos índices para verificar se o índice necessário para este projeto já existe. Isso é importante para evitar criar índices duplicados e garantir que o índice correto seja usado para armazenar os embeddings gerados a partir dos chunks de texto.

    if nome_indice not in indices_existentes: # Verifica se o nome do índice desse chunk já existe na lista de índice existente.
        print(f"📦 Criando índice '{nome_indice}'...")
        pc.create_index( # Função para criar o novo indice no Pinecone
            name=nome_indice,
            dimension=1536, # Dimensão definida pelo modelo de embedding utilizado (text-embedding-3-small da OpenAI)
            metric="cosine", # Métrica de similaridade escolhida para as buscas
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