# src/memory.py
# Camada de persistência do histórico de conversas usando SQLite
# Banco de dados local — zero dependências externas, zero custo de API

import sqlite3  # Módulo nativo do Python — não precisa instalar nada
import os
from datetime import datetime

# ------------------------------------------------------------------
# CONFIGURAÇÃO DO BANCO
# ------------------------------------------------------------------

# Caminho do arquivo .db — fica junto com os outros dados processados
DB_PATH = os.path.join("data", "processed", "historico.db")

def conectar() -> sqlite3.Connection:
    """
    Abre (ou cria) a conexão com o banco SQLite.
    O arquivo .db é criado automaticamente se não existir.
    """
    # check_same_thread=False é necessário porque o FastAPI usa threads diferentes
    return sqlite3.connect(DB_PATH, check_same_thread=False)


# ------------------------------------------------------------------
# CRIAÇÃO DA TABELA
# ------------------------------------------------------------------

def inicializar_banco() -> None:
    """
    Cria a tabela 'conversas' se ela ainda não existir.
    Deve ser chamada uma vez na inicialização da aplicação.
    """
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversas (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            pergunta  TEXT    NOT NULL,
            resposta  TEXT    NOT NULL,
            fontes    TEXT,               -- JSON serializado: lista de strings
            criado_em TEXT    NOT NULL    -- ISO 8601: "2025-01-17T14:30:00"
        )
    """)

    conn.commit()
    conn.close()


# ------------------------------------------------------------------
# ESCRITA
# ------------------------------------------------------------------

def salvar_mensagem(pergunta: str, resposta: str, fontes: list[str]) -> None:
    """
    Salva um par pergunta/resposta no banco.
    Chamada após cada resposta do pipeline RAG.
    """
    import json  # Import local — só carrega quando necessário

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO conversas (pergunta, resposta, fontes, criado_em)
        VALUES (?, ?, ?, ?)
    """, (
        pergunta,
        resposta,
        json.dumps(fontes, ensure_ascii=False),  # Lista → string JSON
        datetime.now().isoformat()               # Timestamp preciso
    ))

    conn.commit()
    conn.close()


# ------------------------------------------------------------------
# LEITURA
# ------------------------------------------------------------------

def carregar_historico(limite: int = 20) -> list[dict]:
    """
    Retorna as últimas N mensagens, da mais antiga para a mais recente.
    Limite padrão: 20 mensagens — evita contexto gigante no GPT.

    Retorna lista de dicts:
    [{"pergunta": "...", "resposta": "...", "fontes": [...], "criado_em": "..."}]
    """
    import json

    conn = conectar()
    cursor = conn.cursor()

    # ORDER BY id DESC LIMIT → pega as mais recentes
    # ORDER BY id ASC no subquery → devolve em ordem cronológica
    cursor.execute("""
        SELECT pergunta, resposta, fontes, criado_em
        FROM (
            SELECT * FROM conversas
            ORDER BY id DESC
            LIMIT ?
        )
        ORDER BY id ASC
    """, (limite,))

    rows = cursor.fetchall()
    conn.close()

    historico = []
    for pergunta, resposta, fontes_json, criado_em in rows:
        historico.append({
            "pergunta":  pergunta,
            "resposta":  resposta,
            "fontes":    json.loads(fontes_json) if fontes_json else [],
            "criado_em": criado_em
        })

    return historico


# ------------------------------------------------------------------
# LIMPEZA
# ------------------------------------------------------------------

def limpar_historico() -> None:
    """
    Apaga todas as conversas do banco.
    Chamada pelo endpoint DELETE /historico.
    """
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM conversas")
    conn.commit()
    conn.close()

# ------------------------------------------------------------------
# TESTE LOCAL
# ------------------------------------------------------------------

if __name__ == "__main__":
    inicializar_banco()
    print("Banco inicializado com sucesso!")

    salvar_mensagem(
        pergunta="O que é RAG?",
        resposta="RAG é uma técnica que combina busca semântica com geração de texto.",
        fontes=["doc1.pdf", "doc2.pdf"]
    )
    print("Mensagem salva!")

    historico = carregar_historico()
    print(f"Histórico: {historico}")