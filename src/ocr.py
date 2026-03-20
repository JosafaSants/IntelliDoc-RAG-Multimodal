import os
import sys
import pytesseract # Biblioteca para tratamento de OCR
from PIL import Image, ImageFilter, ImageEnhance # Biblioteca para manipulação de imagens e tratamento das imagens para o OCR

# Buscando os outros módulos do projeto
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Busca o local no qual o tesseract está instalado
# O pytesseract precisa saber o local do tesseract para funcionar, caso contrário, ele não conseguirá realizar o OCR
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Users\JosafaBarbosadosSant\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"
)



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