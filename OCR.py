import easyocr
from Preprocess import img_preprocess, text_preprocess

reader = easyocr.Reader(['en'],gpu=True)

def perform_ocr(image):
    image = img_preprocess(image)
    text = reader.readtext(image)
    extracted_text = ' '.join([res[1] for res in text])
    final_text = text_preprocess(extracted_text)
    return final_text