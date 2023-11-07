from django.urls import path, include
from .views import *
from . import views
from rest_framework import routers
from django.conf import settings
from .views import CommunityViewSet, BoardViewSet

app_name="politician"

default_router = routers.SimpleRouter()
default_router.register("community", CommunityViewSet, basename="community")

board_router = routers.SimpleRouter()
board_router.register("board",BoardViewSet, basename="board")

urlpatterns = [
    path("", include(default_router.urls)),
    path('list/<str:poly_nm>', views.politician_list),
    path("community/<int:community_id>/", include(board_router.urls)),
]