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