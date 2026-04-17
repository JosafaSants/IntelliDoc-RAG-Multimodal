import os
import sys
from dotenv import load_dotenv
from openai import OpenAI

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from embeddings import gerar_embedding
from vector_store import conectar_pinecone, buscar
from memory import inicializar_banco, salvar_mensagem, carregar_historico  # Importa as funções de memória persistente

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Garante que o banco SQLite existe antes de qualquer consulta
inicializar_banco()


def construir_prompt(pergunta, chunks_relevantes): # Função para construir o prompt a ser enviado para o modelo de linguagem, usando os chunks relevantes encontrados
    """Monta o prompt com contexto dos chunks recuperados."""
    contexto = "" # Define a vairiavel contexto como string vazia para acumular as informações dos chunks relevantes
    for i, chunk in enumerate(chunks_relevantes): # Cria as Fonte 1, Fonte 2, etc. para cada chunk relevante encontrado, e adiciona o conteúdo do chunk a variavel contexto.
        arquivo = chunk.metadata['arquivo'] # Extrai o nome do arquivo do metadata do chunk
        pagina = chunk.metadata['pagina'] # Extrai o número da página do metadata do chunk
        texto = chunk.metadata['texto'] # Extrai o texto do chunk do metadata do chunk
        contexto += f"\n[Fonte {i+1}: {arquivo}, página {pagina}]\n{texto}\n" # Adiciona o conteúdo do chunk ao contexto, formatando com o nome do arquivo e número da página

    prompt = f"""Você é um assistente especializado em responder perguntas sobre documentos técnicos.
Use APENAS as informações fornecidas no contexto abaixo para responder.
Se a resposta não estiver no contexto, diga: "Não encontrei essa informação nos documentos."
Sempre cite a fonte (arquivo e página) ao final da resposta.

CONTEXTO:
{contexto} 

PERGUNTA: {pergunta}

RESPOSTA:"""
    return prompt


def rag_query(pergunta, top_k=5):
    """Pipeline RAG completo: busca + geração + memória persistente."""
    print(f"\n🔍 Pergunta: {pergunta[:50]}{'...' if len(pergunta) > 50 else ''}")
    print("─" * 60)

    # 1. Converte pergunta em embedding
    print("1️⃣  Gerando embedding da pergunta...")
    embedding_query = gerar_embedding(pergunta)

    # 2. Busca chunks relevantes no Pinecone
    print("2️⃣  Buscando chunks relevantes no Pinecone...")
    indice = conectar_pinecone()
    chunks_relevantes = buscar(indice, embedding_query, top_k=top_k)
    print(f"   {len(chunks_relevantes)} chunks encontrados")

    # 3. Carrega histórico de conversas anteriores do SQLite
    # Limita a 10 mensagens para não inflar o contexto enviado ao GPT
    print("3️⃣  Carregando histórico de conversas...")
    historico = carregar_historico(limite=10)

    # 4. Monta o prompt com contexto dos chunks + histórico
    print("4️⃣  Montando prompt com contexto...")
    prompt = construir_prompt(pergunta, chunks_relevantes)

    # Converte o histórico em formato de mensagens para o GPT
    # Cada par pergunta/resposta vira dois turnos: user + assistant
    mensagens = []
    for entrada in historico:
        mensagens.append({"role": "user",      "content": entrada["pergunta"]})
        mensagens.append({"role": "assistant", "content": entrada["resposta"]})

    # Adiciona a pergunta atual como última mensagem
    mensagens.append({"role": "user", "content": prompt})

    # 5. Gera resposta com GPT-4o-mini
    print("5️⃣  Gerando resposta com GPT-4o-mini...")
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=mensagens,  # Histórico completo + pergunta atual
        temperature=0.1
    )

    resposta = response.choices[0].message.content

    # 6. Salva o par pergunta/resposta no banco SQLite
    # Garante que a conversa persiste entre sessões
    fontes = list(set([c.metadata['arquivo'] for c in chunks_relevantes]))
    salvar_mensagem(pergunta, resposta, fontes)
    print("💾 Conversa salva no histórico.")

    print("\n✅ RESPOSTA:")
    print("─" * 60)
    print(resposta)
    print("─" * 60)

    return {
        "pergunta": pergunta,
        "resposta": resposta,
        "chunks_usados": len(chunks_relevantes),
        "fontes": fontes
    }


if __name__ == "__main__":
    # Testa com 3 perguntas diferentes
    perguntas = [
        "O que é RAG e quais são seus componentes principais?",
        "Quais são as boas práticas de segurança em APIs REST?",
        "Como funciona o chunking em projetos de Data Science?"
    ]

    for pergunta in perguntas:
        resultado = rag_query(pergunta)
        print(f"\n📁 Fontes consultadas: {resultado['fontes']}")
        print("\n" + "═" * 60 + "\n")
        