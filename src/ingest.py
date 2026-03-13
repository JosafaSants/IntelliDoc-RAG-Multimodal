import fitz  # PyMuPDF
import json
import os
from langchain_text_splitters import RecursiveCharacterTextSplitter


def extrair_texto_pdf(caminho_pdf):
    """Extrai todo o texto do PDF página por página."""
    doc = fitz.open(caminho_pdf)
    nome_arquivo = os.path.basename(caminho_pdf)
    paginas = []

    for numero_pagina in range(len(doc)):
        texto = doc[numero_pagina].get_text()
        if texto.strip():
            paginas.append({
                "texto": texto,
                "pagina": numero_pagina + 1,
                "arquivo": nome_arquivo
            })

    doc.close()
    return paginas


def criar_chunks(paginas, chunk_size=500, chunk_overlap=50):
    """Divide o texto em chunks menores com overlap."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ".", " "]
    )

    chunks = []
    for pagina in paginas:
        pedacos = splitter.split_text(pagina["texto"])

        for i, pedaco in enumerate(pedacos):
            if len(pedaco.strip()) < 30:
                continue
            chunks.append({
                "texto": pedaco.strip(),
                "metadata": {
                    "arquivo": pagina["arquivo"],
                    "pagina": pagina["pagina"],
                    "chunk_id": f"{pagina['arquivo']}_p{pagina['pagina']}_c{i}"
                }
            })

    return chunks


def processar_todos_pdfs(pasta_raw="data/raw", pasta_processed="data/processed"):
    """Processa todos os PDFs de uma pasta e salva os chunks."""
    pdfs = [f for f in os.listdir(pasta_raw) if f.endswith(".pdf")]

    if not pdfs:
        print("❌ Nenhum PDF encontrado em data/raw/")
        return []

    print(f"📂 {len(pdfs)} PDF(s) encontrado(s):\n")

    todos_chunks = []

    for pdf in pdfs:
        caminho = os.path.join(pasta_raw, pdf)
        paginas = extrair_texto_pdf(caminho)
        chunks = criar_chunks(paginas)
        todos_chunks.extend(chunks)
        print(f"  ✅ {pdf}")
        print(f"     Páginas: {len(paginas)} | Chunks: {len(chunks)}")

    # Salva tudo em um único JSON
    caminho_saida = os.path.join(pasta_processed, "chunks.json")
    with open(caminho_saida, "w", encoding="utf-8") as f:
        json.dump(todos_chunks, f, ensure_ascii=False, indent=2)

    print(f"\n📊 Resumo Final:")
    print(f"   PDFs processados : {len(pdfs)}")
    print(f"   Total de chunks  : {len(todos_chunks)}")
    print(f"   Arquivo gerado   : {caminho_saida}")

    return todos_chunks


if __name__ == "__main__":
    chunks = processar_todos_pdfs()

    if chunks:
        print(f"\n📋 Exemplo de chunk:")
        print(f"   Arquivo : {chunks[5]['metadata']['arquivo']}")
        print(f"   Página  : {chunks[5]['metadata']['pagina']}")
        print(f"   Texto   : {chunks[5]['texto'][:150]}...")