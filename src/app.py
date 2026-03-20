import streamlit as st # Biblioteca para criar a interface web do projeto
import sys 
import os
import json
import tempfile # Biblioteca para utilizar arquivos temporários

from dotenv import load_dotenv

# Adiciona o diretório src ao path para importar os módulos do projeto
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ingest import extrair_texto_pdf, criar_chunks # Insere algumas funções definidas em ingest.py para processar os PDFs
from vector_store import conectar_pinecone, inserir_chunks, buscar, filtrar_pdfs_alterados, calcular_hash_arquivo, carregar_controle, salvar_controle # Insere algumas funções definidas em vector_store.py para lidar com o armazenamento e consulta dos embeddings
from embeddings import gerar_embedding # Insere a função definida em embeddings.py para gerar os embeddings dos chunks de texto
from rag_pipeline import rag_query # Insere a função definida em rag_pipeline.py para processar as perguntas do usuário e gerar as respostas usando o modelo de linguagem

load_dotenv()

# ════════════════════════════════════════════════════════════════════
# CONFIGURAÇÃO DA PÁGINA — PRIMEIRA LINHA OBRIGATÓRIA DO STREAMLIT
# ════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="IntelliDoc RAG",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"   # sidebar SEMPRE começa aberta
)

# ════════════════════════════════════════════════════════════════════
# CSS — estiliza componentes NATIVOS do Streamlit
# Regra: zero HTML dentro de containers. Só componentes nativos.
# ════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;600;700&family=JetBrains+Mono:ital,wght@0,300;0,400;0,500;1,300&display=swap');

* { font-family: 'JetBrains Mono', monospace !important; }
#MainMenu, footer, header { visibility: hidden !important; }
.stDeployButton { display: none !important; }

/* Fundo geral */
.stApp { background-color: #0d1117 !important; }

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #161b22 !important;
    border-right: 1px solid #21262d !important;
    min-width: 260px !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding: 1rem 0.9rem !important;
}

/* FORÇA a sidebar a ficar visível — impede colapso automático */
[data-testid="stSidebar"][aria-expanded="false"] {
    margin-left: 0 !important;
    transform: none !important;
}

/* Expanders na sidebar */
[data-testid="stExpander"] {
    background: #0d1117 !important;
    border: 1px solid #21262d !important;
    border-radius: 6px !important;
    margin-bottom: 6px !important;
}
[data-testid="stExpander"] summary {
    font-family: 'Rajdhani', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.78rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
    color: #8b949e !important;
    padding: 8px 10px !important;
}
[data-testid="stExpander"] summary:hover { color: #58a6ff !important; }
[data-testid="stExpander"] summary svg { color: #484f58 !important; }

/* Métricas */
[data-testid="stMetric"] {
    background: #161b22 !important;
    border: 1px solid #21262d !important;
    border-radius: 6px !important;
    padding: 8px 10px !important;
}
[data-testid="stMetricValue"] {
    color: #58a6ff !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 1.5rem !important;
    font-weight: 700 !important;
}
[data-testid="stMetricLabel"] {
    color: #484f58 !important;
    font-size: 0.62rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
}

/* Botões */
.stButton > button {
    background: #21262d !important;
    color: #58a6ff !important;
    border: 1px solid #30363d !important;
    border-radius: 6px !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.06em !important;
    transition: all 0.15s !important;
    width: 100% !important;
}
.stButton > button:hover {
    background: #30363d !important;
    border-color: #58a6ff !important;
    color: #79c0ff !important;
    transform: translateY(-1px) !important;
}

/* Chat messages */
[data-testid="stChatMessage"] {
    background: #161b22 !important;
    border: 1px solid #21262d !important;
    border-radius: 8px !important;
    margin-bottom: 6px !important;
}
[data-testid="stChatMessageContent"] p {
    color: #e6edf3 !important;
    line-height: 1.7 !important;
}

/* Campo de input */
[data-testid="stChatInput"] textarea {
    background: #161b22 !important;
    border: 1px solid #30363d !important;
    color: #e6edf3 !important;
    border-radius: 8px !important;
}
[data-testid="stChatInput"]:focus-within textarea {
    border-color: #58a6ff !important;
    box-shadow: 0 0 0 3px rgba(88,166,255,0.1) !important;
}

/* Progress bars */
[data-testid="stProgressBar"] {
    background: #21262d !important;
    border-radius: 4px !important;
    height: 6px !important;
    margin: 2px 0 8px 0 !important;
}
[data-testid="stProgressBar"] > div > div {
    background: linear-gradient(90deg, #58a6ff, #388bfd) !important;
    border-radius: 4px !important;
}

/* File uploader */
[data-testid="stFileUploadDropzone"] {
    background: #0d1117 !important;
    border: 1px dashed #30363d !important;
    border-radius: 6px !important;
}
[data-testid="stFileUploadDropzone"]:hover {
    border-color: #58a6ff !important;
}

/* Divider */
hr { border-color: #21262d !important; margin: 8px 0 !important; }

/* Captions */
.stCaption p { color: #484f58 !important; font-size: 0.7rem !important; }

/* Alert/info boxes */
[data-testid="stAlert"] {
    background: #161b22 !important;
    border: 1px solid #21262d !important;
    border-radius: 8px !important;
}
[data-testid="stAlert"] p { color: #8b949e !important; }
</style>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════
# FUNÇÕES AUXILIARES
# ════════════════════════════════════════════════════════════════════

def listar_pdfs():
    """Retorna lista ordenada dos PDFs em data/raw/."""
    pasta = "data/raw"
    if not os.path.exists(pasta):
        return []
    return sorted([f for f in os.listdir(pasta) if f.endswith(".pdf")])


def deletar_pdf(nome):
    """Apaga o PDF do disco e remove seu hash do controle de ingestão."""
    caminho = os.path.join("data", "raw", nome)
    if os.path.exists(caminho):
        os.remove(caminho)              # Remove arquivo físico
    controle = carregar_controle()      # Carrega hashes salvos
    if nome in controle:
        del controle[nome]              # Remove a entrada do dicionário
        salvar_controle(controle)       # Persiste no disco


def contar_chunks():
    """Conta chunks em data/processed/chunks.json."""
    path = os.path.join("data", "processed", "chunks.json")
    if not os.path.exists(path):
        return 0
    with open(path, "r", encoding="utf-8") as f:
        return len(json.load(f))


def carregar_relatorio():
    """Carrega relatorio_ragas.json. Retorna None se não existir."""
    path = os.path.join("data", "processed", "relatorio_ragas.json")
    if not os.path.exists(path):
        return None
    with open(path, "r") as f:
        return json.load(f)


def processar_uploads(uploads):
    """
    Salva PDFs em data/raw/ e indexa apenas novos/alterados (hash MD5).
    Retorna (quantidade_indexada, mensagem).
    """
    # Salva cada arquivo enviado
    for arq in uploads:
        destino = os.path.join("data", "raw", arq.name)
        with open(destino, "wb") as f:
            f.write(arq.getbuffer())       # Binário do arquivo

    controle     = carregar_controle()     # Hashes anteriores
    indice       = conectar_pinecone()     # Conexão Pinecone
    novos_chunks = []
    pdfs_novos   = []

    for pdf in listar_pdfs():
        caminho    = os.path.join("data", "raw", pdf)
        hash_atual = calcular_hash_arquivo(caminho)   # MD5 atual

        # Processa só se for novo ou alterado
        if pdf not in controle or controle[pdf] != hash_atual:
            paginas = extrair_texto_pdf(caminho)       # Extrai texto
            chunks  = criar_chunks(paginas)             # Divide em chunks

            for chunk in chunks:
                emb = gerar_embedding(chunk["texto"])  # Vetoriza via OpenAI
                novos_chunks.append({
                    "id":     chunk["metadata"]["chunk_id"],
                    "values": emb,
                    "metadata": {
                        "texto":   chunk["texto"],
                        "arquivo": chunk["metadata"]["arquivo"],
                        "pagina":  chunk["metadata"]["pagina"]
                    }
                })
            controle[pdf] = hash_atual    # Atualiza hash
            pdfs_novos.append(pdf)

    if novos_chunks:
        inserir_chunks(indice, novos_chunks)   # Envia ao Pinecone
        salvar_controle(controle)               # Persiste hashes
        return len(pdfs_novos), f"✅ {len(pdfs_novos)} PDF(s) indexado(s)!"
    else:
        return 0, "⏭️ Nenhum arquivo novo ou alterado."


# ════════════════════════════════════════════════════════════════════
# ESTADO DA SESSÃO
# ════════════════════════════════════════════════════════════════════
if "mensagens" not in st.session_state:
    st.session_state.mensagens = []   # Histórico do chat


# ════════════════════════════════════════════════════════════════════
# SIDEBAR — expanders nativos, sempre funcionam
# ════════════════════════════════════════════════════════════════════
with st.sidebar:

    # Logo
    st.markdown("""
    <div style="padding: 0 0 10px 0;">
      <span style="font-family:'Rajdhani',sans-serif; font-size:1.2rem;
                   font-weight:700; color:#58a6ff; letter-spacing:0.08em;">
        🧠 INTELLIDOC RAG
      </span>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    # ── SEÇÃO 1: Upload ─────────────────────────────────────────
    # expanded=True → começa aberta, usuário vê o upload imediatamente
    with st.expander("📤 ENVIAR DOCUMENTOS", expanded=True):

        uploads = st.file_uploader(
            "PDFs",                       # Label interno (não exibido)
            type=["pdf"],
            accept_multiple_files=True,   # Múltiplos arquivos de uma vez
            label_visibility="collapsed", # Esconde o label padrão
            key="uploader"
        )

        if uploads:
            st.caption(f"{len(uploads)} arquivo(s) pronto(s)")
            if st.button("⚡ INDEXAR AGORA", key="btn_idx"):
                with st.spinner("Indexando..."):
                    qtd, msg = processar_uploads(uploads)
                if qtd > 0:
                    st.success(msg)
                else:
                    st.info(msg)
                st.rerun()

    # ── SEÇÃO 2: Documentos carregados ──────────────────────────
    # expanded=True → lista sempre visível, sem precisar clicar
    with st.expander("📚 DOCUMENTOS CARREGADOS", expanded=True):

        pdfs = listar_pdfs()

        if not pdfs:
            st.caption("Nenhum documento ainda.")
            st.caption("Use o upload acima ↑")
        else:
            st.caption(f"{len(pdfs)} documento(s) indexado(s)")
            st.divider()

            for pdf in pdfs:
                # Linha por arquivo: nome (truncado) + botão deletar
                col_n, col_d = st.columns([5, 1])

                with col_n:
                    # Trunca nomes longos — max 18 caracteres visíveis
                    nome_curto = pdf[:16] + "…" if len(pdf) > 18 else pdf
                    # st.text usa fonte monoespaçada — limpo, consistente
                    st.text(f"📄 {nome_curto}")

                with col_d:
                    # Key única por arquivo para o Streamlit não confundir os botões
                    if st.button("✕", key=f"d_{pdf}", help=f"Deletar: {pdf}"):
                        deletar_pdf(pdf)        # Apaga arquivo + remove hash
                        st.toast(f"🗑️ Deletado!")
                        st.rerun()              # Atualiza a lista

    # ── SEÇÃO 3: Sistema e RAGAS ─────────────────────────────────
    # expanded=False → começa fechada para não poluir visualmente
    with st.expander("⚙️ SISTEMA & AVALIAÇÃO RAGAS", expanded=False):

        # Métricas gerais do sistema
        col1, col2 = st.columns(2)
        with col1:
            st.metric("PDFs",   len(listar_pdfs()))   # Qtd de PDFs em data/raw/
        with col2:
            st.metric("Chunks", contar_chunks())       # Total de chunks no JSON

        st.divider()
        st.caption("AVALIAÇÃO DE QUALIDADE RAGAS")

        rel = carregar_relatorio()   # Tenta carregar o JSON do relatório

        if rel is None:
            # Instrução quando relatório não existe
            st.caption("Relatório não gerado ainda.")
            st.caption("Execute: `python src/evaluation.py`")
        else:
            # As 4 métricas com seus thresholds mínimos aceitáveis
            metricas = [
                ("Faithfulness",      "Fidelidade",     0.80),
                ("Answer Relevancy",  "Relevância",     0.75),
                ("Context Precision", "Precisão Ctx",   0.70),
                ("Context Recall",    "Recall Ctx",     0.70),
            ]

            for chave, label, threshold in metricas:
                score = float(rel.get(chave, 0))

                # Emoji muda conforme o resultado vs threshold
                emoji = "🟢" if score >= threshold else (
                        "🟡" if score >= threshold - 0.10 else "🔴")

                # Nome à esquerda, score à direita na mesma linha
                c1, c2 = st.columns([3, 1])
                with c1:
                    st.caption(f"{emoji} {label}")
                with c2:
                    st.caption(f"**{score:.2f}**")

                # Barra de progresso proporcional ao score (0.0 a 1.0)
                st.progress(min(score, 1.0))

            st.divider()

            # Score médio geral com indicador delta
            media = float(rel.get("media_geral", 0))
            delta = "✅ Aprovado" if media >= 0.75 else "⚠️ Abaixo do mínimo"
            st.metric("Score Médio Geral", f"{media:.2f}", delta=delta)


# ════════════════════════════════════════════════════════════════════
# ÁREA PRINCIPAL — CABEÇALHO
# ════════════════════════════════════════════════════════════════════
col_h, col_b = st.columns([6, 1])

with col_h:
    st.markdown("""
    <div style="padding: 6px 0 2px 0;">
      <span style="font-family:'Rajdhani',sans-serif; font-size:1.9rem;
                   font-weight:700; color:#e6edf3; letter-spacing:0.02em;">
        🧠 IntelliDoc RAG
      </span><br>
      <span style="font-size:0.72rem; color:#484f58;">
        Converse com seus documentos técnicos usando IA
      </span>
    </div>
    """, unsafe_allow_html=True)

with col_b:
    st.write("")   # Alinhamento vertical
    # Apaga todo o histórico e mostra a tela de boas-vindas
    if st.button("🗑️ Limpar", key="limpar",
                 help="Apaga o histórico da conversa"):
        st.session_state.mensagens = []
        st.rerun()

st.divider()


# ════════════════════════════════════════════════════════════════════
# HISTÓRICO DE MENSAGENS — st.chat_message nativo (sempre funciona)
# ════════════════════════════════════════════════════════════════════
if not st.session_state.mensagens:
    # Tela de boas-vindas centralizada usando colunas nativas
    _, col_c, _ = st.columns([1, 2, 1])
    with col_c:
        st.info(
            "**👋 Bem-vindo ao IntelliDoc!**\n\n"
            "Envie PDFs na sidebar e faça perguntas sobre o conteúdo deles.\n\n"
            "**Exemplos:**\n"
            "- O que é RAG e como funciona?\n"
            "- Boas práticas de segurança em APIs REST?\n"
            "- Como o Git ajuda no desenvolvimento?\n"
            "- O que são embeddings?\n"
            "- Quais são as métricas do RAGAS?"
        )
else:
    # Renderiza cada mensagem com o componente nativo de chat
    for msg in st.session_state.mensagens:
        with st.chat_message(msg["role"]):
            # st.markdown suporta formatação dentro de chat_message
            st.markdown(msg["content"])

            # Fontes consultadas — só para respostas do assistente
            if msg["role"] == "assistant" and msg.get("fontes"):
                fontes = "  ·  ".join([f"📄 `{f}`" for f in msg["fontes"]])
                st.caption(f"🔍 Fontes: {fontes}")


# ════════════════════════════════════════════════════════════════════
# INPUT DO CHAT — fixo no rodapé
# ════════════════════════════════════════════════════════════════════
pergunta = st.chat_input("💬  Pergunte algo sobre seus documentos...")

if pergunta:
    # 1. Registra pergunta no histórico
    st.session_state.mensagens.append({"role": "user", "content": pergunta})

    # 2. Gera resposta via pipeline RAG (Pinecone + GPT-4o-mini)
    with st.spinner("🔍 Buscando e gerando resposta..."):
        resultado = rag_query(pergunta)

    # 3. Registra resposta + fontes no histórico
    st.session_state.mensagens.append({
        "role":    "assistant",
        "content": resultado["resposta"],
        "fontes":  resultado["fontes"]
    })

    # 4. Recarrega para exibir as novas mensagens
    st.rerun()