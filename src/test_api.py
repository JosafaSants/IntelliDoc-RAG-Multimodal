from dotenv import load_dotenv # Carrega a biblioteca para ler variáveis de fornecidas em um arquivo .env
import os # Biblioteca para acessar variáveis do sistema operacional
from openai import OpenAI # Biblioteca oficial da OpenAI para acessar a API de modelos de linguagem, como o GPT-4, ou no nosso caso, o gpt-4o-mini, que é uma versão otimizada e mais barata do GPT-4, mas ainda muito poderosa para muitas tarefas

# Carrega as variáveis do arquivo .env
load_dotenv()

# Conecta com a API da OpenAI a partir da chave de API fornecida no arquivo .env, criando um cliente que será usado para fazer chamadas à API e gerar respostas usando o modelo GPT-4.
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

print("Conectando com GPT-4...") # Imprime uma mensagem para indicar que estamos conectando com o modelo GPT-4

response = client.chat.completions.create( # Cria uma resposta usando o modelo de chat da OpenAi Gpt-4o-mini
    model="gpt-4o-mini", # Define o modelo a ser usado no script, no caso o gpt-4o-mini
    messages=[{"role": "user", "content": "Responda em português em 2 linhas: O que é RAG em IA?"}] # Define o prompt, ou seja, a mensagem que será enviada para o modelo, onde o usuário pergunta "O que é RAG em IA?" e pede para responder em português e em 2 linhas
)

print("\n✅ Resposta do GPT-4:") 
print(response.choices[0].message.content) # Retorna a reposta gerada na definição da variável response, acessando a primeira escolha (choices[0]) e o conteúdo da mensagem (message.content) para imprimir a resposta do modelo GPT-4.