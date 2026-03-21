import ssl # Biblioteca importada para lidar com conexões corporativas que podem ter problemas de certificado SSL, garantindo que as conexões HTTPS funcionem corretamente ao interagir com a API do Pinecone.
import certifi # Biblioteca que fornece certificados SSL atualizados, usada para resolver problemas de certificado em conexões HTTPS, especialmente em ambientes corporativos onde os certificados podem ser desatualizados ou personalizados.
import os

os.environ['SSL_CERT_FILE'] = certifi.where() # Define a variável de ambiente SSL_CERT_FILE para apontar para o arquivo de certificados fornecido pelo certifi, garantindo que as conexões HTTPS usem os certificados corretos e atualizados, o que é crucial para evitar erros de certificado ao se conectar ao Pinecone ou outras APIs externas.
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where() # Define a variável de ambiente REQUESTS_CA_BUNDLE para apontar para o mesmo arquivo de certificados do certifi, garantindo que a biblioteca requests (usada internamente pelo Pinecone e outras bibliotecas) também utilize os certificados corretos para conexões HTTPS, evitando erros de certificado em ambientes corporativos.
ssl._create_default_https_context = ssl.create_default_context # Cria um contexto SSL padrão usando a função create_default_context do módulo ssl, garantindo que as conexões HTTPS usem as configurações de segurança adequadas, o que é especialmente importante em ambientes corporativos onde os certificados podem ser personalizados ou desatualizados. Essa linha é uma medida adicional para garantir que as conexões HTTPS funcionem corretamente ao interagir com a API do Pinecone ou outras APIs externas, mesmo em ambientes com configurações de segurança mais rigorosas.

from pinecone import Pinecone, ServerlessSpec # Busca na biblioteca oficial do Pinecone as classes necessárias para se conectar e interagir com o serviço de banco vetorial, onde Pinecone é a classe principal para criar clientes e índices, e ServerlessSpec é usada para especificar as configurações do índice, como a nuvem e região onde ele será criado.
from dotenv import load_dotenv 
from embeddings import gerar_embeddings_chunks # Importa a função gerar_embeddings_chunks do script embeddings.py, que é responsável por carregar os chunks de texto processados e gerar os embeddings usando a API da OpenAI. Esses embeddings serão usados para inserir os vetores no banco vetorial do Pinecone e realizar buscas semânticas posteriormente.

import hashlib # Biblioteca importada para auxiliar a verificar a atualização dos arquivos PDF
import json # Biblioteca importada para manipular o arquivo de controle de ingestão
import os

CONTROLE_PATH = "data/processed/controle_ingestao.json" # Define o caminho para o arquivo de controle de ingestão

def calcular_hash_arquivo(caminho):
    """Calcula o hash MD5 de um arquivo para detectar mudanças."""
    hash_md5 = hashlib.md5() # Cria um objeto de hash MD5 usando a função md5 da biblioteca hashlib, que será usado para calcular o hash do arquivo PDF.
    with open(caminho, "rb") as f:
        for bloco in iter(lambda: f.read(4096), b""): # Lê o arquivo em blocos de 4096 bytes usando um iterador, o que é eficiente para arquivos grandes, e atualiza o hash MD5 com cada bloco lido. Isso permite calcular o hash do arquivo completo sem precisar carregá-lo inteiro na memória.
            hash_md5.update(bloco)
    return hash_md5.hexdigest() # Retorna o hash do arquivo em formato hexadecimal


def carregar_controle():
    """Carrega o arquivo de controle de ingestão."""
    if os.path.exists(CONTROLE_PATH): # Verifica se o arquivo de controle de ingestão existe
        with open(CONTROLE_PATH, "r") as f:
            return json.load(f) # Se o arquivo existir, ele é aberto e seu conteúdo é carregado usando json.load, retornando um dicionário que mapeia os nomes dos arquivos PDF para seus respectivos hashes MD5. Isso permite comparar os hashes atuais dos arquivos PDF com os hashes armazenados no controle para detectar quais arquivos foram alterados ou adicionados.
    return {}


def salvar_controle(controle):
    """Salva o arquivo de controle de ingestão."""
    with open(CONTROLE_PATH, "w") as f:
        json.dump(controle, f, indent=2) # Salva o dicionário de controle de ingestão no arquivo especificado por CONTROLE_PATH, usando json.dump para escrever o dicionário em formato JSON com uma indentação de 2 espaços para facilitar a leitura. Isso atualiza o controle com os hashes atuais dos arquivos PDF, permitindo que futuras execuções do script possam detectar alterações ou adições nos arquivos PDF comparando os hashes atuais com os armazenados no controle.


def filtrar_pdfs_alterados(pasta_raw="data/raw"):
    """
    Compara o hash atual dos PDFs com o controle salvo.
    Retorna apenas os arquivos que foram adicionados ou alterados.
    """
    controle = carregar_controle() # Usa a função definida anteriormente para carregar o arquivo de controle de ingestão
    pdfs_todos = [f for f in os.listdir(pasta_raw) if f.endswith(".pdf")] # Lista os arquivos .pdf na pasta_raw

    novos_ou_alterados = [] # Cria uma lista vazia para armazenar os arquivos que foram considerados como novos ou sofreram alterações.
    sem_alteracao = [] # Cria uma lista vazi para armazenar os arquivos que não sofreram alterações

    for pdf in pdfs_todos: # Faz o controle de ingestão dos arquivos PDF
        caminho = os.path.join(pasta_raw, pdf) 
        hash_atual = calcular_hash_arquivo(caminho)

        if pdf not in controle or controle[pdf] != hash_atual:
            novos_ou_alterados.append(pdf)
        else:
            sem_alteracao.append(pdf)

    print(f"📂 {len(pdfs_todos)} PDF(s) encontrado(s):")
    for pdf in sem_alteracao:
        print(f"  ⏭️  {pdf} — sem alterações, pulando")
    for pdf in novos_ou_alterados:
        status = "🆕 novo" if pdf not in controle else "♻️  alterado"
        print(f"  {status} — {pdf}")

    return novos_ou_alterados, controle

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


def inserir_chunks(indice, chunks_com_embeddings, batch_size=50): # Defini a função de carga no Pinecone e o tamanho do lote dessa carga.
    """Insere os chunks com embeddings no Pinecone em lotes."""
    print(f"\n📤 Enviando {len(chunks_com_embeddings)} vetores ao Pinecone...")

    for i in range(0, len(chunks_com_embeddings), batch_size): # Divide o chunks_com_embedding em lotes dos tamanhos definidos por batch_size.
        lote = chunks_com_embeddings[i:i + batch_size] # Seleciona o lote atual de chunks com embeddings para serem inseridos no Pinecone.
        indice.upsert(vectors=lote) # Usa o método upsert do índice do Pinecone para inserir ou atualizar os vetores do lote atual. O método upsert é eficiente para lidar com inserções em massa, permitindo que os vetores sejam adicionados ao índice de forma rápida e sem a necessidade de verificar individualmente se cada vetor já existe.
        print(f"   ✅ Lote {i // batch_size + 1} enviado ({len(lote)} vetores)")

    print(f"\n🎉 Todos os vetores inseridos!")


def buscar(indice, embedding_query, top_k=5): # Define a função de busca semântica, que recebe o índice do Pinecone, o embedding da query e o número de resultados mais similares a serem retornados (top_k). Essa função utiliza o método query do índice do Pinecone para buscar os vetores mais similares ao embedding da query, retornando os resultados com suas respectivas metadados, como o texto original do chunk e o nome do arquivo de onde ele foi extraído. A busca semântica é fundamental para permitir que os usuários encontrem informações relevantes mesmo que as palavras exatas não estejam presentes na query, baseando-se na similaridade dos significados representados pelos embeddings.
    """Busca os chunks mais similares a uma query."""
    resultado = indice.query(
        vector=embedding_query, # Embedding da query que buscara no banco do Pinecone os vetores mais similares.
        top_k=top_k, # Retorna apena os resultado mais similares devinidos por top_k.
        include_metadata=True # Retorna os metadados dos vetores encontrados.
    )
    return resultado.matches


if __name__ == "__main__":
    import sys
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from ingest import processar_todos_arquivos  # Agora usa PDFs + imagens
    from embeddings import gerar_embedding

    pasta_raw = os.path.join("data", "raw")

    # 1. Verifica quais arquivos foram alterados (PDFs e imagens)
    pdfs_alterados, controle = filtrar_pdfs_alterados(pasta_raw)

    # 2. Verifica imagens alteradas também
    extensoes_img = {".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp"}
    imagens_alteradas = [
        f for f in os.listdir(pasta_raw)
        if os.path.splitext(f)[1].lower() in extensoes_img
        and (f not in controle or controle[f] != calcular_hash_arquivo(
            os.path.join(pasta_raw, f)
        ))
    ]

    arquivos_alterados = pdfs_alterados + imagens_alteradas

    if not arquivos_alterados:
        print("\n✅ Nenhum arquivo novo ou alterado. Pinecone já está atualizado!")
    else:
        # 3. Processa apenas os arquivos alterados
        from ingest import extrair_texto_pdf, criar_chunks
        from ocr import extrair_texto_imagem

        todos_chunks = []
        extensoes_img_set = {".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp"}

        for arquivo in arquivos_alterados:
            caminho = os.path.join(pasta_raw, arquivo)
            ext     = os.path.splitext(arquivo)[1].lower()

            if ext == ".pdf":
                # Processa PDF normalmente
                paginas = extrair_texto_pdf(caminho)
            else:
                # Processa imagem via OCR
                texto = extrair_texto_imagem(caminho)
                paginas = [{"texto": texto, "pagina": 1, "arquivo": arquivo}]

            chunks = criar_chunks(paginas)
            todos_chunks.extend(chunks)
            print(f"  ✅ {arquivo} → {len(chunks)} chunks")

        # 4. Gera embeddings apenas para os chunks alterados
        print(f"\n🔢 Gerando embeddings para {len(todos_chunks)} chunks...")
        chunks_filtrados = []

        for i, chunk in enumerate(todos_chunks):
            emb = gerar_embedding(chunk["texto"])
            chunks_filtrados.append({
                "id":     chunk["metadata"]["chunk_id"],
                "values": emb,
                "metadata": {
                    "texto":   chunk["texto"],
                    "arquivo": chunk["metadata"]["arquivo"],
                    "pagina":  chunk["metadata"]["pagina"]
                }
            })
            if (i + 1) % 10 == 0 or (i + 1) == len(todos_chunks):
                print(f"   ✅ {i + 1}/{len(todos_chunks)} embeddings gerados")

        # 5. Conecta e insere no Pinecone
        indice = conectar_pinecone()
        inserir_chunks(indice, chunks_filtrados)

        # 6. Atualiza o controle com os novos hashes
        for arquivo in arquivos_alterados:
            caminho = os.path.join(pasta_raw, arquivo)
            controle[arquivo] = calcular_hash_arquivo(caminho)
        salvar_controle(controle)
        print(f"\n💾 Controle de ingestão atualizado!")

    # 7. Testa busca semântica
    print("\n🔍 Testando busca semântica...")
    indice = conectar_pinecone()
    emb    = gerar_embedding("O que é RAG e como funciona?")
    resultados = buscar(indice, emb, top_k=3)

    print(f"\n📋 Top 3 resultados:")
    for i, r in enumerate(resultados):
        print(f"\n  [{i+1}] Score: {r.score:.4f}")
        print(f"       Arquivo: {r.metadata['arquivo']}")
        print(f"       Texto  : {r.metadata['texto'][:100]}...")