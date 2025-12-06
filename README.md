# OCR Shipping Label Extraction

OCR pipeline to extract the `<digits>_1` ID from shipping label / waybill images.

## Structure

- `src/preprocessing.py` – image preprocessing
- `src/ocr_engine.py` – OCR (EasyOCR + Tesseract)
- `src/text_extraction.py` – ID extraction / canonicalization
- `src/utils.py` – evaluation, metrics, JSON saving
- `app.py` – Streamlit demo
- `results/` – OCR results & metrics

## Running evaluation

```bash
python -m src.utils

<img width="1919" height="1108" alt="image" src="https://github.com/user-attachments/assets/84af164f-1d22-4872-8901-c27b35027526" />
