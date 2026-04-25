<div align="center">

# 🧠 IntelliDoc RAG Multimodal

**Sistema de Perguntas & Respostas sobre Documentos com IA**

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![LangChain](https://img.shields.io/badge/LangChain-0.1+-1C3C3C?style=for-the-badge&logo=chainlink&logoColor=white)](https://langchain.com)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-412991?style=for-the-badge&logo=openai&logoColor=white)](https://openai.com)
[![Pinecone](https://img.shields.io/badge/Pinecone-Vector_DB-00BFA5?style=for-the-badge)](https://pinecone.io)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.55+-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Tesseract](https://img.shields.io/badge/Tesseract-5.5-blue?style=for-the-badge)](https://github.com/tesseract-ocr/tesseract)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Status](https://img.shields.io/badge/Status-v1.3_Estavel-brightgreen?style=for-the-badge)]()

<br/>

> Ingere PDFs técnicos e imagens, transforma em embeddings semânticos, armazena em banco vetorial  
> e responde perguntas com GPT-4o-mini — com avaliação automática de fidelidade para evitar alucinações.

<br/>

![Interface IntelliDoc](docs/demo_interface.png)

</div>

---

## 🌐 Demo ao vivo

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://intellidoc-rag.streamlit.app)
[![React App](https://img.shields.io/badge/React-Vercel-black?style=for-the-badge&logo=vercel)](https://intelli-doc-rag-multimodal.vercel.app)
[![FastAPI](https://img.shields.io/badge/FastAPI-Render-00979D?style=for-the-badge)](https://intellidoc-rag-multimodal.onrender.com)

> Acesse, faça upload de um PDF e converse com ele — sem instalar nada.

---

## 📌 O que é este projeto?

O **IntelliDoc RAG Multimodal** é um sistema completo de *Retrieval-Augmented Generation* (RAG) que permite fazer perguntas em linguagem natural sobre documentos técnicos — PDFs ou imagens com texto — e receber respostas precisas, fundamentadas e com citação da fonte.

O diferencial está no **pipeline de avaliação automática**: cada resposta é pontuada em métricas de *fidelidade*, *relevância* e *precisão de contexto* usando a biblioteca RAGAS, tornando o sistema auditável e confiável.

> 📖 **Projeto de portfólio em construção** — desenvolvido do zero, passo a passo, com documentação de cada decisão técnica. Acompanhe a evolução pelos [commits](../../commits) e [issues](../../issues).

---

## ✨ Status das Funcionalidades

| Funcionalidade | Descrição | Versão |
|---|---|---|
| 📄 **Ingestão de PDFs** | Extração de texto com metadados via PyMuPDF | ✅ v1.0 |
| 🔪 **Chunking Inteligente** | Divisão com overlap via LangChain TextSplitter | ✅ v1.0 |
| 🔢 **Embeddings Semânticos** | Vetorização com `text-embedding-3-small` | ✅ v1.0 |
| ⚡ **Ingestão Incremental** | Hash MD5 — processa apenas arquivos novos/alterados | ✅ v1.0 |
| 🗄️ **Banco Vetorial** | 65+ vetores no Pinecone, busca semântica | ✅ v1.0 |
| 🔗 **Pipeline RAG** | Busca semântica + GPT-4o-mini integrados | ✅ v1.0 |
| 🛡️ **Respostas Honestas** | Diz quando não encontra a informação | ✅ v1.0 |
| 📊 **Avaliação RAGAS** | 4 métricas automáticas de qualidade | ✅ v1.0 |
| 🌐 **Interface Streamlit** | Upload, chat, gestão de docs e scores RAGAS | ✅ v1.0 |
| 🖼️ **OCR de Imagens** | Extração de texto de imagens via Tesseract 5.5 | ✅ v1.1 |
| 🔗 **OCR no Pipeline** | Imagens indexadas junto com PDFs automaticamente | ✅ v1.1 |
| 🖼️ **Upload de Imagens** | Interface aceita PNG, JPG, JPEG, BMP, TIFF, WEBP | ✅ v1.1 |
| 🚀 **Deploy em Nuvem** | Streamlit Cloud — intellidoc-rag.streamlit.app | ✅ v1.2 |
| ⚡ **Backend FastAPI** | 6 endpoints REST conectando React ao pipeline RAG | ✅ v1.2 |
| 🎨 **Interface React** | Frontend React + Vite + Tailwind com tema dark tech | ✅ v1.2 |
| 📤 **Upload via React** | Drag-and-drop com feedback: enviando/indexando/erro | ✅ v1.2 |
| 🗑️ **Deleção via React** | Remove documento do Pinecone + controle + disco | ✅ v1.2 |
| 🔒 **Sanitização de Upload** | Validação de filename, null bytes, tamanho máximo 50MB | ✅ v1.2 |
| 🛡️ **Tratamento de Erros** | try/except em todos os endpoints e funções críticas | ✅ v1.2 |
| 💬 **Memória Persistente** | Histórico entre sessões via SQLite | ✅ v1.2 |
| 🌐 **Deploy FastAPI** | Backend FastAPI live no Render (free tier) | ✅ v1.3 |
| 🌐 **Deploy React** | Frontend React live no Vercel (free tier) | ✅ v1.3 |

---

## 🏗️ Arquitetura do Sistema

```
┌──────────────────────────────────────────────────────────────────┐
│                     IntelliDoc RAG Multimodal                     │
└──────────────────────────────────────────────────────────────────┘

  🎨 FRONTEND                🔌 BACKEND               🗄️ STORAGE
  ┌──────────────────┐      ┌──────────────┐          ┌──────────────┐
  │  React (Lovable) │─HTTP▶│   FastAPI    │          │              │
  │  localhost:8080  │      │ localhost:   │─Embed───▶│   Pinecone   │
  └──────────────────┘      │    8000      │  (novos) │  65+ vetores │
                            └──────┬───────┘          └──────┬───────┘
                                   │                         │
  📂 INPUT               🔄 PROCESSING             🔍 RETRIEVAL ✅
  ┌──────────┐          ┌──────────────┐          ┌──────────────┐
  │   PDF    │─PyMuPDF─▶│  Hash MD5    │          │    Busca     │
  └──────────┘          │  Chunking    │          │  Semântica   │
  ┌──────────┐          │  +Metadata   │          └──────────────┘
  │  Imagem  │─Tesseract▶  OCR ✅     │
  └──────────┘          └──────────────┘

  💬 QUERY ✅            🤖 GENERATION ✅          📊 EVALUATION ✅
  ┌──────────┐          ┌──────────────┐          ┌──────────────┐
  │ Pergunta │─Embed───▶│ GPT-4o-mini  │◀─Top-K───│    RAGAS     │
  └──────────┘          │ + Contexto   │          │  Score 0.81  │
                        └──────┬───────┘          └──────────────┘
                               │
                        📤 OUTPUT ✅
                        ┌──────────────┐
                        │   Resposta   │
                        │  + Fontes    │
                        └──────────────┘

  Frontend React (localhost:8080)
          ↓ HTTP
  Backend FastAPI (localhost:8000)
          ↓
  Módulos Python (rag_pipeline, vector_store, embeddings, ocr, evaluation)
          ↓
  Pinecone + GPT-4o-mini
```

---

## 📊 Resultados da Avaliação RAGAS

| Métrica | Score | Threshold | Status |
|---|---|---|---|
| **Faithfulness** | 0.9333 | ≥ 0.80 | ✅ |
| **Answer Relevancy** | 0.9334 | ≥ 0.75 | ✅ |
| **Context Precision** | 0.8000 | ≥ 0.70 | ✅ |
| **Context Recall** | 0.5857 | ≥ 0.70 | ⚠️ Melhora com mais docs |
| **Score Médio** | **0.8131** | ≥ 0.75 | ✅ |

---

## 🖥️ Interfaces

### Streamlit (deploy em nuvem)

**Sidebar:**
- `📤 ENVIAR DOCUMENTOS` — upload de PDFs e imagens com indexação automática
- `📚 DOCUMENTOS CARREGADOS` — lista com botão ✕ para deletar cada arquivo
- `⚙️ SISTEMA & RAGAS` — estatísticas (PDFs, chunks) e scores de qualidade

**Área principal:**
- Chat interativo com histórico da sessão
- Respostas formatadas com citação das fontes
- Botão para limpar o histórico

**Formatos aceitos no upload:** `.pdf` `.png` `.jpg` `.jpeg` `.bmp` `.tiff` `.webp`

### React + FastAPI (interface local)

**Sidebar conectada à API real:**
- Lista documentos indexados vindos do backend
- Métricas RAGAS com barras de progresso em tempo real
- Upload via drag-and-drop ou botão — feedback visual por estado: enviando / indexando / já indexado / erro
- Deleção real: remove vetores do Pinecone + entrada no controle + arquivo em `data/raw/`

**Endpoints FastAPI (`api.py`):**

| Método | Rota | Descrição |
|---|---|---|
| GET | `/` | Health check |
| POST | `/chat` | `{ "pergunta": "..." }` → `{ "resposta": "...", "fontes": [...] }` |
| GET | `/documentos` | Lista arquivos do `controle_ingestao.json` |
| GET | `/metricas` | Lê scores do `relatorio_ragas.json` |
| POST | `/upload` | Recebe arquivo, salva em `data/raw/`, ingestão em background |
| DELETE | `/documentos/{nome}` | Remove vetores do Pinecone + controle + arquivo físico |

---

## 🖼️ Pipeline OCR de Imagens

```
Imagem original
      ↓
Escala de cinza      → Tesseract funciona melhor sem cores
      ↓
Contraste ×2.0       → Destaca texto do fundo
      ↓
Nitidez ×2.0         → Bordas das letras mais definidas
      ↓
Filtro SHARPEN       → Nitidez adicional
      ↓
Tesseract OCR        → lang="por+eng", psm=3 (automático)
      ↓
Limpeza do texto     → Remove linhas vazias e espaços extras
      ↓
Chunks + Pinecone    → Mesmo pipeline dos PDFs ✅
```

---

## ⚡ Ingestão Incremental

```
1ª execução:                  2ª execução (sem mudanças):
──────────────────────        ────────────────────────────────
🆕 novo  — doc1.pdf           ⏭️  doc1.pdf — sem alterações
🆕 novo  — foto.png           ⏭️  foto.png — sem alterações
→ gera embeddings             → zero chamadas à API OpenAI
→ insere no Pinecone          → Pinecone já está atualizado!
→ salva hashes MD5
```

---

## 🛠️ Stack Tecnológica

| Categoria | Tecnologia | Versão |
|---|---|---|
| Linguagem | Python | 3.11 |
| Interface | Streamlit | 1.55+ |
| Orquestração IA | LangChain | 0.1+ |
| LLM | OpenAI GPT-4o-mini | latest |
| Embeddings | text-embedding-3-small | latest |
| Banco Vetorial | Pinecone (serverless) | 8.1+ |
| Parser PDF | PyMuPDF (fitz) | 1.27+ |
| Chunking | LangChain Text Splitters | 0.1+ |
| Deduplicação | Hash MD5 | built-in |
| OCR Engine | Tesseract | 5.5 ✅ |
| OCR Python | pytesseract + Pillow | 0.3+ ✅ |
| Avaliação | RAGAS | 0.4.3 |
| API Backend | FastAPI + Uvicorn | latest |
| Frontend | React + TypeScript + Vite | latest |
| Estilo | Tailwind CSS + Framer Motion | latest |
| Env vars | python-dotenv | 1.0+ |

---

## 📁 Estrutura do Projeto

```
intellidoc-rag/
│
├── 📄 README.md
├── 📋 requirements.txt
├── 📄 LICENSE
├── 🔒 .env.example
├── 🚫 .gitignore
├── 🔧 fix_ssl.py
├── 📄 api.py              # Backend FastAPI — endpoints HTTP
│
├── 📂 frontend/           # Interface React (Lovable.ai)
│   ├── src/
│   │   ├── components/    # ChatArea, Sidebar, WelcomeScreen
│   │   └── types/         # Tipagens TypeScript
│   └── package.json
│
├── 📂 data/
│   ├── raw/                   # PDFs e imagens originais
│   └── processed/
│       ├── chunks.json
│       ├── controle_ingestao.json
│       └── relatorio_ragas.json
│
├── 📂 docs/
│   └── demo_interface.png
│
└── 📂 src/
    ├── ingest.py          # ✅ Ingestão PDFs + integração OCR
    ├── embeddings.py      # ✅ Embeddings via OpenAI
    ├── vector_store.py    # ✅ Pinecone + ingestão incremental PDFs e imagens
    ├── memory.py          # ✅ Memória persistente — SQLite histórico de conversas
    ├── rag_pipeline.py    # ✅ Pipeline RAG end-to-end
    ├── evaluation.py      # ✅ Avaliação RAGAS
    ├── ocr.py             # ✅ OCR de imagens com Tesseract
    └── app.py             # ✅ Interface Streamlit com upload de imagens
```

---

## 🚀 Como Executar

### Pré-requisitos
- Python 3.11
- Tesseract 5.5 instalado ([download](https://github.com/UB-Mannheim/tesseract/wiki))
- Conta OpenAI com API Key e créditos
- Conta Pinecone com API Key

### 1. Clone o repositório

```bash
git clone https://github.com/JosafaSants/IntelliDoc-RAG-Multimodal.git
cd IntelliDoc-RAG-Multimodal
```

### 2. Ambiente virtual

```bash
py -3.11 -m venv venv
venv\Scripts\Activate.ps1    # Windows
source venv/bin/activate      # Mac/Linux
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente

```bash
copy .env.example .env
# Edite o .env com suas chaves reais
```

### 5. (Redes corporativas) Corrija o SSL

```bash
python fix_ssl.py
```

### 6. Indexe os documentos

```bash
# Coloque PDFs e imagens em data/raw/ e execute:
python src/vector_store.py
```

### 7. Inicie a interface Streamlit

```bash
streamlit run src/app.py
```

### Executar com React + FastAPI (novo)

```bash
# Terminal 1 — Backend
uvicorn api:app --reload

# Terminal 2 — Frontend
cd frontend
npm install
npm run dev

# Acesse: http://localhost:8080
```

---

## 🗺️ Roadmap

- [x] **Fase 1** — Ambiente, Git e API OpenAI ✅
- [x] **Fase 2** — Ingestão multi-PDF com chunking ✅
- [x] **Fase 3** — Embeddings e banco vetorial Pinecone ✅
- [x] **Fase 4** — Pipeline RAG end-to-end ✅
- [x] **Fase 5** — Avaliação RAGAS — score médio 0.81 ✅
- [x] **Fase 6** — Interface Streamlit — v1.0 publicada ✅
- [x] **Fase 7** — OCR de imagens integrado ao pipeline ✅
- [x] **Fase 7b** — Upload de imagens na interface Streamlit ✅
- [x] **Fase 7c** — Correções de segurança: path traversal, logging e retorno None ✅
- [x] **Fase 7d** — Segunda rodada de segurança: sanitização de upload, limites, LGPD ✅ v1.2
- [x] **Fase 8** — Deploy Streamlit Cloud ✅
- [x] **Fase 9** — Backend FastAPI + Frontend React ✅ v1.2
- [x] **Fase 10** — Sidebar conectada aos endpoints reais ✅ v1.2
- [x] **Fase 11** — Upload e deleção de documentos via interface React ✅ v1.2
- [x] **Fase 12** — Memória persistente entre sessões (SQLite) ✅
- [x] **Fase 13** — Deploy React + FastAPI na nuvem ✅ v1.3

---

## 📝 Diário de Desenvolvimento

### ✅ Correções de Segurança (code review)
- **Path traversal no DELETE** — o endpoint `DELETE /documentos/{nome}` usava o nome do arquivo diretamente no `os.path.join` sem validação. Um valor como `../../api.py` poderia deletar arquivos fora de `data/raw/`. Corrigido com `os.path.realpath` + `os.path.commonpath`: agora o endpoint verifica que o caminho resolvido está dentro do diretório permitido antes de deletar qualquer coisa.
- **Erros silenciosos no upload em background** — a função `_ingerir_arquivo` rodava sem nenhum `try/except`. Se a API da OpenAI falhasse ou o Pinecone retornasse erro, o problema desaparecia sem deixar rastro e o documento ficava marcado como "indexando" para sempre. Corrigido com bloco `try/except` geral e `logging.exception` para registrar o erro completo com stack trace.
- **Retorno `None` implícito no OCR** — `processar_imagens_pasta` em `ocr.py` retornava `None` quando não havia imagens na pasta, em vez de retornar `[]`. Qualquer código que tentasse iterar sobre esse resultado travaria com `TypeError`. Corrigido para `return []`, mantendo o contrato de tipo esperado pelos chamadores.
- **Erro do Pinecone expunha detalhes internos** — exceções no `DELETE /documentos/{nome}` propagavam mensagens brutas com nome do índice e região para o cliente. Corrigido com `logger.error` interno e resposta genérica HTTP 500 ao frontend.
- **`deletar_pdf()` não limpava o Pinecone** — ao deletar um documento pela interface Streamlit, o arquivo físico era removido mas os vetores permaneciam no Pinecone e continuavam aparecendo nas respostas. Corrigido com chamada `indice.delete(filter={"arquivo": {"$eq": nome}})`.
- **`listar_pdfs()` ignorava imagens** — a sidebar do Streamlit listava apenas arquivos `.pdf`, deixando imagens indexadas invisíveis na lista. Corrigido com filtro para todas as extensões aceitas (PNG, JPG, JPEG, BMP, TIFF, WEBP).
- **`__main__` de `ingest.py` chamava função inexistente** — o bloco de execução direta chamava `ingerir_todos_pdfs()`, que não existia mais após refatoração. Corrigido para `processar_todos_arquivos()`.
- **Log registrava pergunta completa (LGPD)** — `rag_pipeline.py` imprimia a pergunta inteira no terminal. Em produção, logs com dados do usuário violam a LGPD. Corrigido com truncamento para os primeiros 50 caracteres.

### ✅ Segunda Rodada de Correções (code review)
- **`IndexError` em lista vazia no `embeddings.py`** — ao final da função `gerar_embeddings_chunks`, o código acessava `chunks_com_embeddings[0]` para exibir a dimensão do vetor sem verificar se a lista estava vazia. Se nenhum chunk fosse carregado, a execução terminava com `IndexError`. Corrigido com guard `if chunks_com_embeddings:` antes do acesso.
- **`IndexError` no `__main__` de `ingest.py`** — o exemplo de saída acessava `chunks[5]` diretamente, sem garantir que existiam pelo menos 6 chunks. Corrigido para `chunks[min(5, len(chunks) - 1)]`.
- **`filename` None causava `TypeError` no upload** — se o cliente enviasse um arquivo sem nome, `arquivo.filename` chegava como `None` e o `os.path.splitext(None)` lançava `TypeError` antes mesmo da validação de extensão. Corrigido com validação HTTP 400 explícita antes de qualquer uso do nome.
- **`filename` sem sanitização permitia path traversal no upload** — o nome do arquivo enviado pelo cliente era usado diretamente em `os.path.join("data", "raw", arquivo.filename)`. Um valor como `subdir/evil.pdf` criava subpastas arbitrárias; null bytes (`\x00`) podiam causar comportamento indefinido. Corrigido com `os.path.basename` para descartar componentes de diretório, remoção de null bytes e regex que aceita apenas caracteres alfanuméricos seguros.
- **Sem limite de tamanho no upload** — arquivos de qualquer tamanho eram aceitos e lidos inteiros em memória, possibilitando esgotamento de RAM e disco. Corrigido com `MAX_UPLOAD_BYTES = 50 * 1024 * 1024` (50 MB) e resposta HTTP 413 caso o limite seja excedido.
- **Endpoint `/chat` sem tratamento de erro** — qualquer falha na OpenAI ou no Pinecone propagava um traceback completo como HTTP 500. Corrigido com `try/except` que registra o erro internamente e devolve HTTP 503 com mensagem genérica; pergunta vazia agora retorna HTTP 400.
- **`processar_uploads` no Streamlit sem `try/except`** — erros de OCR, OpenAI ou Pinecone durante o upload pela interface Streamlit exibiam um traceback Python completo para o usuário, expondo caminhos internos e detalhes do ambiente. Corrigido com captura de exceção e exibição de mensagem amigável via `st.error`.
- **Ausência de aviso LGPD na interface** — perguntas digitadas pelo usuário são enviadas para a API da OpenAI (servidores nos EUA) sem nenhuma notificação na tela, o que contraria o art. 33 da LGPD sobre transferência internacional de dados. Adicionado aviso na tela de boas-vindas informando que as perguntas são processadas pela OpenAI e orientando a não incluir dados pessoais sensíveis.

### ✅ Fases 9–11 — Stack React + FastAPI completo
- `api.py` criado na raiz com 6 endpoints: GET /, POST /chat, GET /documentos, GET /metricas, POST /upload, DELETE /documentos/{nome}
- Frontend React + TypeScript + Vite + Tailwind + Framer Motion integrado em `frontend/`
- `ChatArea.tsx` conectado à API real — pipeline completo funcionando
- `Sidebar.tsx` conectada: lista documentos reais, métricas RAGAS ao vivo, upload drag-and-drop, deleção real
- Upload com feedback por estado: enviando / indexando / já indexado / erro
- Deleção remove vetores do Pinecone + entrada no controle + arquivo físico em `data/raw/`
- CORS configurado para localhost:8080
- Pipeline validado: React → FastAPI → Pinecone → GPT-4o-mini → resposta na tela

### ✅ Fase 7b — Upload de imagens na interface
- `app.py` atualizado para aceitar imagens no upload (PNG, JPG, JPEG, BMP, TIFF, WEBP)
- `processar_uploads()` atualizado para detectar tipo do arquivo e aplicar OCR quando necessário
- Sidebar reorganizada sem expanders problemáticos — seções limpas e funcionais
- Scores RAGAS visíveis diretamente na sidebar com barras de progresso

### ✅ Fase 7 — OCR integrado ao pipeline
- Tesseract 5.5 instalado e configurado no Windows
- `src/ocr.py` criado com pré-processamento automático de imagens
- `ingest.py` e `vector_store.py` atualizados para PDFs e imagens juntos
- Ingestão incremental funcionando para imagens

### ✅ Fase 6 — v1.0 publicada
- Interface Streamlit dark mode com sidebar funcional
- Release v1.0.0 publicada no GitHub

### ✅ Fases 1–5 — Pipeline completo
- Ambiente, embeddings, Pinecone, RAG e avaliação RAGAS implementados

### 🔧 Melhorias identificadas pelo desenvolvedor
- **Ingestão incremental v2** — embeddings gerados apenas para chunks alterados

---

## 🧑‍💻 Sobre o Desenvolvimento

Construído do zero como portfólio de aprendizado em **IA aplicada e Engenharia de Software**. O repositório documenta não apenas o produto final, mas a jornada — com decisões técnicas, problemas encontrados e melhorias propostas pelo próprio desenvolvedor.

---

## 📄 Licença

Distribuído sob a licença MIT. Veja [LICENSE](LICENSE).

---

<div align="center">

Feito com 🧠 e muito café

⭐ Se este projeto te ajudou, deixe uma estrela!

</div>
