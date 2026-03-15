import os
import sys
from dotenv import load_dotenv
from openai import OpenAI

# Adiciona o src ao path para importar os módulos de embeddings e vector_store
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from embeddings import gerar_embedding # Função para gerar embedding usando OpenAI definida em embeddings.py
from vector_store import conectar_pinecone, buscar # Funções para conectar e buscar no Pinecone definidas em vector_store.py

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY")) # Busca a chave da API do OpenAI do arquivo .env


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
    """Pipeline RAG completo: busca + geração."""
    print(f"\n🔍 Pergunta: {pergunta}")
    print("─" * 60)

    # 1. Converte pergunta em embedding
    print("1️⃣  Gerando embedding da pergunta...")
    embedding_query = gerar_embedding(pergunta) # Converte a pergunta do usuário em um vetor de embedding usando a função gerar_embedding definida em embeddings.py, que utiliza a API do OpenAI para criar uma representação vetorial da pergunta, permitindo que ela seja comparada com os embeddings dos chunks armazenados no Pinecone para encontrar os mais relevantes.

    # 2. Busca chunks relevantes no Pinecone
    print("2️⃣  Buscando chunks relevantes no Pinecone...")
    indice = conectar_pinecone() # Conecta ao Pinecone usando a função conectar_pinecone definida em vector_store.py, que inicializa a conexão com o serviço do Pinecone e retorna um objeto de índice que pode ser usado para realizar consultas de busca semântica.
    chunks_relevantes = buscar(indice, embedding_query, top_k=top_k) # Cria uma lista de chunks relevantes usando a função buscar definida em vector_store.py, que realiza uma consulta de busca semântica no índice do Pinecone usando o embedding da pergunta e retorna os chunks mais similares, com base na similaridade dos embeddings, permitindo que o sistema encontre informações relevantes mesmo que as palavras exatas não estejam presentes na pergunta do usuário.
    print(f"   {len(chunks_relevantes)} chunks encontrados")

    # 3. Monta o prompt com contexto
    print("3️⃣  Montando prompt com contexto...")
    prompt = construir_prompt(pergunta, chunks_relevantes) # Constrói o prompt a ser enviado para o gpt-4o-mini, definido na função construir_prompt.

    # 4. Gera resposta com GPT-4o-mini
    print("4️⃣  Gerando resposta com GPT-4o-mini...")
    response = client.chat.completions.create( # Acessa a API da OpenAI para gerar uma resposta baseada no prompt construído.
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1  # Baixo para respostas mais precisas, menos criativas.
    )

    resposta = response.choices[0].message.content

    print("\n✅ RESPOSTA:")
    print("─" * 60)
    print(resposta)
    print("─" * 60)

    return {
        "pergunta": pergunta,
        "resposta": resposta,
        "chunks_usados": len(chunks_relevantes),
        "fontes": list(set([c.metadata['arquivo'] for c in chunks_relevantes]))
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
        