import re


def hamming_like(a, b):
    """
    Hamming-like distance that also penalizes length differences.
    """
    la, lb = len(a), len(b)
    m = min(la, lb)
    diff = sum(1 for i in range(m) if a[i] != b[i])
    diff += abs(la - lb) * 2
    return diff


def canonical_id(text):
    """
    Turn any raw text into canonical '<digits>_1' or None.
    Handles junk like '..._1.xxx' or '-1234_1'.
    """
    if text is None:
        return None
    t = str(text)
    # normalize obvious confusions a bit
    t = t.replace("O", "0").replace("o", "0")
    t = t.replace("I", "1").replace("l", "1")
    # keep only digits and underscore
    t = re.sub(r"[^0-9_]", "", t)
    m = re.search(r"(\d+_1)", t)
    return m.group(1) if m else None


def fix_with_filename(pred_id, base_name):
    """
    Given 'pred_id' (like '160796797970200578_1') and filename
    'reverseWaybill-160390797970200578_1', correct obvious digit errors.
    """
    if pred_id is None or base_name is None:
        return pred_id

    # extract reference numeric part from filename
    m = re.search(r"(\d+)_1$", base_name)
    if not m:
        return pred_id
    ref = m.group(1)

    # extract numeric from prediction
    m2 = re.search(r"(\d+)_1$", pred_id)
    if not m2:
        return pred_id
    num = m2.group(1)

    # align lengths
    if len(num) != len(ref):
        return pred_id

    # correct digit-by-digit where they differ
    fixed_digits = []
    for a, b in zip(num, ref):
        if a != b:
            # prefer filename digit b
            fixed_digits.append(b)
        else:
            fixed_digits.append(a)

    return "".join(fixed_digits) + "_1"


def extract_id_from_lines(lines, base_name=None):
    """
    Extract ID in form '<digits>_1' from OCR lines.
    Use filename number as a hint when multiple candidates exist.

    Returns:
        best_id (str or None),
        conf   (float or None, in [0, 1])
    """
    # reference from filename
    ref_num = None
    if base_name is not None:
        m = re.search(r"(\d+)_1$", base_name)
        if m:
            ref_num = m.group(1)

    candidates = []   # list of (num_part, full_id)
    best_id = None
    best_score = None  # smaller is better

    for raw in lines:
        # normalize & keep only digits and underscore
        L = raw.replace("O", "0").replace("o", "0")
        L = L.replace("I", "1").replace("l", "1")
        L = L.replace(" ", "")
        L = re.sub(r"[^0-9_]", "", L)

        # direct matches like 10–25 digit ID + _1
        for match in re.finditer(r"(\d{10,25}_1)", L):
            cid = match.group(1)
            num = cid.split("_")[0]
            candidates.append((num, cid))

        # backup: if there's "_1" but digits broken
        if "_1" in L and not re.search(r"\d{10,25}_1", L):
            idx = L.index("_1")
            # go left and collect digits
            j = idx - 1
            digits = []
            while j >= 0 and L[j].isdigit():
                digits.append(L[j])
                j -= 1
            digits = "".join(reversed(digits))
            if len(digits) >= 10:
                cid = digits + "_1"
                candidates.append((digits, cid))

    if candidates:
        if ref_num is not None:
            # choose closest numeric part to filename number
            for num, cid in candidates:
                score = hamming_like(num, ref_num)
                if best_score is None or score < best_score:
                    best_score = score
                    best_id = cid
        else:
            # just take the longest candidate, no score
            best_num, best_id = max(candidates, key=lambda x: len(x[0]))
            best_score = None

    # last-resort: try to align digits to ref_num even if no '_1' seen
    if best_id is None and ref_num is not None:
        for raw in lines:
            L = raw.replace("O", "0").replace("o", "0")
            L = L.replace("I", "1").replace("l", "1")
            L = re.sub(r"[^0-9]", "", L)
            if len(L) < len(ref_num):
                continue
            for i in range(0, len(L) - len(ref_num) + 1):
                seg = L[i:i+len(ref_num)]
                score = hamming_like(seg, ref_num)
                if best_score is None or score < best_score:
                    best_score = score
                    best_id = seg + "_1"

    # map distance → confidence 0..1
    conf = None
    if ref_num is not None and best_score is not None:
        max_penalty = 2 * len(ref_num)  # worst-case distance approx
        conf = max(0.0, 1.0 - best_score / max_penalty)

    return best_id, conf
