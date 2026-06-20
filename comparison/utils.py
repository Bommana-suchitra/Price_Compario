try:
    import tensorflow as tf
except Exception as e:
    tf = None
    print("TensorFlow import error (optional):", e)

import numpy as np
from PIL import Image
import pytesseract
import cv2
import re
import os


# ==================================================
# LOAD LIGHTWEIGHT MODEL (FALLBACK ONLY)
# Note: don't load at import time. Load lazily in fallback.
# ==================================================
mobilenet_model = None


# ==================================================
# CATEGORY KEYWORDS (COVERS MOST E-COMMERCE)
# ==================================================
CATEGORIES = {
    "wireless earpods": ["earpods", "earbuds", "airdopes", "earphones", "tws"],
    "mobile phone": ["mobile", "smartphone", "iphone", "android"],
    "laptop": ["laptop", "notebook", "macbook"],
    "headphones": ["earbuds", "earphones", "headset", "airdopes"],
    "television": ["television", "tv", "smart tv"],
    "camera": ["camera", "dslr"],
    "watch": ["watch", "smartwatch"],
    "shoes": ["shoes", "footwear", "sneakers"],
    "clothing": ["shirt", "tshirt", "t-shirt", "jeans", "dress"],
    "health supplement": ["moringa", "protein", "vitamin", "powder", "capsule"],
    "grocery": ["rice", "atta", "oil", "dal", "spices"],
    "home appliance": ["mixer", "grinder", "fan", "iron", "washing machine"],
    "kitchen appliance": ["blender", "toaster", "kettle"],
    "bag": ["bag", "backpack", "handbag"],
    "book": ["book", "novel", "author"],
}


# ==================================================
# IMAGE PREPROCESSING (OCR ACCURACY)
# ==================================================
def preprocess_image(image_path):
    img = cv2.imread(image_path)
    if img is None:
        return None

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, None, fx=1.3, fy=1.3, interpolation=cv2.INTER_CUBIC)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    return gray


# ==================================================
# OCR TEXT EXTRACTION
# ==================================================
def extract_text(image_path):
    try:
        processed = preprocess_image(image_path)
        if processed is None:
            print("[ERROR] Failed to preprocess image")
            return ""

        text = pytesseract.image_to_string(processed, config="--oem 3 --psm 6")
        text = re.sub(r"\s+", " ", text)
        print(f"[DEBUG] OCR success, extracted {len(text)} chars")
        return text.lower().strip()
    except Exception as e:
        print(f"[ERROR] OCR error: {type(e).__name__}: {e}")
        print(f"[HINT] Tesseract OCR may not be installed. Install with: sudo apt-get install tesseract-ocr")
        return ""





# ==================================================
# OCR-BASED CATEGORY DETECTION (PRIMARY)
# ==================================================
def detect_category_from_text(text):
    for category, keywords in CATEGORIES.items():
        for kw in keywords:
            if kw in text:
                return category
    return None


# ==================================================
# ML FALLBACK (ONLY IF OCR FAILS)
# ==================================================
def ml_fallback_category(image_path):
    try:
        if tf is None:
            # TensorFlow not available — skip ML fallback
            print("[INFO] TensorFlow not available, skipping ML fallback")
            return ("product", 0.0)

        global mobilenet_model
        if mobilenet_model is None:
            try:
                print("[DEBUG] Loading MobileNet model...")
                mobilenet_model = tf.keras.applications.MobileNet(weights="imagenet")
                print("[DEBUG] MobileNet loaded successfully")
            except Exception as e:
                print(f"[ERROR] Failed to load MobileNet: {e}")
                return "product"

        img = Image.open(image_path).convert("RGB").resize((224, 224))
        arr = np.array(img)
        arr = tf.keras.applications.mobilenet.preprocess_input(arr)
        arr = np.expand_dims(arr, axis=0)

        preds = mobilenet_model.predict(arr, verbose=0)
        decoded = tf.keras.applications.mobilenet.decode_predictions(preds, top=5)[0]

        # evaluate predictions: each decoded item is (class, label, prob)
        # return the first matching category and the model probability for that label
        for (cls, label, prob) in decoded:
            lab = label.replace("_", " ").lower()
            for category, keywords in CATEGORIES.items():
                if any(k in lab for k in keywords):
                    print(f"[DEBUG] ML matched category: {category} (label={lab}, prob={prob})")
                    return (category, float(prob))
    except Exception as e:
        print(f"[ERROR] ML fallback error: {type(e).__name__}: {e}")
    print("[INFO] No category matched, defaulting to 'product'")
    return ("product", 0.0)


# ==================================================
# MAIN IDENTIFICATION FUNCTION (FIXED)
# ==================================================
def identify_product(image_path):
    # 1️⃣ OCR FIRST
    ocr_text = extract_text(image_path)
    print(f"[DEBUG] OCR extracted text length: {len(ocr_text)}")
    print(f"[DEBUG] OCR text sample: {ocr_text[:100]}")
  #  ocr_text = clean_ocr_text(raw_text)

    # 2️⃣ OCR-BASED CATEGORY
    product_type = detect_category_from_text(ocr_text)
    method = None
    confidence = 0.0
    if product_type:
        method = "ocr"
        confidence = 0.95
        print(f"[DEBUG] Category detected from OCR: {product_type}")

    # 3️⃣ FALLBACKS
    if not product_type:
        filename_category = detect_category_from_text(os.path.basename(image_path).lower())
        if filename_category:
            product_type = filename_category
            method = "filename"
            confidence = 0.7
            print(f"[DEBUG] Category detected from filename: {product_type}")

    if not product_type:
        ml_cat, ml_conf = ml_fallback_category(image_path)
        product_type = ml_cat
        method = "ml"
        confidence = float(ml_conf or 0.0)
        print(f"[DEBUG] Category from ML fallback: {product_type} (confidence={confidence})")

    words = re.findall(r"[a-zA-Z0-9]{3,}", ocr_text)
    clean_text = " ".join(words[:6])
    # Prefer a short cleaned OCR snippet for search queries
    result = {
        "product_type": product_type,
        "ocr_text": clean_text if clean_text else ocr_text,
        "confidence": round(confidence, 2),
        "method": method or "unknown"
    }
    print(f"[DEBUG] Final product result: {result}")
    return result


# ==================================================
# SEARCH QUERY BUILDER 
# ==================================================
def build_search_query(product_type, ocr_text):
    if ocr_text:
        return f"{ocr_text} {product_type}"
    return product_type
