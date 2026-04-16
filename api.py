# ============================================================
# api.py — Backend FastAPI do IntelliDoc
# Expõe o pipeline RAG como uma API HTTP para o frontend React
# ============================================================

import sys
import os

# Adiciona a pasta src/ ao path do Python para que possamos
# importar nossos módulos (rag_pipeline, vector_store, etc.)
# sem precisar mover nenhum arquivo de lugar
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from fastapi import FastAPI, UploadFile, File  # FastAPI cria endpoints HTTP — UploadFile e File permitem receber arquivos enviados pelo frontend
from fastapi.middleware.cors import CORSMiddleware  # CORS permite que o React (rodando na porta 5173) acesse esta API (que roda na porta 8000) sem ser bloqueado pelo navegador
from pydantic import BaseModel  # BaseModel define a estrutura exata dos dados JSON que chegam e saem da API
from dotenv import load_dotenv  # Carrega as variáveis do .env (chaves OpenAI, Pinecone etc.)
import shutil  # Biblioteca padrão para manipular arquivos — usaremos para salvar uploads em data/raw/
import json  # Para ler o relatorio_ragas.json que já existe em data/processed/

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()
# ============================================================
# CRIAÇÃO DA APLICAÇÃO FASTAPI
# ============================================================

# Cria a instância principal da aplicação FastAPI
# É ela que vai "escutar" as requisições HTTP vindas do frontend React
app = FastAPI(
    title="IntelliDoc API",       # Nome que aparece na documentação automática
    description="Backend RAG do IntelliDoc — Pinecone + GPT-4o-mini",
    version="1.0.0"
)

# ============================================================
# CONFIGURAÇÃO DO CORS
# ============================================================
# CORS (Cross-Origin Resource Sharing) é uma política de segurança
# dos navegadores que bloqueia requisições entre origens diferentes.
# Exemplo: React rodando em localhost:5173 tentando acessar a API
# em localhost:8000 — sem essa configuração, o navegador bloquearia.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",   # Porta padrão do Vite (frontend React em desenvolvimento)
        "http://localhost:8080",   # Porta alternativa caso o React rode aqui
        "http://localhost:3000",   # Porta alternativa caso o React rode aqui
    ],
    allow_credentials=True,        # Permite envio de cookies e headers de autenticação
    allow_methods=["*"],           # Permite todos os métodos HTTP (GET, POST, DELETE etc.)
    allow_headers=["*"],           # Permite todos os headers HTTP
)
# ============================================================
# IMPORTAÇÃO DOS MÓDULOS DO PROJETO
# ============================================================
# Importamos apenas as funções que já existem nos módulos.
# Os nomes devem bater exatamente com o que está definido em cada arquivo.
from rag_pipeline import rag_query          # Função principal do RAG — recebe pergunta, retorna resposta + fontes
from vector_store import conectar_pinecone  # Conecta ao Pinecone e retorna o índice
from vector_store import buscar             # Busca chunks similares no Pinecone

# ============================================================
# MODELOS DE DADOS (Pydantic)
# ============================================================
# Pydantic valida automaticamente os dados que chegam na API.
# Se o frontend mandar um JSON sem o campo "pergunta", a API
# rejeita a requisição automaticamente com erro 422.

class PerguntaRequest(BaseModel):
    # Modelo para o endpoint de chat — o frontend envia este JSON:
    # { "pergunta": "O que é RAG?" }
    pergunta: str

class PerguntaResponse(BaseModel):
    # Modelo para a resposta do chat — a API devolve este JSON:
    # { "resposta": "...", "fontes": ["doc1.pdf", "doc2.pdf"] }
    resposta: str
    fontes: list[str]

# ============================================================
# ENDPOINTS DA API
# ============================================================
# Cada endpoint é uma "porta de entrada" da API.
# O frontend React vai chamar cada um desses endereços HTTP.


# ------------------------------------------------------------
# GET /
# Endpoint de health check — verifica se a API está no ar
# O frontend pode chamar isso para saber se o backend está rodando
# ------------------------------------------------------------
@app.get("/")
def raiz():
    return {"status": "online", "mensagem": "IntelliDoc API rodando!"}


# ------------------------------------------------------------
# POST /chat
# Endpoint principal — recebe a pergunta do usuário e retorna
# a resposta gerada pelo pipeline RAG (Pinecone + GPT-4o-mini)
# ------------------------------------------------------------
@app.post("/chat", response_model=PerguntaResponse)
def chat(request: PerguntaRequest):
    # request.pergunta contém o texto digitado pelo usuário no frontend
    # rag_query já faz tudo: embedding → busca Pinecone → GPT-4o-mini → resposta
    resultado = rag_query(request.pergunta)

    # rag_query retorna um dicionário com "resposta" e "fontes"
    # Aqui extraímos os dois campos e devolvemos para o frontend
    return PerguntaResponse(
        resposta=resultado["resposta"],
        fontes=resultado["fontes"]
    )


# ------------------------------------------------------------
# GET /documentos
# Retorna a lista de documentos indexados no Pinecone
# O frontend usa isso para preencher a sidebar com os arquivos
# ------------------------------------------------------------
@app.get("/documentos")
def listar_documentos():
    # Lê o arquivo de controle de ingestão que já existe no projeto
    # Ele contém os nomes e hashes de todos os arquivos indexados
    caminho_controle = os.path.join("data", "processed", "controle_ingestao.json")

    if not os.path.exists(caminho_controle):
        # Se o arquivo não existir ainda, devolve lista vazia
        return {"documentos": []}

    with open(caminho_controle, "r") as f:
        controle = json.load(f)

    # controle é um dicionário: { "arquivo.pdf": "hash_md5", ... }
    # Transformamos em lista de objetos com nome e tipo
    documentos = []
    for nome_arquivo in controle.keys():
        documentos.append({
            "nome": nome_arquivo,
            "tipo": "imagem" if nome_arquivo.lower().endswith(
                (".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp")
            ) else "pdf"
        })

    return {"documentos": documentos}


# ------------------------------------------------------------
# GET /metricas
# Retorna os scores RAGAS do último relatório gerado
# O frontend usa isso para preencher o painel "Sistema & RAGAS"
# ------------------------------------------------------------
@app.get("/metricas")
def obter_metricas():
    # Lê o relatório RAGAS que já existe em data/processed/
    caminho_ragas = os.path.join("data", "processed", "relatorio_ragas.json")

    if not os.path.exists(caminho_ragas):
        # Se ainda não houver relatório, devolve zeros
        return {
            "faithfulness": 0.0,
            "answer_relevancy": 0.0,
            "context_precision": 0.0,
            "context_recall": 0.0,
            "score_medio": 0.0
        }

    with open(caminho_ragas, "r") as f:
        relatorio = json.load(f)

    return relatorio

# ------------------------------------------------------------
# POST /upload
# Recebe um arquivo (PDF ou imagem) enviado pelo frontend,
# salva em data/raw/ e executa a ingestão completa no Pinecone
# ------------------------------------------------------------

# BackgroundTasks permite que a ingestão rode em segundo plano
# sem bloquear a resposta HTTP para o frontend
from fastapi import BackgroundTasks

# HTTPException permite retornar erros HTTP com mensagem clara
from fastapi import HTTPException

# Importa as funções de processamento que já existem no projeto
from ingest import extrair_texto_pdf, criar_chunks
from ocr import extrair_texto_imagem
from embeddings import gerar_embedding
from vector_store import (
    conectar_pinecone,
    inserir_chunks,
    calcular_hash_arquivo,
    carregar_controle,
    salvar_controle,
)

# Extensões de imagem aceitas pelo pipeline OCR
EXTENSOES_IMAGEM = {".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp"}


def _ingerir_arquivo(caminho: str, nome_arquivo: str):
    """
    Função executada em background após o upload.
    Detecta o tipo do arquivo, extrai texto, gera embeddings
    e insere no Pinecone — exatamente como o vector_store.py faz.
    """
    ext = os.path.splitext(nome_arquivo)[1].lower()

    # ── Extrai texto conforme o tipo do arquivo ────────────────
    if ext == ".pdf":
        # PDF nativo: extração direta com PyMuPDF
        paginas = extrair_texto_pdf(caminho)
    elif ext in EXTENSOES_IMAGEM:
        # Imagem: OCR com Tesseract
        texto = extrair_texto_imagem(caminho)
        # Empacota no mesmo formato que o PDF retorna
        paginas = [{"texto": texto, "pagina": 1, "arquivo": nome_arquivo}]
    else:
        # Tipo não suportado — não deveria chegar aqui por causa
        # da validação no endpoint, mas é uma garantia extra
        print(f"⚠️  Tipo não suportado: {ext}")
        return

    # ── Divide em chunks com overlap ───────────────────────────
    chunks = criar_chunks(paginas)
    print(f"  📄 {nome_arquivo} → {len(chunks)} chunks")

    # ── Gera embeddings para cada chunk ────────────────────────
    chunks_com_embedding = []
    for i, chunk in enumerate(chunks):
        emb = gerar_embedding(chunk["texto"])
        chunks_com_embedding.append({
            "id":     chunk["metadata"]["chunk_id"],
            "values": emb,
            "metadata": {
                "texto":   chunk["texto"],
                "arquivo": chunk["metadata"]["arquivo"],
                "pagina":  chunk["metadata"]["pagina"],
            }
        })

    # ── Insere no Pinecone ──────────────────────────────────────
    indice = conectar_pinecone()
    inserir_chunks(indice, chunks_com_embedding)

    # ── Atualiza o controle MD5 ─────────────────────────────────
    # Salva o hash do arquivo para que próximos uploads do mesmo
    # arquivo só reprocessem se o conteúdo tiver mudado
    controle = carregar_controle()
    controle[nome_arquivo] = calcular_hash_arquivo(caminho)
    salvar_controle(controle)

    print(f"✅ {nome_arquivo} indexado com sucesso!")


@app.post("/upload")
async def upload_documento(
    background_tasks: BackgroundTasks,
    arquivo: UploadFile = File(...)
):
    """
    Recebe um arquivo do frontend, valida o tipo,
    salva em data/raw/ e dispara a ingestão em background.
    Retorna imediatamente para não travar o frontend.
    """
    # ── Valida a extensão do arquivo ────────────────────────────
    ext = os.path.splitext(arquivo.filename)[1].lower()
    extensoes_aceitas = {".pdf"} | EXTENSOES_IMAGEM

    if ext not in extensoes_aceitas:
        # 400 Bad Request com mensagem clara para o frontend
        raise HTTPException(
            status_code=400,
            detail=f"Tipo '{ext}' não suportado. Aceitos: PDF, PNG, JPG, WEBP, BMP, TIFF"
        )

    # ── Salva o arquivo em data/raw/ ────────────────────────────
    caminho_destino = os.path.join("data", "raw", arquivo.filename)

    # Lê o conteúdo do arquivo enviado pelo frontend (bytes)
    conteudo = await arquivo.read()

    with open(caminho_destino, "wb") as f:
        f.write(conteudo)

    print(f"💾 Arquivo salvo: {caminho_destino}")

    # ── Verifica se já está indexado com mesmo hash ─────────────
    controle = carregar_controle()
    hash_novo = calcular_hash_arquivo(caminho_destino)

    if arquivo.filename in controle and controle[arquivo.filename] == hash_novo:
        # Arquivo idêntico já indexado — não precisa reprocessar
        return {
            "status": "ja_indexado",
            "arquivo": arquivo.filename,
            "mensagem": "Arquivo já estava indexado e não foi alterado."
        }

    # ── Dispara a ingestão em background ───────────────────────
    # background_tasks.add_task faz a ingestão rodar DEPOIS que
    # o frontend já recebeu a resposta HTTP — sem timeout
    background_tasks.add_task(_ingerir_arquivo, caminho_destino, arquivo.filename)

    return {
        "status": "indexando",
        "arquivo": arquivo.filename,
        "mensagem": "Arquivo recebido. Indexação em andamento..."
    }

# ------------------------------------------------------------
# DELETE /documentos/{nome}
# Remove um documento do Pinecone e do controle de ingestão.
# O parâmetro {nome} é o nome do arquivo — ex: guia_git.pdf
# ------------------------------------------------------------
@app.delete("/documentos/{nome}")
def deletar_documento(nome: str):
    """
    Remove todos os vetores do arquivo do Pinecone
    e apaga a entrada do controle de ingestão (MD5).
    """
    # ── 1. Verifica se o arquivo está no controle ───────────
    controle = carregar_controle()

    if nome not in controle:
        # 404 se o arquivo não existir no controle
        raise HTTPException(
            status_code=404,
            detail=f"Documento '{nome}' não encontrado no controle de ingestão."
        )

    # ── 2. Busca os IDs dos vetores no Pinecone por metadata ─
    # O Pinecone serverless permite deletar por filtro de metadata
    # usando o método delete() com filter= ao invés de ids=
    indice = conectar_pinecone()

    try:
        indice.delete(
            filter={"arquivo": {"$eq": nome}}
            # $eq = "equal" — deleta todos os vetores onde
            # metadata["arquivo"] == nome do arquivo enviado
        )
        print(f"🗑️  Vetores de '{nome}' removidos do Pinecone")
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao deletar vetores do Pinecone: {str(e)}"
        )

    # ── 3. Remove do controle de ingestão ───────────────────
    del controle[nome]
    salvar_controle(controle)
    print(f"✅ '{nome}' removido do controle de ingestão")

    # ── 4. Remove o arquivo físico de data/raw/ ─────────────
    # Opcional mas importante: evita que o arquivo seja
    # reingerido na próxima execução do vector_store.py
    caminho_raw = os.path.join("data", "raw", nome)
    if os.path.exists(caminho_raw):
        os.remove(caminho_raw)
        print(f"🗑️  Arquivo físico '{nome}' removido de data/raw/")

    return {
        "status": "deletado",
        "arquivo": nome,
        "mensagem": f"'{nome}' removido do Pinecone, do controle e de data/raw/."
    }