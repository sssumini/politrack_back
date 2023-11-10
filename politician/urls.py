from django.urls import path, include
from .views import *
from . import views
from rest_framework import routers
from django.conf import settings
from .views import CommunityViewSet, BoardViewSet, CommunityBoardViewSet

app_name="politician"

community_router = routers.SimpleRouter()
community_router.register("community", CommunityViewSet, basename="community")

quiz_router = routers.SimpleRouter()
quiz_router.register("quiz", QuizViewSet, basename="quiz")

board_router = routers.SimpleRouter()
board_router.register("communitydetail",BoardViewSet, basename="communitydetail")

community_board_router = routers.SimpleRouter()
community_board_router.register("detail",CommunityBoardViewSet, basename="detail")


opinion_router = routers.SimpleRouter()
opinion_router.register("opinion",OpinionViewSet, basename="opinion")


urlpatterns = [
    path("", include(community_router.urls)),
    path("", include(board_router.urls)),
    path("", include(opinion_router.urls)),
    path("", include(quiz_router.urls)),
    path('poly/<str:poly_nm>', views.politician_list_by_poly),
    path('orig/<str:orig_nm>', views.politician_list_by_orig),
    path('name/<str:hg_nm>', views.politician_list_by_hgnm),
    path('id/<str:mona_cd>', views.politician_list_by_mona),
    path("community/<int:community_id>/", include(community_board_router.urls)),
    path('community/<int:community_id>/wordcloud', views.generate_wordcloud, name='generate_wordcloud'),
]