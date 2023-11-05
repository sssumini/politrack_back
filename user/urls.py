from django.urls import include, path
from .views import *

urlpatterns = [
    path("signin", UserRegisterView.as_view()),
    path("login/", UserLoginView.as_view()),
    path("logout/", UserLogoutView.as_view()),
    path("view/", UserDetailView.as_view()),
]