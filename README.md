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

![image alt](https://github.com/HarshZazadiya/ORC-waybills/blob/9627550f2b5386b9d77ae0f7493e1f18fa3e1719/Screenshot%202025-12-07%20000644.png)
