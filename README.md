<div align="center">

# 🧠 IntelliDoc RAG Multimodal

**Sistema de Perguntas & Respostas sobre Documentos com IA**

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![LangChain](https://img.shields.io/badge/LangChain-0.1+-1C3C3C?style=for-the-badge&logo=chainlink&logoColor=white)](https://langchain.com)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-412991?style=for-the-badge&logo=openai&logoColor=white)](https://openai.com)
[![Pinecone](https://img.shields.io/badge/Pinecone-Vector_DB-00BFA5?style=for-the-badge)](https://pinecone.io)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Em_Desenvolvimento-orange?style=for-the-badge)]()

<br/>

> Ingere PDFs e imagens, transforma em embeddings semânticos, armazena em banco vetorial  
> e responde perguntas com GPT-4o-mini — com avaliação automática de fidelidade para evitar alucinações.

<br/>

![Demo](https://placehold.co/900x400/1a1a2e/4fc3f7?text=🎬+Demo+em+breve&font=montserrat)

</div>

---

## 📌 O que é este projeto?

O **IntelliDoc RAG Multimodal** é um sistema completo de *Retrieval-Augmented Generation* (RAG) que permite fazer perguntas em linguagem natural sobre qualquer documento técnico — PDFs ou imagens com texto — e receber respostas precisas, fundamentadas e com citação da fonte.

O diferencial está no **pipeline de avaliação automática**: cada resposta é pontuada em métricas de *fidelidade*, *relevância* e *precisão de contexto* usando a biblioteca RAGAS, tornando o sistema auditável e confiável.

> 📖 **Projeto de portfólio em construção** — desenvolvido do zero com documentação de cada decisão técnica e aprendizado. Acompanhe a evolução pelos [commits](../../commits) e [issues](../../issues).

---

## ✨ Funcionalidades

| Funcionalidade | Descrição | Status |
|---|---|---|
| 📄 **Ingestão de PDFs** | Extração de texto com metadados via PyMuPDF | 🔄 Em breve |
| 🖼️ **OCR de Imagens** | Reconhecimento óptico de texto com Tesseract | 🔄 Em breve |
| 🔢 **Embeddings Semânticos** | Vetorização com `text-embedding-3-small` da OpenAI | 🔄 Em breve |
| 🗄️ **Banco Vetorial** | Armazenamento e busca por similaridade no Pinecone | 🔄 Em breve |
| 🤖 **Respostas com GPT-4o-mini** | Geração de respostas fundamentadas no contexto | ✅ Conectado |
| 📊 **Avaliação RAGAS** | Métricas: faithfulness, answer relevancy, context precision | 🔄 Em breve |
| 🛡️ **Anti-Alucinação** | Guardrails que bloqueiam respostas abaixo do threshold | 🔄 Em breve |
| 💬 **Memória de Conversa** | Histórico para contexto em conversas longas | 🔄 Em breve |
| 🌐 **Interface Web** | Chat interativo via Streamlit com upload de documentos | 🔄 Em breve |

---

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                    IntelliDoc RAG Multimodal                 │
└─────────────────────────────────────────────────────────────┘

  📂 INPUT                🔄 PROCESSING              🗄️ STORAGE
  ┌──────────┐           ┌──────────────┐           ┌──────────────┐
  │   PDF    │──PyMuPDF──▶              │           │              │
  └──────────┘           │   Chunking   │──Embed───▶│   Pinecone   │
  ┌──────────┐           │  + Metadata  │           │ Vector Store │
  │  Imagem  │─Tesseract─▶              │           │              │
  └──────────┘           └──────────────┘           └──────┬───────┘
                                                           │
  💬 QUERY                🤖 GENERATION              🔍 RETRIEVAL
  ┌──────────┐           ┌──────────────┐           ┌──────────────┐
  │ Pergunta │──Embed───▶│  GPT-4o-mini │◀──Top-K───│    Busca     │
  │  do User │           │  + Contexto  │           │  Semântica   │
  └──────────┘           └──────┬───────┘           └──────────────┘
                                │
  📊 EVALUATION           📤 OUTPUT
  ┌──────────────┐       ┌──────────────┐
  │    RAGAS     │◀──────│   Resposta   │
  │  Faithfulness│       │ + Fontes     │
  │  Relevancy   │       │ + Score      │
  └──────────────┘       └──────────────┘
```

---

## 🛠️ Stack Tecnológica

| Categoria | Tecnologia | Versão |
|---|---|---|
| Linguagem | Python | 3.10+ |
| Orquestração IA | LangChain | 0.1+ |
| LLM | OpenAI GPT-4o-mini | latest |
| Embeddings | OpenAI text-embedding-3-small | latest |
| Banco Vetorial | Pinecone | 3.0+ |
| Parser PDF | PyMuPDF (fitz) | 1.23+ |
| OCR | Tesseract + pytesseract | 5.0+ |
| Avaliação | RAGAS | 0.1+ |
| Interface | Streamlit | 1.30+ |
| Gerenciamento env | python-dotenv | 1.0+ |

---

## 📁 Estrutura do Projeto

```
intellidoc-rag/
│
├── 📄 README.md                  # Este arquivo
├── 📋 requirements.txt           # Dependências Python
├── 🔒 .env.example               # Modelo de variáveis de ambiente
├── 🚫 .gitignore                 # Ignora .env, venv, __pycache__
│
├── 📂 data/
│   ├── raw/                      # PDFs e imagens originais
│   └── processed/                # Chunks extraídos em JSON
│
├── 📂 src/
│   ├── ingest.py                 # Ingestão: PDF + OCR
│   ├── embeddings.py             # Geração de embeddings OpenAI
│   ├── vector_store.py           # Interface com Pinecone
│   ├── rag_pipeline.py           # Pipeline RAG completo
│   ├── evaluation.py             # Métricas RAGAS
│   └── app.py                    # Interface Streamlit
│
├── 📂 tests/
│   └── test_pipeline.py          # Testes automatizados
│
├── 📂 notebooks/
│   └── exploration.ipynb         # Experimentos e protótipos
│
└── 📂 docs/
    └── architecture.md           # Documentação da arquitetura
```

---

## 🚀 Como Executar

### Pré-requisitos

- Python 3.10+
- Tesseract OCR instalado no sistema ([guia de instalação](https://github.com/tesseract-ocr/tesseract))
- Conta OpenAI com API Key e créditos
- Conta Pinecone com API Key

### 1. Clone o repositório

```bash
git clone https://github.com/JosafaSants/IntelliDoc-RAG-Multimodal.git
cd IntelliDoc-RAG-Multimodal
```

### 2. Crie e ative o ambiente virtual

```bash
# Criar venv
python -m venv venv

# Ativar (Windows)
venv\Scripts\Activate.ps1

# Ativar (Mac/Linux)
source venv/bin/activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente

```bash
# Copie o arquivo de exemplo
copy .env.example .env

# Edite o .env com suas chaves reais
OPENAI_API_KEY=sk-...
PINECONE_API_KEY=...
PINECONE_INDEX_NAME=intellidoc
```

### 5. Execute o teste de conexão

```bash
python src/test_api.py
```

---

## 📊 Métricas de Avaliação (RAGAS)

O sistema avalia automaticamente cada resposta gerada:

| Métrica | Descrição | Threshold |
|---|---|---|
| **Faithfulness** | A resposta é fiel ao contexto recuperado? | ≥ 0.80 |
| **Answer Relevancy** | A resposta é relevante para a pergunta? | ≥ 0.75 |
| **Context Precision** | O contexto recuperado é preciso? | ≥ 0.70 |
| **Context Recall** | Todo contexto necessário foi recuperado? | ≥ 0.70 |

Respostas abaixo do threshold de **faithfulness** são bloqueadas automaticamente para evitar alucinações.

---

## 🗺️ Roadmap

- [x] **Fase 1** — Ambiente, Git, VS Code e API OpenAI conectada ✅
- [ ] **Fase 2** — Pipeline de ingestão (PDF + OCR) 🔄
- [ ] **Fase 3** — Embeddings e banco vetorial
- [ ] **Fase 4** — Pipeline RAG completo
- [ ] **Fase 5** — Avaliação RAGAS e anti-alucinação
- [ ] **Fase 6** — Interface Streamlit e publicação

---

## 📝 Diário de Desenvolvimento

### ✅ Fase 1 — Concluída em 13/03/2026
- Ambiente Python configurado com `venv` no Windows
- Estrutura de pastas e `.gitignore` criados
- Variáveis de ambiente seguras com `python-dotenv`
- Primeira chamada à API da OpenAI funcionando com `gpt-4o-mini`
- Repositório publicado no GitHub

---

## 🧑‍💻 Sobre o Desenvolvimento

Este projeto está sendo construído do zero como portfólio de aprendizado em **IA aplicada e Engenharia de Software**. Cada fase documenta decisões técnicas, problemas encontrados e aprendizados — tornando o repositório não apenas um produto final, mas um registro de evolução real.

Se você também está aprendendo, fique à vontade para acompanhar o progresso pelas [Issues](../../issues) e [commits](../../commits).

---

## 🤝 Contribuições

Contribuições, sugestões e feedbacks são bem-vindos!

1. Fork o projeto
2. Crie sua branch: `git checkout -b feat/minha-feature`
3. Commit suas mudanças: `git commit -m 'feat: adiciona nova feature'`
4. Push para a branch: `git push origin feat/minha-feature`
5. Abra um Pull Request

---

## 📄 Licença

Distribuído sob a licença MIT. Veja [LICENSE](LICENSE) para mais informações.

---

<div align="center">

Feito com 🧠 e muito café

⭐ Se este projeto te ajudou, deixe uma estrela no repositório!

</div>
