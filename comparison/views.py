from django.shortcuts import render
import requests
from django.core.files.storage import FileSystemStorage
from django.shortcuts import redirect
from PIL import Image
import numpy as np
import tensorflow as tf
import pytesseract
try:
    import cv2
    HAS_CV2 = True
except Exception:
    cv2 = None
    HAS_CV2 = False
import pytesseract

# Load MobileNet once globally
model = tf.keras.applications.mobilenet.MobileNet(weights="imagenet")


# ---------- IMAGE RECOGNITION ----------
def recognize_product(image_file):
    # -------------------------------
    # 1. ImageNet → E-commerce mapping
    # -------------------------------
    IMAGENET_TO_PRODUCT = {
        "notebook": "laptop",
        "laptop": "laptop",
        "computer keyboard": "keyboard",
        "mouse": "mouse",
        "cellular telephone": "mobile phone",
        "remote control": "mobile phone",
        "smartphone": "mobile phone",
        "headphone": "headphones",
        "earphone": "headphones",
        "running shoe": "shoes",
        "sneaker": "shoes",
        "coffee maker": "mixer grinder",
        "espresso maker": "mixer grinder",
        "blender": "mixer grinder",
        "television": "tv",
        "monitor": "monitor",
        "shirt": "shirt",
        "jeans": "jeans",
        "handbag": "bag",
        "backpack": "bag",
        "watch": "watch"
    }

    GENERIC_IGNORE = {
        "web site", "web page", "poster", "document",
        "screen", "screenshot", "book", "menu"
    }

    product_type = "product"

    # -------------------------------
    # 2. Product category detection
    # -------------------------------
    try:
        img = Image.open(image_file).convert("RGB").resize((224, 224))
        arr = np.array(img)
        arr = tf.keras.applications.mobilenet.preprocess_input(arr)
        arr = np.expand_dims(arr, axis=0)

        preds = model.predict(arr, verbose=0)
        decoded = tf.keras.applications.mobilenet.decode_predictions(preds, top=5)[0]

        for _, label, confidence in decoded:
            label = label.replace("_", " ").lower()
            if confidence > 0.50 and label not in GENERIC_IGNORE:
                product_type = IMAGENET_TO_PRODUCT.get(label, label)
                break

    except Exception as e:
        print("Classification error:", e)

    # -------------------------------
    # 3. OCR for brand detection
    # -------------------------------
    brand_name = ""

    KNOWN_BRANDS = {
        "nike", "adidas", "puma", "reebok", "skechers", "asics",
        "apple", "samsung", "oneplus", "xiaomi", "realme",
        "hp", "dell", "lenovo", "asus", "acer",
        "sony", "boat", "jbl", "noise",
        "zara", "levis", "h&m", "gucci", "prada"
    }

    STOPWORDS = {
        "made", "model", "design", "power", "size", "india",
        "new", "brand", "quality", "original"
    }

    try:
        img_pil = Image.open(image_file).convert("RGB")
        text = pytesseract.image_to_string(img_pil, config="--psm 6").lower()

        for brand in KNOWN_BRANDS:
            if brand in text:
                brand_name = brand
                break

        # Fallback: most frequent valid word
        if not brand_name:
            import re
            from collections import Counter

            words = re.findall(r"[a-z]{4,}", text)
            words = [w for w in words if w not in STOPWORDS]

            if words:
                brand_name = Counter(words).most_common(1)[0][0]

    except Exception as e:
        print("OCR error:", e)

    # -------------------------------
    # 4. Final clean search query
    # -------------------------------
    if brand_name and len(brand_name) > 2:
        search_query = f"{brand_name} {product_type}"
    else:
        search_query = product_type

    print(f"[RECOGNIZED] Brand: {brand_name}, Product: {product_type}")
    return search_query


# ---------- AMAZON API ----------
def amazon_search(query):
    query = query.lower().strip()
    url = "https://real-time-amazon-data.p.rapidapi.com/search"

    params = { 
        "query": query,
        "page": "1",
        "country": "IN"
    }

    headers = {
        "x-rapidapi-key": "b51872216bmshe7a5446be4e8a38p1df6cbjsn63058b1e4f09",
        "x-rapidapi-host": "real-time-amazon-data.p.rapidapi.com"
    }
    results = []

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        data = response.json()
        print("AMAZON RESPONSE:", data)

        products = data.get("data", {}).get("products", [])

        for item in products:
            try:
                # Extract price - try multiple fields
                price = (
                    item.get("product_price")
                    or item.get("product_minimum_offer_price")
                )
                
                # Extract image URL
                image = item.get("product_photo")
                
                # Extract product title
                title = item.get("product_title")
                
                # Extract product link
                link = item.get("product_url")
                
                # Only add if we have all required fields
                if price and image and title and link:
                    results.append({
                        "title": title,
                        "price": f"₹ {price}",
                        "image": image,
                        "link": link,
                        "source": "Amazon"
                    })
            except Exception as item_error:
                print(f"Error processing Amazon item: {item_error}")
                continue

        return results[:3]  # Return top 3 relevant results

    except requests.exceptions.Timeout:
        print("Amazon API Timeout Error")
        return []
    except requests.exceptions.ConnectionError:
        print("Amazon API Connection Error")
        return []
    except Exception as e:
        print("Amazon API Error:", e)
        return []

    
# ---------- WALMART API ----------
def flipkart_search(query):
    query = query.lower().strip()
    url = "https://rapidapi.com/datavio-datavio-default/api/flipkart-apis/playground"

    params = {
        "query": query,
        "page": "1",
        "sort": "relevance"
    }

    headers = {
        "x-rapidapi-key": "b51872216bmshe7a5446be4e8a38p1df6cbjsn63058b1e4f09",
        "x-rapidapi-host": "real-time-flipkart-data2.p.rapidapi.com"
    }

    results = []

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        print("WALMART RESPONSE:", data)

        items = data.get("items", [])

        for item in items:
            try:
                # Extract price - handle different formats
                price_data = item.get("price")
                if price_data is None:
                    continue
                    
                if isinstance(price_data, dict):
                    price = price_data.get("price") or price_data.get("current_price")
                else:
                    price = price_data
                
                # Extract image URL
                image = item.get("image")
                
                # Extract product title
                title = item.get("name") or item.get("product_title")
                
                # Extract product link
                link = item.get("canonicalUrl") or item.get("product_url") or item.get("url")
                
                # Only add if we have price, image, title, and link
                if price and image and title and link:
                    results.append({
                        "title": title,
                        "price": f"₹ {price}",
                        "image": image,
                        "link": link,
                        "source": "Walmart"
                    })
            except Exception as item_error:
                print(f"Error processing Walmart item: {item_error}")
                continue

        return results[:3]  # Return top 3 relevant results

    except requests.exceptions.Timeout:
        print("Walmart API Timeout Error")
        return []
    except requests.exceptions.ConnectionError:
        print("Walmart API Connection Error")
        return []
    except Exception as e:
        print("Walmart API Error:", e)
        return []


# ---------- UPLOAD PAGE ----------
def upload_page(request):
    return render(request, "upload.html")


# ---------- RESULT PAGE ----------
def result_page(request):
    if request.method == "POST":
        image = request.FILES["image"]
        fs = FileSystemStorage()
        filename = fs.save(image.name, image)
        image_url = fs.url(filename)

        search_query = recognize_product(image)

        amazon_results = amazon_search(search_query)
        flipkart_results = flipkart_search(search_query)
        PRODUCT_DETAILS = {
            "headphones": "True Wireless Stereo (TWS), Bluetooth, Built-in Mic, Fast Charging",
            "mobile phone": "Smartphone, Touchscreen, Camera, Internet Connectivity",
            "laptop": "Portable Computer, Keyboard, Display, Battery Powered",
            "shoes": "Comfortable Footwear, Casual & Sports Use",
            "watch": "Stylish Watch, Daily Wear, Durable Build"
        }

        product_type = search_query.split()[-1]
        description = PRODUCT_DETAILS.get(product_type, "High quality product with best features")


        return render(request, "results.html", {
            "product_name": search_query,
            "description": description,
            "amazon_results": amazon_results,
            "flipkart_results": flipkart_results,
            "image_url": image_url
        })

    return redirect("upload")