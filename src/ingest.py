import fitz  # PyMuPDF
import json
import os
from langchain_text_splitters import RecursiveCharacterTextSplitter

def extrair_texto_pdf(caminho_pdf):
    """Extrai todo o texto do PDF página por página."""
    doc = fitz.open(caminho_pdf)
    nome_arquivo = os.path.basename(caminho_pdf)
    paginas = []

    print(f"📄 Processando: {nome_arquivo}")
    print(f"   Total de páginas: {len(doc)}")

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


def salvar_chunks(chunks, caminho_saida):
    """Salva os chunks em JSON."""
    with open(caminho_saida, 'w', encoding='utf-8') as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)
    print(f"✅ Chunks salvos em: {caminho_saida}")


if __name__ == "__main__":
    caminho_pdf = "data/raw/manual_tecnico_ia.pdf"
    caminho_saida = "data/processed/chunks.json"

    paginas = extrair_texto_pdf(caminho_pdf)
    chunks = criar_chunks(paginas)

    print(f"   Chunks gerados: {len(chunks)}")

    print("\n📋 Preview dos primeiros 2 chunks:")
    for chunk in chunks[:2]:
        print(f"\n--- Chunk (Página {chunk['metadata']['pagina']}) ---")
        print(chunk['texto'][:200])

    salvar_chunks(chunks, caminho_saida)