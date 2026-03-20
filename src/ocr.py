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
