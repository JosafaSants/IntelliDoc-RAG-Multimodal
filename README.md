<div align="center">

# 🧠 IntelliDoc RAG Multimodal

**Sistema de Perguntas & Respostas sobre Documentos com IA**

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![LangChain](https://img.shields.io/badge/LangChain-0.1+-1C3C3C?style=for-the-badge&logo=chainlink&logoColor=white)](https://langchain.com)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-412991?style=for-the-badge&logo=openai&logoColor=white)](https://openai.com)
[![Pinecone](https://img.shields.io/badge/Pinecone-Vector_DB-00BFA5?style=for-the-badge)](https://pinecone.io)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.55+-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Status](https://img.shields.io/badge/Status-v1.0_Publicado-brightgreen?style=for-the-badge)]()

<br/>

> Ingere PDFs técnicos, transforma em embeddings semânticos, armazena em banco vetorial  
> e responde perguntas com GPT-4o-mini — com avaliação automática de fidelidade para evitar alucinações.

<br/>

![Interface IntelliDoc](docs/demo_interface.png)


</div>

---

## 📌 O que é este projeto?

O **IntelliDoc RAG Multimodal** é um sistema completo de *Retrieval-Augmented Generation* (RAG) que permite fazer perguntas em linguagem natural sobre documentos técnicos e receber respostas precisas, fundamentadas e com citação da fonte.

O sistema avalia automaticamente cada resposta com métricas de *fidelidade*, *relevância* e *precisão de contexto* usando a biblioteca RAGAS, tornando as respostas auditáveis e confiáveis.

> 📖 **Projeto de portfólio** — construído do zero, passo a passo, com documentação de cada decisão técnica. Acompanhe a evolução pelos [commits](../../commits) e [issues](../../issues).

---

## ⚠️ Status das Funcionalidades

> **Este projeto está em evolução contínua.**
> A **v1.0** cobre o pipeline completo com PDFs via interface web.
> O suporte a **imagens com OCR** está planejado para a **v1.1** e será implementado em breve.

| Funcionalidade | Descrição | Versão |
|---|---|---|
| 📄 **Ingestão de PDFs** | Extração de texto com metadados via PyMuPDF | ✅ v1.0 |
| 🔪 **Chunking Inteligente** | Divisão com overlap via LangChain TextSplitter | ✅ v1.0 |
| 🔢 **Embeddings Semânticos** | Vetorização com `text-embedding-3-small` | ✅ v1.0 |
| ⚡ **Ingestão Incremental** | Hash MD5 — processa apenas arquivos novos/alterados | ✅ v1.0 |
| 🗄️ **Banco Vetorial** | 63+ vetores no Pinecone, busca semântica | ✅ v1.0 |
| 🔗 **Pipeline RAG** | Busca semântica + GPT-4o-mini integrados | ✅ v1.0 |
| 🛡️ **Respostas Honestas** | Diz quando não encontra a informação | ✅ v1.0 |
| 📊 **Avaliação RAGAS** | 4 métricas automáticas de qualidade | ✅ v1.0 |
| 🌐 **Interface Streamlit** | Upload, chat, gestão de docs e scores RAGAS | ✅ v1.0 |
| 🖼️ **OCR de Imagens** | Extração de texto de imagens via Tesseract | 🔜 **v1.1** |
| 💬 **Memória Persistente** | Histórico entre sessões | 🔜 **v1.1** |
| 🚀 **Deploy em Nuvem** | Streamlit Cloud ou Hugging Face Spaces | 🔜 **v1.1** |

---

## 🏗️ Arquitetura do Sistema

```
┌──────────────────────────────────────────────────────────────────┐
│                     IntelliDoc RAG Multimodal                     │
└──────────────────────────────────────────────────────────────────┘

  📂 INPUT               🔄 PROCESSING             🗄️ STORAGE
  ┌──────────┐          ┌──────────────┐          ┌──────────────┐
  │   PDF    │─PyMuPDF─▶│  Hash MD5    │          │              │
  └──────────┘          │  Chunking    │─Embed───▶│   Pinecone   │
  ┌──────────┐          │  +Metadata   │  (novos) │  Vector DB   │
  │  Imagem  │─[v1.1]──▶│  OCR [v1.1] │          │              │
  └──────────┘          └──────────────┘          └──────┬───────┘
                                                         │
  💬 QUERY ✅            🤖 GENERATION ✅          🔍 RETRIEVAL ✅
  ┌──────────┐          ┌──────────────┐          ┌──────────────┐
  │ Pergunta │─Embed───▶│ GPT-4o-mini  │◀─Top-K───│    Busca     │
  └──────────┘          │ + Contexto   │          │  Semântica   │
                        └──────┬───────┘          └──────────────┘
                               │
  📊 EVALUATION ✅       📤 OUTPUT ✅
  ┌──────────────┐      ┌──────────────┐
  │    RAGAS     │◀─────│   Resposta   │
  │  Score 0.81  │      │  + Fontes    │
  └──────────────┘      └──────────────┘
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

> O Context Recall abaixo do threshold é esperado com corpus pequeno (4 documentos). Adicionar mais PDFs ao sistema aumenta diretamente esse score.

---

## 🖥️ Interface Streamlit

A interface web permite usar o sistema completo sem linha de comando:

**Sidebar:**
- `📤 Enviar Documentos` — upload de PDFs com indexação automática
- `📚 Documentos Carregados` — lista com opção de deletar cada arquivo
- `⚙️ Sistema & Avaliação RAGAS` — estatísticas e scores de qualidade

**Área principal:**
- Chat interativo com histórico da sessão
- Respostas formatadas com citação das fontes
- Botão para limpar o histórico

---

## ⚡ Ingestão Incremental

O sistema usa **hash MD5** para detectar mudanças e gera embeddings **apenas para chunks novos ou alterados**:

```
1ª execução:                  2ª execução (sem mudanças):
──────────────────────        ────────────────────────────────
🆕 novo  — doc1.pdf           ⏭️  doc1.pdf — sem alterações
🆕 novo  — doc2.pdf           ⏭️  doc2.pdf — sem alterações
→ gera embeddings             → zero chamadas à API OpenAI
→ insere no Pinecone          → Pinecone já está atualizado!
→ salva hashes MD5

3ª execução (doc1 alterado):
─────────────────────────────
⏭️  doc2.pdf — sem alterações
♻️  doc1.pdf — alterado
→ embeddings APENAS do doc1
→ atualiza só os vetores do doc1
```

> **Detalhe técnico:** a otimização opera no nível do chunk — `gerar_embedding()` é chamada diretamente sobre os chunks dos arquivos alterados, evitando reprocessar o corpus inteiro. Identificado e implementado durante revisão de código.

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
| OCR | Tesseract + pytesseract | 🔜 v1.1 |
| Avaliação | RAGAS | 0.4+ |
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
├── 🔧 fix_ssl.py              # Correção de SSL corporativo Windows
│
├── 📂 data/
│   ├── raw/                   # PDFs e imagens originais
│   └── processed/
│       ├── chunks.json            # Chunks extraídos com metadados
│       ├── controle_ingestao.json # Hashes MD5 — ingestão incremental
│       └── relatorio_ragas.json   # Scores da avaliação RAGAS
│
└── 📂 src/
    ├── ingest.py          # ✅ Ingestão multi-PDF com chunking
    ├── embeddings.py      # ✅ Embeddings via OpenAI
    ├── vector_store.py    # ✅ Pinecone + ingestão incremental
    ├── rag_pipeline.py    # ✅ Pipeline RAG end-to-end
    ├── evaluation.py      # ✅ Avaliação RAGAS
    └── app.py             # ✅ Interface Streamlit
```

---

## 🚀 Como Executar

### Pré-requisitos
- Python 3.11
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
# Coloque PDFs em data/raw/ e execute:
python src/vector_store.py
```

### 7. Inicie a interface

```bash
streamlit run src/app.py
# Acesse http://localhost:8501
```

---

## 🗺️ Roadmap

- [x] **Fase 1** — Ambiente, Git e API OpenAI ✅
- [x] **Fase 2** — Ingestão multi-PDF com chunking ✅
- [x] **Fase 3** — Embeddings e banco vetorial Pinecone ✅
- [x] **Fase 4** — Pipeline RAG end-to-end ✅
- [x] **Fase 5** — Avaliação RAGAS — score médio 0.81 ✅
- [x] **Fase 6** — Interface Streamlit completa ✅ — **v1.0 publicada!**
- [ ] **Fase 7** — OCR de imagens com Tesseract 🔜 v1.1
- [ ] **Fase 8** — Deploy em nuvem 🔜 v1.1

---

## 📝 Diário de Desenvolvimento

### ✅ Fase 6 — v1.0 publicada
- Interface Streamlit dark mode com sidebar funcional
- Gestão completa de documentos: upload, listagem e deleção
- Chat interativo com histórico e citação de fontes
- Painel de scores RAGAS visível na interface
- Botão de limpar histórico do chat

### ✅ Fase 5 — Avaliação RAGAS
- Faithfulness: **0.93** · Answer Relevancy: **0.93** · Score médio: **0.81**
- Relatório salvo em JSON e exibido na interface

### ✅ Fase 4 — Pipeline RAG
- Busca semântica + GPT-4o-mini integrados end-to-end
- Citação automática de fontes em cada resposta
- Sistema honesto — responde "Não encontrei" quando necessário

### ✅ Fase 3 — Embeddings e Pinecone
- 63 vetores de 1536 dimensões indexados
- Resolvido SSL corporativo Windows via exportação de certificados

### ✅ Fase 2 — Ingestão de PDFs
- 4 documentos técnicos → 63 chunks com metadados

### ✅ Fase 1 — Fundações
- Python 3.11, venv, .gitignore, .env, API OpenAI funcionando

### 🔧 Melhorias identificadas durante o desenvolvimento
- **Ingestão incremental v1** — hash MD5 para detectar mudanças
- **Ingestão incremental v2** — embeddings gerados apenas para chunks alterados, eliminando desperdício de créditos de API *(identificado e corrigido pelo desenvolvedor)*

---

## 🧑‍💻 Sobre o Desenvolvimento

Construído do zero como portfólio de aprendizado em **IA aplicada e Engenharia de Software**. O repositório documenta não apenas o produto final, mas a jornada de aprendizado — com decisões técnicas, problemas encontrados e melhorias propostas pelo próprio desenvolvedor.

---

## 🤝 Contribuições

1. Fork o projeto
2. Crie sua branch: `git checkout -b feat/minha-feature`
3. Commit: `git commit -m 'feat: descrição'`
4. Push: `git push origin feat/minha-feature`
5. Abra um Pull Request

---

## 📄 Licença

Distribuído sob a licença MIT. Veja [LICENSE](LICENSE).

---

<div align="center">

Feito com 🧠 e muito café

⭐ Se este projeto te ajudou, deixe uma estrela!

</div>