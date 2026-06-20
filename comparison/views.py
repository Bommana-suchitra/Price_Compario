from django.shortcuts import render,redirect
from django.core.files.storage import FileSystemStorage
from urllib.parse import quote_plus
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ProductImage
from .utils import identify_product, build_search_query
from . import price_search
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
@login_required(login_url='login')
def upload_page(request):
     if request.method == "POST":
        return result_page(request) 
     return render(request, "upload.html")


def home(request):
    return render(request, "home.html")
def login_view(request):
     if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST["username"],
            password=request.POST["password"]
        )
        if user:
            login(request, user)
            return redirect("upload")
        else:
            messages.error(request, "Invalid username or password")

     return render(request, "login.html")


def register_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        confirm = request.POST["confirm_password"]

        if password != confirm:
            messages.error(request, "Passwords do not match")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
        else:
            User.objects.create_user(username=username, password=password)
            messages.success(request, "Account created successfully. Please login.")
            return redirect("login")

    return render(request, "register.html")


@login_required(login_url='login')

def result_page(request):
    product = {}
    query = ""
    results = []
    best = None
    image_url = None

    if request.method == "POST" and request.FILES.get("image"):
        image = request.FILES["image"]
        fs = FileSystemStorage()
        filename = fs.save(image.name, image)
        image_url = fs.url(filename)

        product_image = ProductImage.objects.create(image=filename)
        image_path = product_image.image.path

        product = identify_product(image_path)

        query = build_search_query(
            product.get("product_type", "product"),
            product.get("ocr_text", "")
        )

        DEFAULT_BRANDS = {
            "laptop": "dell laptop",
            "mobile phone": "samsung mobile",
            "headphones": "boat earbuds",
            "watch": "smart watch",
            "shoes": "nike shoes",
            "television": "smart tv",
        }

        if len(query.split()) < 2:
            query = DEFAULT_BRANDS.get(product.get("product_type"), query)

        price_search.API_ERRORS.clear()

        # SEARCH
        amazon = price_search.amazon_search(query)
        ebay = price_search.ebay_search(query)
        google = price_search.google_search(query)

        print("Amazon:", len(amazon))
        print("eBay:", len(ebay))
        print("Google:", len(google))
        print("Errors:", price_search.API_ERRORS)

        results = amazon + ebay + google
        results = [r for r in results if r.get("price")]
        results.sort(key=lambda x: x["price"])

        if results:
            best = results[0]

        # Precompute star ratings
        for r in results:
            rating = r.get("rating")
            if rating:
                filled = int(float(rating))
                empty = 5 - filled
                r["stars"] = ["★"] * filled + ["☆"] * empty
            else:
                r["stars"] = []

    search_links = {
        "amazon": f"https://www.amazon.in/s?k={quote_plus(query)}",
        "ebay": f"https://www.ebay.in/sch/i.html?_nkw={quote_plus(query)}",
        "google": f"https://www.google.com/search?q={quote_plus(query)}"
    }

    failed_services = []
    for e in price_search.API_ERRORS:
        if "amazon" in e.lower():
            failed_services.append("Amazon")
        if "ebay" in e.lower():
            failed_services.append("eBay")
        if "google" in e.lower():
            failed_services.append("Google")

    return render(request, "results.html", {
        "image_url": image_url,
        "product": product,
        "query": query,
        "results": results,
        "best": best,
        "api_problem": bool(price_search.API_ERRORS),
        "failed_services": list(set(failed_services)),
        "search_links": search_links,
    })
