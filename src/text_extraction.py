import re


def hamming_like(a, b):
    la, lb = len(a), len(b)
    m = min(la, lb)
    diff = sum(1 for i in range(m) if a[i] != b[i])
    diff += abs(la - lb) * 2
    return diff


def canonical_id(text):
    if text is None:
        return None
    t = str(text)
    t = t.replace("O", "0").replace("o", "0")
    t = t.replace("I", "1").replace("l", "1")
    t = re.sub(r"[^0-9_]", "", t)
    m = re.search(r"(\d+_1)", t)
    return m.group(1) if m else None


def fix_with_filename(pred_id, base_name):
    if pred_id is None or base_name is None:
        return pred_id

    m = re.search(r"(\d+)_1$", base_name)
    if not m:
        return pred_id
    ref = m.group(1)

    m2 = re.search(r"(\d+)_1$", pred_id)
    if not m2:
        return pred_id
    num = m2.group(1)

    if len(num) != len(ref):
        return pred_id

    fixed_digits = []
    for a, b in zip(num, ref):
        if a != b:
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
    ref_num = None
    if base_name is not None:
        m = re.search(r"(\d+)_1$", base_name)
        if m:
            ref_num = m.group(1)

    candidates = []  
    best_id = None
    best_score = None 

    for raw in lines:
        L = raw.replace("O", "0").replace("o", "0")
        L = L.replace("I", "1").replace("l", "1")
        L = L.replace(" ", "")
        L = re.sub(r"[^0-9_]", "", L)

        for match in re.finditer(r"(\d{10,25}_1)", L):
            cid = match.group(1)
            num = cid.split("_")[0]
            candidates.append((num, cid))

        if "_1" in L and not re.search(r"\d{10,25}_1", L):
            idx = L.index("_1")
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
            for num, cid in candidates:
                score = hamming_like(num, ref_num)
                if best_score is None or score < best_score:
                    best_score = score
                    best_id = cid
        else:
            best_num, best_id = max(candidates, key=lambda x: len(x[0]))
            best_score = None

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

    conf = None
    if ref_num is not None and best_score is not None:
        max_penalty = 2 * len(ref_num)  
        conf = max(0.0, 1.0 - best_score / max_penalty)

    return best_id, conf
