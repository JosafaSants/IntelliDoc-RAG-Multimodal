import streamlit as st # Biblioteca para criar a interface web do projeto
import sys 
import os
import json
import tempfile # Biblioteca para utilizar arquivos temporários

from dotenv import load_dotenv # Carrega variáveis do arquivo .env (usado localmente)

# Adiciona o diretório src ao path para importar os módulos do projeto
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ingest import extrair_texto_pdf, criar_chunks # Funções de ingestão de PDFs
from vector_store import conectar_pinecone, inserir_chunks, buscar, filtrar_pdfs_alterados, calcular_hash_arquivo, carregar_controle, salvar_controle # Funções do Pinecone
from embeddings import gerar_embedding # Geração de embeddings
from rag_pipeline import rag_query # Pipeline RAG principal

# ════════════════════════════════════════════════════════════════════
# CARREGAMENTO DE SECRETS — funciona local e na nuvem
#
# Estratégia de fallback em duas etapas:
# 1. Tenta carregar do st.secrets (Streamlit Community Cloud)
# 2. Se não encontrar, cai para o .env local via load_dotenv()
#
# Isso permite que o mesmo código rode sem modificação
# tanto na máquina do desenvolvedor quanto na nuvem.
# ════════════════════════════════════════════════════════════════════
load_dotenv() # Carrega o .env local (não faz nada se o arquivo não existir)

try:
    # Tenta ler as chaves do sistema de secrets do Streamlit Cloud
    # st.secrets só existe quando o app roda na nuvem
    os.environ["OPENAI_API_KEY"]   = st.secrets["OPENAI_API_KEY"]
    os.environ["PINECONE_API_KEY"] = st.secrets["PINECONE_API_KEY"]
    os.environ["PINECONE_INDEX_NAME"] = st.secrets["PINECONE_INDEX_NAME"]
    os.environ["PINECONE_ENVIRONMENT"] = st.secrets["PINECONE_ENVIRONMENT"]
except Exception:
    # Se st.secrets não existir (ambiente local), os valores já foram
    # carregados pelo load_dotenv() acima — não faz nada aqui
    pass

# ════════════════════════════════════════════════════════════════════
# CONFIGURAÇÃO DA PÁGINA
# ════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="IntelliDoc RAG",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)
 
# ════════════════════════════════════════════════════════════════════
# CSS — Estilização global via variáveis CSS
#
# REGRA DE OURO: dentro de sidebar/expanders usar APENAS componentes
# nativos do Streamlit (st.metric, st.progress, st.caption, st.text,
# st.columns, st.button, st.divider). HTML customizado via
# st.markdown só na área principal, onde renderiza sem bugs.
# ════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
/* Remove ícones indesejados do Material Icons nos expanders e sidebar */
[data-testid="stSidebar"] span[data-testid="stIconMaterial"],
[data-testid="stExpander"] span[data-testid="stIconMaterial"] {
    display: none !important;
}

/* Remove o keyboard_double do topo da sidebar */
[data-testid="stSidebarCollapseButton"] span {
    display: none !important;
}
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&family=IBM+Plex+Mono:wght@300;400;500&display=swap');
 
:root {
    --bg-deep:       #0a0e14;
    --bg-surface:    #111820;
    --bg-elevated:   #171d27;
    --border-subtle: #1e2733;
    --border-mid:    #2a3545;
    --accent:        #3b82f6;
    --accent-glow:   rgba(59,130,246,0.12);
    --text-primary:  #d4dae3;
    --text-secondary:#5c6a7a;
    --text-muted:    #3a4553;
    --green:         #22c55e;
    --yellow:        #eab308;
    --red:           #ef4444;
    --font-display:  'Rajdhani', sans-serif;
    --font-body:     'IBM Plex Mono', 'JetBrains Mono', monospace;
}
 
* { font-family: var(--font-body) !important; }
#MainMenu, footer, header { visibility: hidden !important; }
.stDeployButton { display: none !important; }
 
/* ── App background ──────────────────────────────────── */
.stApp {
    background: var(--bg-deep) !important;
}
 
/* ── Sidebar ─────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: var(--bg-surface) !important;
    border-right: 1px solid var(--border-subtle) !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding: 1rem 0.9rem !important;
}
[data-testid="stSidebar"][aria-expanded="false"] {
    margin-left: 0 !important;
    transform: none !important;
}
 
/* ── Expanders ───────────────────────────────────────── */
[data-testid="stExpander"] {
    background: var(--bg-deep) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 8px !important;
    margin-bottom: 6px !important;
}
[data-testid="stExpander"] summary {
    font-family: var(--font-display) !important;
    font-weight: 700 !important;
    font-size: 0.74rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.12em !important;
    color: var(--text-secondary) !important;
    padding: 9px 11px !important;
}
[data-testid="stExpander"] summary:hover {
    color: var(--accent) !important;
}
 
/* ── Metrics ─────────────────────────────────────────── */
[data-testid="stMetric"] {
    background: var(--bg-elevated) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 8px !important;
    padding: 10px 12px !important;
}
[data-testid="stMetricValue"] {
    color: var(--accent) !important;
    font-family: var(--font-display) !important;
    font-size: 1.5rem !important;
    font-weight: 700 !important;
}
[data-testid="stMetricLabel"] {
    color: var(--text-muted) !important;
    font-size: 0.6rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
}
[data-testid="stMetricDelta"] {
    font-family: var(--font-display) !important;
    font-weight: 600 !important;
}
 
/* ── Buttons ─────────────────────────────────────────── */
.stButton > button {
    background: var(--bg-elevated) !important;
    color: var(--accent) !important;
    border: 1px solid var(--border-mid) !important;
    border-radius: 6px !important;
    font-family: var(--font-display) !important;
    font-weight: 700 !important;
    font-size: 0.82rem !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    transition: all 0.15s ease !important;
    width: 100% !important;
    padding: 0.4rem 0.8rem !important;
}
.stButton > button:hover {
    background: var(--accent) !important;
    color: #fff !important;
    border-color: var(--accent) !important;
    box-shadow: 0 0 20px var(--accent-glow) !important;
    transform: translateY(-1px) !important;
}
 
/* ── Chat ────────────────────────────────────────────── */
[data-testid="stChatMessage"] {
    background: var(--bg-surface) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 10px !important;
    margin-bottom: 8px !important;
}
[data-testid="stChatMessageContent"] p {
    color: var(--text-primary) !important;
    line-height: 1.7 !important;
    font-size: 0.88rem !important;
}
[data-testid="stChatInput"] textarea {
    background: var(--bg-surface) !important;
    border: 1px solid var(--border-mid) !important;
    color: var(--text-primary) !important;
    border-radius: 10px !important;
    font-size: 0.88rem !important;
}
[data-testid="stChatInput"]:focus-within textarea {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px var(--accent-glow) !important;
}
 
/* ── Progress bars ───────────────────────────────────── */
[data-testid="stProgressBar"] {
    background: var(--bg-elevated) !important;
    border-radius: 4px !important;
    height: 5px !important;
    margin: 2px 0 8px 0 !important;
}
[data-testid="stProgressBar"] > div > div {
    background: linear-gradient(90deg, var(--accent), #60a5fa) !important;
    border-radius: 4px !important;
}
 
/* ── File uploader ───────────────────────────────────── */
[data-testid="stFileUploadDropzone"] {
    background: var(--bg-deep) !important;
    border: 1px dashed var(--border-mid) !important;
    border-radius: 8px !important;
}
[data-testid="stFileUploadDropzone"]:hover {
    border-color: var(--accent) !important;
}
 
/* ── Misc ────────────────────────────────────────────── */
hr { border-color: var(--border-subtle) !important; margin: 8px 0 !important; }
.stCaption p { color: var(--text-secondary) !important; font-size: 0.68rem !important; }
[data-testid="stAlert"] {
    background: var(--bg-surface) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 10px !important;
}
[data-testid="stAlert"] p { color: var(--text-secondary) !important; }
.stSpinner > div { color: var(--accent) !important; }
 
/* ── Scrollbar ───────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg-deep); }
::-webkit-scrollbar-thumb { background: var(--border-mid); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--text-muted); }
 
/* ── Welcome card (área principal, HTML seguro) ──────── */
.welcome-box {
    background: var(--bg-surface);
    border: 1px solid var(--border-subtle);
    border-radius: 12px;
    padding: 2.5rem 2rem;
    text-align: center;
    max-width: 560px;
    margin: 2.5rem auto;
}
.welcome-box h2 {
    font-family: var(--font-display) !important;
    font-size: 1.5rem; font-weight: 700;
    color: var(--text-primary);
    margin: 0 0 0.4rem 0;
}
.welcome-box .sub {
    color: var(--text-secondary);
    font-size: 0.78rem; margin-bottom: 1.3rem; line-height: 1.5;
}
.welcome-box .chip {
    background: var(--bg-deep);
    border: 1px solid var(--border-subtle);
    border-radius: 8px; padding: 9px 14px;
    color: var(--text-secondary); font-size: 0.74rem;
    margin-bottom: 5px; text-align: left;
}
.welcome-box .chip:hover {
    border-color: var(--accent); color: var(--text-primary);
}
 
/* ── Header (área principal) ─────────────────────────── */
.hdr-title {
    font-family: var(--font-display) !important;
    font-size: 1.7rem; font-weight: 700;
    color: var(--text-primary); line-height: 1.1;
}
.hdr-accent { color: var(--accent); }
.hdr-sub {
    font-size: 0.7rem; color: var(--text-muted);
    letter-spacing: 0.04em; margin-top: 2px;
}
</style>
""", unsafe_allow_html=True)
 
 
# ════════════════════════════════════════════════════════════════════
# FUNÇÕES AUXILIARES — lógica preservada do original
# ════════════════════════════════════════════════════════════════════
 
def listar_pdfs():
    """Retorna lista ordenada de todos os documentos em data/raw/ — PDFs e imagens."""
    pasta = "data/raw"
    if not os.path.exists(pasta):
        return []
    extensoes_aceitas = {".pdf", ".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp"}
    # Filtra qualquer arquivo cuja extensão esteja no conjunto aceito
    # Isso garante que imagens indexadas apareçam na sidebar junto com os PDFs
    return sorted([
        f for f in os.listdir(pasta)
        if os.path.splitext(f)[1].lower() in extensoes_aceitas
    ])
 
 
def deletar_pdf(nome):
    """
    Remove o documento completamente:
    1. Apaga o arquivo físico de data/raw/
    2. Remove os vetores do Pinecone (filtro por metadata["arquivo"])
    3. Remove o hash do controle de ingestão

    Sem o passo 2, o conteúdo continuaria sendo retornado nas buscas
    mesmo após o usuário deletar o documento pela interface.
    """
    # ── 1. Remove arquivo físico ────────────────────────────────
    caminho = os.path.join("data", "raw", nome)
    if os.path.exists(caminho):
        os.remove(caminho)

    # ── 2. Remove vetores do Pinecone ───────────────────────────
    # filter={"arquivo": {"$eq": nome}} deleta todos os vetores
    # onde metadata["arquivo"] == nome — mesmo padrão do api.py
    try:
        indice = conectar_pinecone()
        indice.delete(filter={"arquivo": {"$eq": nome}})
    except Exception as e:
        st.warning(f"⚠️ Arquivo removido localmente, mas erro ao limpar Pinecone: {e}")

    # ── 3. Remove do controle de ingestão ───────────────────────
    controle = carregar_controle()
    if nome in controle:
        del controle[nome]
        salvar_controle(controle)
 
 
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
    Salva arquivos em data/raw/ e indexa apenas novos/alterados.
    Agora aceita PDFs e imagens (png, jpg, jpeg, bmp, tiff, webp).
    Retorna (quantidade_indexada, mensagem).
    """
    for arq in uploads:
        destino = os.path.join("data", "raw", arq.name)
        with open(destino, "wb") as f:
            f.write(arq.getbuffer())

    controle          = carregar_controle()
    indice            = conectar_pinecone()
    novos_chunks      = []
    arquivos_novos    = []
    extensoes_img     = {".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp"}

    # Verifica PDFs e imagens juntos
    todos_arquivos = [
        f for f in os.listdir("data/raw")
        if f.endswith(".pdf") or
        os.path.splitext(f)[1].lower() in extensoes_img
    ]

    for arquivo in todos_arquivos:
        caminho    = os.path.join("data", "raw", arquivo)
        hash_atual = calcular_hash_arquivo(caminho)

        if arquivo not in controle or controle[arquivo] != hash_atual:
            ext = os.path.splitext(arquivo)[1].lower()

            if ext == ".pdf":
                # Processa PDF normalmente
                paginas = extrair_texto_pdf(caminho)
            else:
                # Processa imagem via OCR
                from ocr import extrair_texto_imagem
                texto   = extrair_texto_imagem(caminho)
                paginas = [{"texto": texto, "pagina": 1, "arquivo": arquivo}]

            chunks = criar_chunks(paginas)

            for chunk in chunks:
                emb = gerar_embedding(chunk["texto"])
                novos_chunks.append({
                    "id":     chunk["metadata"]["chunk_id"],
                    "values": emb,
                    "metadata": {
                        "texto":   chunk["texto"],
                        "arquivo": chunk["metadata"]["arquivo"],
                        "pagina":  chunk["metadata"]["pagina"]
                    }
                })
            controle[arquivo] = hash_atual
            arquivos_novos.append(arquivo)

    if novos_chunks:
        inserir_chunks(indice, novos_chunks)
        salvar_controle(controle)
        return len(arquivos_novos), f"✅ {len(arquivos_novos)} arquivo(s) indexado(s)!"
    else:
        return 0, "⏭️ Nenhum arquivo novo ou alterado." 
 
# ════════════════════════════════════════════════════════════════════
# ESTADO DA SESSÃO
# ════════════════════════════════════════════════════════════════════
if "mensagens" not in st.session_state:
    st.session_state.mensagens = []
 
 
# ════════════════════════════════════════════════════════════════════
# SIDEBAR — 100% componentes nativos dentro de expanders
# ════════════════════════════════════════════════════════════════════
with st.sidebar:
 
    # ── Logo ─────────────────────────────────────────────────────
    st.markdown(
        '<span style="font-family:Rajdhani,sans-serif;font-size:1.15rem;'
        'font-weight:700;color:#d4dae3;letter-spacing:0.06em;">'
        '🧠 INTELLIDOC </span>'
        '<span style="font-family:Rajdhani,sans-serif;font-size:1.15rem;'
        'font-weight:400;color:#3b82f6;">RAG</span>',
        unsafe_allow_html=True
    )
    st.divider()
 
    # ── SEÇÃO 1: Upload ─────────────────────────────────────────
    st.markdown("**📤 ENVIAR DOCUMENTOS**")
    st.divider()

    uploads = st.file_uploader(
        "PDFs e Imagens",
        type=["pdf", "png", "jpg", "jpeg", "bmp", "tiff", "webp"],
        accept_multiple_files=True,
        label_visibility="collapsed",
        key="uploader"
    )

    if uploads:
        st.caption(f"{len(uploads)} arquivo(s) pronto(s)")
        if st.button("⚡ INDEXAR AGORA", key="btn_idx"):
            with st.spinner("Indexando..."):
                try:
                    qtd, msg = processar_uploads(uploads)
                    if qtd > 0:
                        st.success(msg)
                    else:
                        st.info(msg)
                except Exception as e:
                    # Captura erros de OCR, OpenAI ou Pinecone
                    # sem expor traceback completo ao usuário
                    st.error("Erro ao processar arquivos. Tente novamente.")
                    # Importa logging aqui para registrar o erro internamente
                    import logging
                    logging.exception("Falha em processar_uploads: %s", str(e))
            st.rerun()

    st.divider()

    # ── SEÇÃO 2: Documentos carregados ──────────────────────────
    st.markdown("**📚 DOCUMENTOS CARREGADOS**")

    pdfs = listar_pdfs()

    if not pdfs:
        st.caption("Nenhum documento ainda.")
        st.caption("Use o upload acima ↑")
    else:
        st.caption(f"{len(pdfs)} documento(s) indexado(s)")
        st.divider()
        for pdf in pdfs:
            col_n, col_d = st.columns([5, 1])
            with col_n:
                nome_curto = pdf[:16] + "…" if len(pdf) > 18 else pdf
                st.text(f"📄 {nome_curto}")
            with col_d:
                if st.button("✕", key=f"d_{pdf}", help=f"Deletar: {pdf}"):
                    deletar_pdf(pdf)
                    st.toast(f"🗑️ Deletado!")
                    st.rerun()

    st.divider()

    # ── SEÇÃO 3: Sistema e RAGAS ─────────────────────────────────
    with st.expander("⚙️ SISTEMA & RAGAS", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.metric("PDFs", len(listar_pdfs()))
        with col2:
            st.metric("Chunks", contar_chunks())

        st.divider()
        rel = carregar_relatorio()

        if rel is None:
            st.caption("Execute: `python src/evaluation.py`")
        else:
            metricas = [
                ("Faithfulness",      "Fidelidade",    0.80),
                ("Answer Relevancy",  "Relevância",    0.75),
                ("Context Precision", "Precisão Ctx",  0.70),
                ("Context Recall",    "Recall Ctx",    0.70),
            ]
            for chave, label, threshold in metricas:
                score = float(rel.get(chave, 0))
                emoji = "🟢" if score >= threshold else "🟡" if score >= threshold - 0.10 else "🔴"
                c1, c2 = st.columns([3, 1])
                with c1:
                    st.caption(f"{emoji} {label}")
                with c2:
                    st.caption(f"**{score:.2f}**")
                st.progress(min(score, 1.0))
            st.divider()
            media = float(rel.get("media_geral", 0))
            delta = "✅ Aprovado" if media >= 0.75 else "⚠️ Abaixo do mínimo"
            st.metric("Score Médio", f"{media:.2f}", delta=delta)
 
 
# ════════════════════════════════════════════════════════════════════
# ÁREA PRINCIPAL — CABEÇALHO
# ════════════════════════════════════════════════════════════════════
col_h, col_b = st.columns([6, 1])
 
with col_h:
    st.markdown(
        '<div style="padding:4px 0 0 0;">'
        '<span class="hdr-title">🧠 Intelli<span class="hdr-accent">Doc</span></span>'
        '<div class="hdr-sub">Sistema RAG Multimodal · Converse com seus documentos técnicos</div>'
        '</div>',
        unsafe_allow_html=True
    )
 
with col_b:
    st.write("")
    if st.button("🗑️ Limpar", key="limpar", help="Apaga o histórico da conversa"):
        st.session_state.mensagens = []
        st.rerun()
 
st.divider()
 
 
# ════════════════════════════════════════════════════════════════════
# HISTÓRICO DE MENSAGENS
# ════════════════════════════════════════════════════════════════════
if not st.session_state.mensagens:
    # Tela de boas-vindas — HTML na área principal (renderiza sem bugs)
    st.markdown("""
    <div class="welcome-box">
      <h2>👋 Bem-vindo ao IntelliDoc</h2>
      <div class="sub">
        Envie seus PDFs técnicos na sidebar e faça perguntas
        sobre o conteúdo deles usando linguagem natural.
      </div>
      <div class="chip">💡 O que é RAG e como funciona?</div>
      <div class="chip">🔒 Boas práticas de segurança em APIs REST?</div>
      <div class="chip">🔀 Como o Git ajuda no desenvolvimento?</div>
      <div class="chip">🧮 O que são embeddings e para que servem?</div>
      <div class="chip">📊 Quais métricas o RAGAS utiliza?</div>
      <div style="margin-top:1rem;padding:8px 12px;background:var(--bg-deep);
        border:1px solid var(--border-subtle);border-radius:6px;
        color:var(--text-muted);font-size:0.65rem;line-height:1.4;">
        ⚠️ Suas perguntas são processadas pela API da OpenAI (EUA).<br>
        Não inclua dados pessoais sensíveis nos documentos ou perguntas.
      </div>
    </div>
    """, unsafe_allow_html=True)
else:
    for msg in st.session_state.mensagens:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
 
            # Fontes consultadas — apenas para respostas do assistente
            if msg["role"] == "assistant" and msg.get("fontes"):
                fontes = "  ·  ".join([f"📄 `{f}`" for f in msg["fontes"]])
                st.caption(f"🔍 Fontes: {fontes}")
 
 
# ════════════════════════════════════════════════════════════════════
# INPUT DO CHAT
# ════════════════════════════════════════════════════════════════════
pergunta = st.chat_input("💬  Pergunte algo sobre seus documentos...")
 
if pergunta:
    # 1. Registra pergunta no histórico
    st.session_state.mensagens.append({"role": "user", "content": pergunta})
 
    # 2. Gera resposta via pipeline RAG (Pinecone + GPT-4o-mini)
    with st.spinner("🔍 Buscando contexto e gerando resposta…"):
        resultado = rag_query(pergunta)
 
    # 3. Registra resposta + fontes no histórico
    st.session_state.mensagens.append({
        "role":    "assistant",
        "content": resultado["resposta"],
        "fontes":  resultado["fontes"]
    })
 
    # 4. Recarrega para exibir novas mensagens
    st.rerun()