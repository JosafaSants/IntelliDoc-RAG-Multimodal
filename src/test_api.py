from dotenv import load_dotenv
import os
from openai import OpenAI

# Carrega as variáveis do arquivo .env
load_dotenv()

# Conecta com a API da OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

print("Conectando com GPT-4...")

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Responda em português em 2 linhas: O que é RAG em IA?"}]
)

print("\n✅ Resposta do GPT-4:")
print(response.choices[0].message.content)