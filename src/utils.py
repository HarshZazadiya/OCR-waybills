import os
import json

import cv2
import pandas as pd
from rapidfuzz.distance import Levenshtein

from .preprocessing import preprocess_image
from .ocr_engine import run_ocr
from .text_extraction import (
    canonical_id,
    fix_with_filename,
    extract_id_from_lines,
)


def load_ground_truth(gt_csv_path, img_col="Image", gt_col="ground_truth"):
    """
    Load and clean ground truth CSV into a dict: {image_name: canonical_gt_id}
    """
    gt_csv = pd.read_csv(gt_csv_path)

    gt_csv[img_col] = gt_csv[img_col].astype(str).str.strip()
    gt_csv[gt_col] = gt_csv[gt_col].astype(str).str.strip()

    gt_dict = {}
    for img_name, gt_raw in zip(gt_csv[img_col], gt_csv[gt_col]):
        gt_clean = canonical_id(gt_raw)
        if gt_clean is not None:
            gt_dict[img_name] = gt_clean

    return gt_dict


def evaluate_dataset(image_dir, gt_csv_path, output_json_path="results/final_ocr_results.json"):
    """
    Main evaluation:
    - Walk over images in image_dir
    - Run OCR + extraction
    - Compare with ground truth
    - Save JSON + return metrics
    """
    os.makedirs(os.path.dirname(output_json_path), exist_ok=True)

    gt_dict = load_ground_truth(gt_csv_path)
    print("Total GT rows (after cleaning):", len(gt_dict))

    results = []
    correct = 0
    total = 0

    for fname in sorted(os.listdir(image_dir)):
        if not fname.lower().endswith(".jpg"):
            continue

        fpath = os.path.join(image_dir, fname)
        base = fname.replace(".jpg", "").strip()

        print("\nProcessing:", base)

        img = cv2.imread(fpath)
        if img is None:
            print("Could not read:", fpath)
            continue

        enhanced, th = preprocess_image(img)
        lines = run_ocr(enhanced, th)

        raw_pred_id, conf_score = extract_id_from_lines(lines, base_name=base)
        pred_id = canonical_id(raw_pred_id)
        pred_id = fix_with_filename(pred_id, base)

        gt_id = gt_dict.get(base, None)

        print("Pred (raw):", raw_pred_id)
        print("Pred canon:", pred_id)
        print("GT canon  :", gt_id)
        print("Confidence:", conf_score)

        has_gt = gt_id is not None

        if has_gt:
            total += 1
            ok = (pred_id == gt_id)
            if ok:
                correct += 1
        else:
            ok = False

        results.append({
            "image": base,
            "raw_prediction": raw_pred_id,
            "prediction": pred_id,
            "ground_truth": gt_id,
            "correct": ok,
            "confidence_score": conf_score,
        })

    accuracy = (correct / total * 100) if total > 0 else 0.0

    # CHARACTER ERROR RATE
    cer_list = []
    for r in results:
        gt = r["ground_truth"]
        pr = r["prediction"]
        if gt and pr:
            d = Levenshtein.distance(gt, pr)
            cer = d / len(gt)
            cer_list.append(cer)

    avg_cer = sum(cer_list) / len(cer_list) if cer_list else 0

    # save JSON
    with open(output_json_path, "w") as f:
        json.dump(results, f, indent=4)

    print("\n==============================")
    print(" Labeled images:", total)
    print(" Correct       :", correct)
    print(" FINAL ACCURACY (exact '<digits>_1'):", accuracy)
    print(" Average CER   :", avg_cer)
    print("==============================")
    print("Saved results to:", output_json_path)

    return {
        "results": results,
        "accuracy": accuracy,
        "avg_cer": avg_cer,
        "total": total,
        "correct": correct,
    }


if __name__ == "__main__":
    # Example paths – adjust for your environment / Colab
    IMAGE_DIR = "/content/drive/MyDrive/ReverseWayBill"
    GT_CSV = "/content/drive/MyDrive/ReverseWayBill_groundtruth/ground_truth.csv"

    evaluate_dataset(
        image_dir=IMAGE_DIR,
        gt_csv_path=GT_CSV,
        output_json_path="results/final_ocr_results_with_conf.json",
    )
