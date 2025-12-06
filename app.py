import streamlit as st
import cv2
import numpy as np

from src.preprocessing import preprocess_image
from src.ocr_engine import run_ocr
from src.text_extraction import (
    extract_id_from_lines,
    canonical_id,
    fix_with_filename,
)

st.title("Shipping Label OCR Demo")

uploaded_file = st.file_uploader("Upload a waybill image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

    st.image(
        cv2.cvtColor(img, cv2.COLOR_BGR2RGB),
        caption="Uploaded Image",
        use_column_width=True,
    )

    enhanced, th = preprocess_image(img)
    lines = run_ocr(enhanced, th)

    base_name = (
        uploaded_file.name.replace(".jpg", "")
        .replace(".jpeg", "")
        .replace(".png", "")
    )

    raw_pred_id, conf_score = extract_id_from_lines(lines, base_name=base_name)
    pred_id = canonical_id(raw_pred_id)
    pred_id = fix_with_filename(pred_id, base_name)

    st.subheader("Extracted Target ID")
    if pred_id:
        st.write(pred_id)
        if conf_score is not None:
            st.write(f"Confidence (0–1): {conf_score:.3f}")
    else:
        st.write("No valid ID found")

    show_raw = st.checkbox("Show raw OCR text", value=False)
    if show_raw:
        st.subheader("Raw OCR Text (debug)")
        for l in lines:
            st.write(l)
