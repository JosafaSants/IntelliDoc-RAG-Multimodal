import os
import sys
import pytesseract # Biblioteca para tratamento de OCR
from PIL import Image, ImageFilter, ImageEnhance # Biblioteca para manipulação de imagens e tratamento das imagens para o OCR

# Buscando os outros módulos do projeto
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# ============================================================
# CONFIGURAÇÃO DO TESSERACT
# ============================================================
# O pytesseract precisa saber onde o executável do Tesseract
# está instalado. Em vez de hardcodar o caminho (o que quebra
# em qualquer outra máquina), lemos do .env via variável de
# ambiente TESSERACT_CMD.
#
# Se a variável não estiver definida, usamos o caminho padrão
# de instalação do Windows como fallback — ajuste conforme
# seu sistema operacional:
#   Windows : C:\Program Files\Tesseract-OCR\tesseract.exe
#   Linux   : /usr/bin/tesseract  (geralmente já no PATH)
#   Mac     : /usr/local/bin/tesseract
# ============================================================

TESSERACT_CMD = os.getenv(
    "TESSERACT_CMD",
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"  # fallback padrão Windows
)
pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD



def pre_processar_imagem(caminho_imagem):
    """
    Aplica um pré-processamento na imagem para auximar a qualidade do OCR.
    Imagens com baixo contraste ou ruido de imagem, produzem textos com erros.
    Dess forma essa esta auxilia a aumentar a qualidade e precisão do OCR.
    """

    img = Image.open(caminho_imagem)

    # Converte a imagem em preto e braco pois o Tesseract funciona melhor sem cores
    img = img.convert("L")

    # Aumenta o contraste para destar os texto da imagem
    img = ImageEnhance.Contrast(img).enhance(2.0)

    # Aumenta a nitdez para indentificar texto e deifa a imagem mais definida
    img = ImageEnhance.Sharpness(img)  .enhance(2.0)

    # Aplicando um filtro de nitidez
    img = img.filter(ImageFilter.SHARPEN)

    return img

def extrair_texto_imagem(caminho_imagem):
    """
    Extrai texto de uma imagem usando OCR com Tesseract.
    Retorna o texto extraído como string
    """
    nome_arquivo = os.path.basename(caminho_imagem)
    print(f"🖼️  Processando imagem: {nome_arquivo}")

    # Chama a função definida acima que pré-precessa a imagem
    img = pre_processar_imagem(caminho_imagem)

    # Executando o OCR
    # lang="por+eng" → tenta português primeiro, depois inglês para determinar o que esta escrito
    texto = pytesseract.image_to_string(
        img,
        lang= "por+eng",
        config= "--psm 3" # Modo automatico de segmentação de pagina. Analisa a imagem inteira automaticamente, detecta colunas, parágrafos e linhas sozinho
    )

    texto_limpo = "\n".join(
        linha for linha in texto.splitlines() if linha.strip()
    )
    # Vamos remover linhas em branco e espaços desnecessarios
    # O splitlines() vai dividir o texto em uma lista de linhas
    # O filtro 'if linha.strip()' irá descartar linhas que só tem espaços
    # E o join irar unir todas as linhas em uma mesma string

    print(f"... Qtd de caracteres extraídos: {len(texto_limpo)}")
    return texto_limpo

def processar_imagens_pasta(pasta_raw=os.path.join("data", "raw")):
    """
    Processa todas as imagens de uma determinada pasta e irá
    retornar uma lista de dicionários no mesmo formato dos chunks dos PDFs.
    Para que possamos usar o mesmo pipeline e tratar os PDFs e Imagens da mesma forma
    sem alterações significativas ao projeto.
    """

    # Definição dos formatos de imagens aceitaveis para o OCR
    extensoes = {".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp"} # Foi indicado que usar o '{}' substituindo o '[]' torna a leitura da extenção mais rapida.

    # Comparativo dos formatos de imagem aceitavel
    imagens = [
        f for f in os.listdir(pasta_raw)
        if os.path.splitext(f)[1].lower() in extensoes
    ]

    if not imagens:
        print("📭 Nenhuma imagem encontrada em data/raw/")
        return []  # ← Retorna lista vazia — nunca None
    
    print(f"🖼️  {len(imagens)} imagem(ns) encontrada(s)\n")

    paginas = [] # Iremos acumular este objeto lista com os texto no mesmo formato do chunk

    for imagem in imagens:
        caminho = os.path.join(pasta_raw, imagem)
        texto = extrair_texto_imagem(caminho) # Referencia a função acima

        if texto.strip():
            # Monta o dicionario de forma similar a função extrai_texto_pdf() definida na função ingest.py
            paginas.append({
                "texto": texto,
                "pagina": 1,
                "arquivo": imagem
            })
            
        else:
            print(f"   ⚠️  Nenhum texto encontrado em {imagem}")

    return paginas


if __name__ == "__main__":
    # Este bloco só executa quando rodamos python src/ocr.py diretamente
    # Quando o módulo é importado por outro arquivo, este bloco é ignorado
    paginas = processar_imagens_pasta(
        os.path.join("data", "raw")
    )

    if paginas:
        print(f"\n✅ {len(paginas)} imagem(ns) processada(s)")
        print(f"\n📋 Preview do primeiro resultado:")
        print(f"   Arquivo : {paginas[0]['arquivo']}")
        print(f"   Texto   : {paginas[0]['texto'][:200]}...")
    else:
        print("\n❌ Nenhum texto extraído.")