<div align="center">

# 🧠 IntelliDoc RAG Multimodal

**Sistema de Perguntas & Respostas sobre Documentos com IA**

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![LangChain](https://img.shields.io/badge/LangChain-0.1+-1C3C3C?style=for-the-badge&logo=chainlink&logoColor=white)](https://langchain.com)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-412991?style=for-the-badge&logo=openai&logoColor=white)](https://openai.com)
[![Pinecone](https://img.shields.io/badge/Pinecone-Vector_DB-00BFA5?style=for-the-badge)](https://pinecone.io)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Em_Desenvolvimento-orange?style=for-the-badge)]()

<br/>

> Ingere PDFs e imagens, transforma em embeddings semânticos, armazena em banco vetorial  
> e responde perguntas com GPT-4 — com avaliação automática de fidelidade para evitar alucinações.

<br/>

![Demo](https://placehold.co/900x400/1a1a2e/4fc3f7?text=🎬+Demo+em+breve&font=montserrat)

</div>

---

## 📌 O que é este projeto?

O **IntelliDoc RAG Multimodal** é um sistema completo de *Retrieval-Augmented Generation* (RAG) que permite fazer perguntas em linguagem natural sobre qualquer documento técnico — PDFs ou imagens com texto — e receber respostas precisas, fundamentadas e com citação da fonte.

O diferencial está no **pipeline de avaliação automática**: cada resposta é pontuada em métricas de *fidelidade*, *relevância* e *precisão de contexto* usando a biblioteca RAGAS, tornando o sistema auditável e confiável.

---

## ✨ Funcionalidades

| Funcionalidade | Descrição |
|---|---|
| 📄 **Ingestão de PDFs** | Extração de texto com metadados (página, seção) via PyMuPDF |
| 🖼️ **OCR de Imagens** | Reconhecimento óptico de texto em imagens com Tesseract |
| 🔢 **Embeddings Semânticos** | Vetorização com `text-embedding-3-small` da OpenAI |
| 🗄️ **Banco Vetorial** | Armazenamento e busca por similaridade no Pinecone |
| 🤖 **Respostas com GPT-4** | Geração de respostas fundamentadas no contexto recuperado |
| 📊 **Avaliação RAGAS** | Métricas automáticas: faithfulness, answer relevancy, context precision |
| 🛡️ **Anti-Alucinação** | Guardrails que bloqueiam respostas abaixo do threshold de fidelidade |
| 💬 **Memória de Conversa** | Histórico de perguntas para contexto em conversas longas |
| 🌐 **Interface Web** | Chat interativo via Streamlit com upload de documentos |

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
  │ Pergunta │──Embed───▶│    GPT-4     │◀──Top-K───│    Busca     │
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
| LLM | OpenAI GPT-4 | latest |
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
- Conta OpenAI com API Key
- Conta Pinecone com API Key

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/intellidoc-rag.git
cd intellidoc-rag
```

### 2. Crie e ative o ambiente virtual

```bash
# Criar venv
python -m venv venv

# Ativar (Windows)
venv\Scripts\activate

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
cp .env.example .env

# Edite o .env com suas chaves
OPENAI_API_KEY=sk-...
PINECONE_API_KEY=...
PINECONE_INDEX_NAME=intellidoc
```

### 5. Execute a interface

```bash
streamlit run src/app.py
```

Acesse `http://localhost:8501` no navegador. 🎉

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

- [x] Estrutura inicial do projeto
- [ ] **Fase 1** — Ambiente e configuração inicial
- [ ] **Fase 2** — Pipeline de ingestão (PDF + OCR)
- [ ] **Fase 3** — Embeddings e banco vetorial
- [ ] **Fase 4** — Pipeline RAG completo
- [ ] **Fase 5** — Avaliação RAGAS e anti-alucinação
- [ ] **Fase 6** — Interface Streamlit e publicação

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
