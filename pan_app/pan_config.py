from pan_car.settings import BASE_DIR
import os
import pytesseract
model_name='pancard.pt'
model_path=os.path.join(BASE_DIR,'pan_app',model_name)

pytteseract = r"/usr/bin/tesseract"
# pytteseract = r'C:\Users\Pravin Bhosure\AppData\Local\Tesseract-OCR\\tesseract.exe'
pytesseract.pytesseract.tesseract_cmd = pytteseract