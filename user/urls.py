from django.urls import include, path
from .views import *

from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

urlpatterns = [
    # path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('signin/', RegisterView.as_view(), name='auth_register'),
    path('login/', LoginView.as_view(), name='login'),
    path("logout/", LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]