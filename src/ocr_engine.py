import cv2
import pytesseract
from easyocr import Reader

reader = Reader(['en'], gpu=True)
def run_ocr(enhanced, th, ocr_reader=reader):
    easy_lines = ocr_reader.readtext(enhanced, detail=0, paragraph=True)

    tess1 = pytesseract.image_to_string(
        enhanced,
        config="--psm 6"
    ).split("\n")

    th_inv = cv2.bitwise_not(th)
    tess2 = pytesseract.image_to_string(
        th_inv,
        config="--psm 6 -c tessedit_char_whitelist=0123456789_"
    ).split("\n")

    lines = easy_lines + tess1 + tess2
    lines = [l.strip() for l in lines if len(l.strip()) > 0]
    return lines



