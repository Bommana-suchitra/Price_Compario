# Price Compario

A Django-based price comparison web application that identifies a product from an uploaded image, builds a search query from OCR/text analysis, and compares prices from Amazon, eBay, and Google Shopping.

## Features

- User registration and login flow
- Upload product images for automated product identification
- OCR-based text extraction and category detection
- Price search using Amazon, eBay, and Google Shopping APIs
- Displays the best available price and comparison results
- Stores uploaded images using Django media storage

## Project Structure

- `comparison/` - Main Django app
  - `views.py` - Handles pages, uploads, and result rendering
  - `models.py` - Defines `ProductImage` model for uploaded images
  - `price_search.py` - Performs third-party price searches
  - `utils.py` - Image OCR, category detection, and query building
  - `urls.py` - App-level URL routes
  - `templates/` - HTML templates for pages
  - `static/` - CSS, JS, and image assets
- `price/` - Django project configuration
  - `settings.py` - Django settings and media configuration
  - `urls.py` - Root URL configuration
- `requirements.txt` - Python package dependencies
- `manage.py` - Django management utility

## Requirements

- Python 3.11+ (recommended)
- Django 5.x
- `djangorestframework`
- `Pillow`
- `requests`
- Tesseract OCR installed on the system
- Optional: TensorFlow for ML fallback category detection

## Setup

1. Clone the repository and change into the project folder:

```bash
cd Price_Compario-main
```

2. Create and activate a Python virtual environment:

```bash
python -m venv venv
venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Install Tesseract OCR on your system:

- Windows: install from https://github.com/tesseract-ocr/tesseract
- Linux: `sudo apt-get install tesseract-ocr`
- macOS: `brew install tesseract`

5. Apply migrations:

```bash
python manage.py migrate
```

6. Create a superuser (optional):

```bash
python manage.py createsuperuser
```

## Configuration

The application uses two external APIs for price search. Set the following environment variables before running the server:

- `RAPIDAPI_KEY` - API key for Amazon search
- `SERP_API_KEY` - API key for SerpApi (used for eBay and Google Shopping)

If environment variables are not set, the default keys embedded in `comparison/price_search.py` will be used, but it is strongly recommended to provide your own keys.

Example on Windows PowerShell:

```powershell
$env:RAPIDAPI_KEY = "your_rapidapi_key"
$env:SERP_API_KEY = "your_serp_api_key"
```

## Running the App

```bash
python manage.py runserver
```

Open your browser at `http://127.0.0.1:8000/`.

## Using the App

1. Register a new user or log in with an existing account.
2. Navigate to the upload page.
3. Upload a product image.
4. Review the search results and best price shown on the results page.

## Notes

- The app uses OCR via Tesseract to extract text from uploaded images. Image quality affects detection accuracy.
- If OCR fails to detect a product, the system will attempt simple filename matching and TensorFlow-based fallback category detection.
- The current search logic only returns the first result from each service and filters by detected price.
- Debug mode is enabled in `price/settings.py`, so this project is not ready for production deployment without additional hardening.

## Troubleshooting

- If OCR is not working, verify Tesseract is installed and available in your PATH.
- If API requests fail, check the API keys and service availability.
- If uploads do not appear, ensure `MEDIA_ROOT` is writable and Django is serving media files during development.

## License

This project includes a `LICENSE` file. Review that file for license details.

