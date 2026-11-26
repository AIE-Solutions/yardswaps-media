"""Blur only the text in a listing photo that can identify someone: phone numbers and licence plates.

Nov 26 2026: the old rule (just_listed.blur_digit_text) blurred every OCR word with a digit in it. On real
equipment photos tesseract reads trees, grilles, bumpers and mast chains as "4", "16" or "M4", so the Reels showed
blur boxes on the machine itself (2005 Peterbilt 379: three; a Toyota forklift: six), which reads as tampering.
A blur here is now kept for:
  - a phone number: a text line in a phone shape (915-555-1234, (915) 555-1234, 9155551234, 555-1234);
  - a plate, read with confidence 70+: one capital word of 6 to 8 letters and digits with 2+ of each
    (ABC1234), or two neighbouring words of 2-3 capital letters and 3-4 digits (ABC 1234).
Serial numbers, model numbers, hours and prices are not private and stay sharp. Faces are still handled by
just_listed.faces_in (the whole photo is skipped).

blur_private_text() keeps blur_digit_text()'s return shape: (image, boxes_blurred, ocr_ok).
"""
import re
import shutil

# 915-555-1234, (915) 555-1234, 915.555.1234, 9155551234, 555-1234: separators between the groups, so a
# model number next to an hour reading ("137562 4500 hrs") is not taken for a phone number.
PHONE_SHAPE = re.compile(r"\(\d{3}\)\s*\d{3}[\s.\-]+\d{4}|\b\d{3}[.\-]\d{3}[.\-]\d{4}\b|\b\d{3}\s\d{3}\s\d{4}\b"
                         r"|\b\d{10}\b|\b\d{3}[.\-]\d{4}\b")
PLATE_CONF = 70
WORD_CONF = 60


def _plate_like(word, conf):
    """One upper-case word of 6 to 8 letters and digits with at least 2 of each (ABC1234, 7ABC123)."""
    w = re.sub(r"[^A-Za-z0-9]", "", word)
    digits = sum(c.isdigit() for c in w)
    letters = sum(c.isalpha() for c in w)
    return conf >= PLATE_CONF and 6 <= len(w) <= 8 and digits >= 2 and letters >= 2 and w == w.upper()


def _plate_pair(w1, w2, conf):
    """Two neighbouring words read as one plate: 2-3 capital letters and 3-4 digits (ABC 1234, 123 ABC).
    "2016 JOHN", "DEERE 50G" and "4500 hrs" do not fit."""
    a, b = (re.sub(r"[^A-Za-z0-9]", "", w) for w in (w1, w2))
    letters_digits = lambda x, y: (x.isalpha() and x.isupper() and 2 <= len(x) <= 3
                                   and y.isdigit() and 3 <= len(y) <= 4)
    return conf >= PLATE_CONF and (letters_digits(a, b) or letters_digits(b, a))


def private_text_boxes(img_bgr):
    """[(x, y, w, h, why)] of phone numbers and plates in the photo, or None when OCR is not installed."""
    if not shutil.which("tesseract"):
        return None
    import cv2
    import pytesseract
    rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    d = pytesseract.image_to_data(rgb, output_type=pytesseract.Output.DICT, config="--psm 11")
    lines = {}
    boxes = []
    for i, word in enumerate(d["text"]):
        word = (word or "").strip()
        try:
            conf = float(d["conf"][i])
        except ValueError:
            conf = -1
        if not word or conf < 0:
            continue
        box = (d["left"][i], d["top"][i], d["width"][i], d["height"][i])
        lines.setdefault((d["block_num"][i], d["par_num"][i], d["line_num"][i]), []).append((word, conf, box))
        if _plate_like(word, conf):
            boxes.append((*box, f"plate {word}"))
    for words in lines.values():
        for (w1, c1, b1), (w2, c2, b2) in zip(words, words[1:]):
            if _plate_pair(w1, w2, min(c1, c2)):
                boxes += [(*b1, f"plate {w1} {w2}"), (*b2, f"plate {w1} {w2}")]
        sure = [(w, c, b) for w, c, b in words if c >= WORD_CONF]
        text = " ".join(w for w, c, b in sure)
        if PHONE_SHAPE.search(text):
            for w, c, b in sure:
                if any(ch.isdigit() for ch in w):
                    boxes.append((*b, f"phone {text}"))
    return boxes


def blur_private_text(img_bgr):
    """Blur phone numbers and plates only. Returns (image, boxes_blurred, ocr_ok)."""
    import cv2
    boxes = private_text_boxes(img_bgr)
    if boxes is None:
        return img_bgr, 0, False
    out = img_bgr.copy()
    for x, y, w, h, _ in boxes:
        pad = max(6, h // 2)
        x0, y0 = max(0, x - pad), max(0, y - pad)
        x1, y1 = min(out.shape[1], x + w + pad), min(out.shape[0], y + h + pad)
        roi = out[y0:y1, x0:x1]
        if roi.size:
            k = max(15, (max(roi.shape[:2]) // 2) * 2 + 1)
            out[y0:y1, x0:x1] = cv2.GaussianBlur(roi, (k, k), 0)
    return out, len(boxes), True


if __name__ == "__main__":  # python3 listings/photo_privacy.py photo.jpg ... : what would be blurred
    import sys
    import cv2
    for path in sys.argv[1:]:
        print(path, private_text_boxes(cv2.imread(path)))
