<div align="center">

# 🧠 IntelliDoc RAG Multimodal

**Sistema de Perguntas & Respostas sobre Documentos com IA**

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
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
| 📄 **Ingestão de PDFs** | Extração de texto com metadados via PyMuPDF | ✅ Concluído |
| 🔪 **Chunking Inteligente** | Divisão em chunks com overlap via LangChain | ✅ Concluído |
| 🔢 **Embeddings Semânticos** | Vetorização com `text-embedding-3-small` da OpenAI | ✅ Concluído |
| 🗄️ **Banco Vetorial Pinecone** | 63 vetores indexados, busca semântica funcionando | ✅ Concluído |
| 🔗 **Pipeline RAG Completo** | Busca semântica + GPT-4o-mini integrados | ✅ Concluído |
| 🛡️ **Respostas Honestas** | Sistema diz quando não encontra a informação | ✅ Concluído |
| 🖼️ **OCR de Imagens** | Reconhecimento óptico de texto com Tesseract | 🔄 Em breve |
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
  │  Imagem  │─Tesseract─▶              │           │  ✅ 63 docs  │
  └──────────┘           └──────────────┘           └──────┬───────┘
                                                           │
  💬 QUERY                🤖 GENERATION ✅           🔍 RETRIEVAL ✅
  ┌──────────┐           ┌──────────────┐           ┌──────────────┐
  │ Pergunta │──Embed───▶│  GPT-4o-mini │◀──Top-K───│    Busca     │
  │  do User │           │  + Contexto  │           │  Semântica   │
  └──────────┘           └──────┬───────┘           └──────────────┘
                                │
  📊 EVALUATION           📤 OUTPUT ✅
  ┌──────────────┐       ┌──────────────┐
  │    RAGAS     │◀──────│   Resposta   │
  │  Faithfulness│       │ + Fontes     │
  │  Relevancy   │       │ + Score      │
  └──────────────┘       └──────────────┘
```

---

## 💬 Exemplo de Uso

```
🔍 Pergunta: Quais são as boas práticas de segurança em APIs REST?

1️⃣  Gerando embedding da pergunta...
2️⃣  Buscando chunks relevantes no Pinecone... (5 chunks encontrados)
3️⃣  Montando prompt com contexto...
4️⃣  Gerando resposta com GPT-4o-mini...

✅ RESPOSTA:
As boas práticas de segurança em APIs REST incluem:
1. Uso de JWT com tempo de expiração curto (15-60 min)
2. Princípio do menor privilégio em todos os componentes
3. Monitoramento e logs de tentativas de autenticação
[Fonte: manual_seguranca_apis.pdf, páginas 2-3]

📁 Fontes consultadas: ['manual_seguranca_apis.pdf']
```

---

## 🛠️ Stack Tecnológica

| Categoria | Tecnologia | Versão |
|---|---|---|
| Linguagem | Python | 3.11 ✅ |
| Orquestração IA | LangChain | 0.1+ |
| LLM | OpenAI GPT-4o-mini | latest |
| Embeddings | OpenAI text-embedding-3-small | latest |
| Banco Vetorial | Pinecone | 8.1+ |
| Parser PDF | PyMuPDF (fitz) | 1.27+ |
| Chunking | LangChain Text Splitters | 0.1+ |
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
│   └── processed/
│       └── chunks.json           # 63 chunks extraídos com metadados ✅
│
├── 📂 src/
│   ├── ingest.py                 # ✅ Ingestão multi-PDF com chunking
│   ├── embeddings.py             # ✅ Geração de embeddings OpenAI
│   ├── vector_store.py           # ✅ Interface com Pinecone + busca semântica
│   ├── rag_pipeline.py           # ✅ Pipeline RAG completo end-to-end
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

- Python 3.11
- Conta OpenAI com API Key e créditos
- Conta Pinecone com API Key

### 1. Clone o repositório

```bash
git clone https://github.com/JosafaSants/IntelliDoc-RAG-Multimodal.git
cd IntelliDoc-RAG-Multimodal
```

### 2. Crie e ative o ambiente virtual

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

### 5. Execute o pipeline completo

```bash
# 1. Ingira os documentos
python src/ingest.py

# 2. Indexe no Pinecone
python src/vector_store.py

# 3. Faça perguntas!
python src/rag_pipeline.py
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

---

## 🗺️ Roadmap

- [x] **Fase 1** — Ambiente, Git, VS Code e API OpenAI conectada ✅
- [x] **Fase 2** — Pipeline de ingestão multi-PDF com chunking ✅
- [x] **Fase 3** — Embeddings e banco vetorial Pinecone ✅
- [x] **Fase 4** — Pipeline RAG completo end-to-end ✅
- [ ] **Fase 5** — Avaliação RAGAS e anti-alucinação 🔄
- [ ] **Fase 6** — Interface Streamlit e publicação

---

## 📝 Diário de Desenvolvimento

### ✅ Fase 4 — Concluída em 13/03/2026
- Pipeline RAG end-to-end funcionando: pergunta → embedding → busca → GPT-4o-mini → resposta
- Prompt engineering com system prompt focado em fidelidade ao contexto
- Citação automática de fontes (arquivo + página) em cada resposta
- Sistema honesto: responde "Não encontrei essa informação" quando o contexto não cobre a pergunta
- Temperatura 0.1 para respostas mais determinísticas e precisas
- Testado com 3 perguntas cobrindo diferentes documentos do corpus

### ✅ Fase 3 — Concluída em 13/03/2026
- Geração de embeddings com `text-embedding-3-small` da OpenAI (1536 dimensões)
- Índice `intellidoc` criado no Pinecone (serverless, AWS us-east-1)
- 63 vetores inseridos em 2 lotes via upsert
- Busca semântica testada e funcionando
- Resolvido problema de certificado SSL em ambiente corporativo Windows

### ✅ Fase 2 — Concluída em 13/03/2026
- Pipeline de ingestão de PDFs com PyMuPDF funcionando
- Chunking inteligente com `RecursiveCharacterTextSplitter` do LangChain
- 4 documentos técnicos ingeridos → 63 chunks gerados com metadados

### ✅ Fase 1 — Concluída em 13/03/2026
- Ambiente Python 3.11 configurado com `venv` no Windows
- Estrutura de pastas e `.gitignore` criados
- Variáveis de ambiente seguras com `python-dotenv`
- Primeira chamada à API da OpenAI funcionando com `gpt-4o-mini`

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
