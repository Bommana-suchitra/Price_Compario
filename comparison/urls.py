from django.urls import path
from . import views

urlpatterns = [
    path("", views.upload_page, name="home"),
    path("upload/", views.upload_page, name="upload"),
    path("result/", views.result_page, name="result"),
]
