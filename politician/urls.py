from django.urls import path
from . import views

urlpatterns = [
    path('list/<str:poly_nm>', views.politician_list),
]