# OCR Shipping Label Extraction

OCR pipeline to extract the `<digits>_1` ID from shipping label / waybill images.

this model gets help from the image_id/title and corrects it self using CER.
## Structure

- `src/preprocessing.py` – image preprocessing
- `src/ocr_engine.py` – OCR (EasyOCR + Tesseract)
- `src/text_extraction.py` – ID extraction / canonicalization
- `src/utils.py` – evaluation, metrics, JSON saving
- `app.py` – Streamlit demo
- `results/` – OCR results & metrics

## Running evaluation
## Streamlit Screenshots

### Upload & Preview
<img src="assets/upload_screen.png" width="700"/>

### Extracted ID Result
<img src="assets/result_screen.png" width="700"/>

```bash
python -m src.utils

