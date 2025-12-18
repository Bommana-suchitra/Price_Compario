from django.shortcuts import render
#from django.http import JsonResponse
import requests
from django.core.files.storage import FileSystemStorage
from django.shortcuts import redirect
from PIL import Image
import numpy as np
import tensorflow as tf

# Load MobileNet once globally
model = tf.keras.applications.mobilenet.MobileNet(weights="imagenet")


# ---------- IMAGE RECOGNITION ----------
def recognize_product(image_file):
    img = Image.open(image_file).convert("RGB").resize((224, 224))
    img = np.array(img) 
    img = tf.keras.applications.mobilenet.preprocess_input(img)
    img = np.expand_dims(img, axis=0)

    preds = model.predict(img)
    decoded = tf.keras.applications.mobilenet.decode_predictions(preds, top=5)

    keywords = []
    for _, label, confidence in decoded[0]:
        if confidence > 0.15:
            keywords.append(label.replace("_", " ").lower())

    # fallback safety
    if not keywords:
        return "product"

    # return 1–2 keywords for better search
    return " ".join(keywords[:2])


# ---------- AMAZON API ----------
def amazon_search(query):
    query = query.lower().strip()
    url = "https://real-time-amazon-data.p.rapidapi.com/search"



    params = { "query": query,
        "page": "1",
        "country": "IN"
    }

    headers = {
        "x-rapidapi-key": "b51872216bmshe7a5446be4e8a38p1df6cbjsn63058b1e4f09",
       "x-rapidapi-host": "real-time-amazon-data.p.rapidapi.com"
    }
    results = []

    try:
        response = requests.get(url, headers=headers, params=params,timeout=10)
        data = response.json()
        print("AMAZON RESPONSE:", data)

        products = data.get("data", {}).get("products", [])

        for item in products:
             price_data = item.get("price", {})
             price = (
                price_data.get("current_price")
                or price_data.get("value")
                or price_data.get("amount")
                or price_data.get("raw")
            )
             results.append({
                 "title": item.get("product_title"),
                 "price": f"₹ {price}" ,
                 "image": item.get("product_photo"),
                 "link": item.get("product_url"),
                 "source": "Amazon"
})

        return results[:6]

    except Exception as e:
        print("Amazon API Error:", e)
        return []
    
# ---------- WALMART API ----------
def walmart_search(query):
    query = query.lower().strip()
    url = "https://realtime-walmart-data.p.rapidapi.com/search"

    params = {
        "query": query,
        "page": "1",
        "sort": "relevance"
    }

    headers = {
        "x-rapidapi-key": "b51872216bmshe7a5446be4e8a38p1df6cbjsn63058b1e4f09",
        "x-rapidapi-host": "realtime-walmart-data.p.rapidapi.com"
    }

    results = []

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        print("WALMART RESPONSE:", data)

        items = data.get("items", [])

        for item in items:
            price_data = item.get("price")
            price = price_data.get("price") if isinstance(price_data, dict) else price_data

            results.append({
                "title": item.get("name", "Unknown product"),
                "price": f"₹ {price}" if price else "Price not available",
                "image": item.get("image"),
                "link": item.get("canonicalUrl"),
                "source": "Walmart"
            })

        return results[:6]

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

        # Detect product name
        detected_name = recognize_product(image)
        search_query = detected_name.replace("_", " ")

        # Search Amazon
        amazon_results = amazon_search(search_query)
        walmart_results = walmart_search(search_query)

       # print("AMAZON RESULTS:", amazon_results) 
        return render(request, "results.html", {
            "product_name": detected_name,
            "amazon_results": amazon_results,
            "walmart_results": walmart_results,
            "image_url": image_url
        })



    return redirect("upload")