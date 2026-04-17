import fitz # Importa a biblioteca PyMuPDF para manipulação de PDFs
import json # Biblioteca importada para salvar os chunks em formato JSON
import os # Biblioteca importada para manipulação de arquivos e diretórios do sistema operacional
from langchain_text_splitters import RecursiveCharacterTextSplitter # Biblioteca importada apos uma decisão de usabilidade para dividir o texto em chunks menores, com overlap para manter o contexto. Isso se deu pelo fato de usarmos um Banco Vetorial no futuro


def extrair_texto_pdf(caminho_pdf): # Define a função para extrair texto de um PDF, recebendo o caminho do arquivo como argumento
    """Extrai todo o texto do PDF página por página."""
    doc = fitz.open(caminho_pdf) # Abre o PDF usando a biblioteca PyMuPDF
    nome_arquivo = os.path.basename(caminho_pdf) # Obtém o nome do arquivo a partir do caminho completo
    paginas = [] # Inicializa uma lista para armazenar o texto de cada página

    for numero_pagina in range(len(doc)): # Itera sobre cada página do PDF usando o número da página
        texto = doc[numero_pagina].get_text() # Extrai o texto da página atual usando o método get_text() da biblioteca PyMuPDF
        if texto.strip(): # Verifica se o texto extraído não está vazio (após remover espaços em branco)
            paginas.append({ # Adiciona um dicionário à lista de páginas, contendo o texto, número da página e nome do arquivo
                "texto": texto,
                "pagina": numero_pagina + 1,
                "arquivo": nome_arquivo
            })

    doc.close() # Fecha o documento PDF para liberar recursos do sistema
    return paginas # Retorna a lista de páginas, onde cada página é representada por um dicionário contendo o texto, número da página e nome do arquivo


def criar_chunks(paginas, chunk_size=500, chunk_overlap=50): # Define a função para criar chunks a partir do texto extraído, recebendo a lista de páginas, o tamanho do chunk e o overlap como argumentos, no caso da nossa função o tamanho do chunk é de 500 caracteres, com um overlap de 50 caracteres para manter o contexto entre os chunks foi definido em 500 caracteres, com um overlap de 50 caracteres para manter o contexto entre os chunks. Esses valores podem ser ajustados conforme necessário, dependendo do tamanho médio dos textos e do contexto que se deseja preservar.
    """Divide o texto em chunks menores com overlap."""
    splitter = RecursiveCharacterTextSplitter( # Cria uma instância do RecursiveCharacterTextSplitter, configurando o tamanho do chunk, o overlap e os separadores para dividir o texto de forma eficiente, mantendo o contexto entre os chunks.
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ".", " "] # Define os separadores para dividir o texto, priorizando quebras de parágrafo, depois quebras de linha, pontos e espaços, para criar chunks mais naturais e coerentes.
    ) # Para essa função, o texto não será dividido em exatos 500 caracteres, mas sim em pedaços que se aproximem desse tamanho, respeitando os separadores definidos para manter a coerência do texto. O overlap de 50 caracteres garante que haja uma sobreposição entre os chunks, o que é importante para preservar o contexto e evitar que informações importantes sejam cortadas entre os chunks.

    chunks = [] # Inicializa uma lista para armazenar os chunks gerados a partir do texto das páginas
    for pagina in paginas: # Itera sobre cada página da lista de páginas, onde cada página é representada por um dicionário contendo o texto, número da página e nome do arquivo
        pedacos = splitter.split_text(pagina["texto"]) # Usa o método split_text() do splitter para dividir o texto da página em pedaços menores (chunks) de acordo com a configuração definida, retornando uma lista de pedaços de texto.

        for i, pedaco in enumerate(pedacos): # Itera sobre cada pedaço de texto gerado a partir da página, usando a função enumerate() para obter o índice do pedaço (i) e o próprio pedaço de texto (pedaco).
            if len(pedaco.strip()) < 30: # Verifica se o pedaço de texto é muito curto (menos de 30 caracteres após remover espaços em branco), e se for, ignora esse pedaço para evitar criar chunks com pouco conteúdo ou que sejam irrelevantes.
                continue
            chunks.append({
                "texto": pedaco.strip(),
                "metadata": {
                    "arquivo": pagina["arquivo"],
                    "pagina": pagina["pagina"],
                    "chunk_id": f"{pagina['arquivo']}_p{pagina['pagina']}_c{i}" # ID do chunk gerado, esse id é utilizado posteriomente no Pinecone para facilitar a busca e identificação do chunk, ele é composto pelo nome do arquivo, número da página e índice do chunk dentro daquela página, garantindo que cada chunk tenha um identificador único e fácil de rastrear.
                }
            })

    return chunks


def processar_todos_arquivos(pasta_raw="data/raw"):
    """
    Processa todos os arquivos de data/raw/ — PDFs e imagens.
    Retorna uma lista unificada de chunks com metadados,
    independente do tipo de arquivo de origem.
    """
    from ocr import processar_imagens_pasta   # Importa o módulo de OCR

    print(f"📂 Verificando arquivos em {pasta_raw}...\n")

    todos_chunks = []

    # ── Processa PDFs ─────────────────────────────────────────────
    pdfs = [f for f in os.listdir(pasta_raw) if f.endswith(".pdf")]

    if pdfs:
        print(f"📄 {len(pdfs)} PDF(s) encontrado(s)")
        for pdf in pdfs:
            caminho = os.path.join(pasta_raw, pdf)
            paginas = extrair_texto_pdf(caminho)
            chunks  = criar_chunks(paginas)
            todos_chunks.extend(chunks)
            print(f"   ✅ {pdf} → {len(chunks)} chunks")
    else:
        print("📄 Nenhum PDF encontrado")

    print()

    # ── Processa Imagens via OCR ───────────────────────────────────
    extensoes_img = {".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp"}
    imagens = [
        f for f in os.listdir(pasta_raw)
        if os.path.splitext(f)[1].lower() in extensoes_img
    ]

    if imagens:
        print(f"🖼️  {len(imagens)} imagem(ns) encontrada(s)")
        paginas_ocr = processar_imagens_pasta(pasta_raw)
        chunks_ocr  = criar_chunks(paginas_ocr)
        todos_chunks.extend(chunks_ocr)
        print(f"   ✅ {len(imagens)} imagem(ns) → {len(chunks_ocr)} chunks")
    else:
        print("🖼️  Nenhuma imagem encontrada")

    print(f"\n📊 Total de chunks gerados: {len(todos_chunks)}")
    return todos_chunks


if __name__ == "__main__":
    chunks = processar_todos_arquivos()

    if chunks:
        print(f"\n📋 Exemplo de chunk:")
        print(f"   Arquivo : {chunks[5]['metadata']['arquivo']}")
        print(f"   Página  : {chunks[5]['metadata']['pagina']}")
        print(f"   Texto   : {chunks[5]['texto'][:150]}...")