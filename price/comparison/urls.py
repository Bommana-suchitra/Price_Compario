from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
     path("", views.home, name="home"),

    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),  # ✅ ADD THIS

    path("upload/", views.upload_page, name="upload"),
    path("result/", views.result_page, name="result"),

    path("logout/", auth_views.LogoutView.as_view(next_page="home"), name="logout"),
]
 