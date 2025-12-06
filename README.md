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
