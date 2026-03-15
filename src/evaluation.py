import os
import sys
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from rag_pipeline import rag_query, construir_prompt
from embeddings import gerar_embedding
from vector_store import conectar_pinecone, buscar

load_dotenv()

def