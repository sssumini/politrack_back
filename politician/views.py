#from rest_framework.decorators import api_view
from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework.decorators import action
# Create your views here.
from .models import Community, Board
from .serializers import CommunitySerializer, BoardSerializer

from django.shortcuts import get_object_or_404, render

class CommunityViewSet(viewsets.ModelViewSet):
    queryset = Community.objects.all()
    serializer_class = CommunitySerializer

def create(self, request):
    serializer = self.get_serailizer(data=request.data)
    serializer.is_valid(raise_exception=True)
    self.perform_create(serializer)
    #community = serializer.instance

    return Response(serializer.data)

class BoardViewSet(viewsets.ModelViewSet):

    queryset = Board.objects.all()
    serializer_class = BoardSerializer

    @action(detail=True, methods=['get'])
    def get_community_fields(self, request, pk=None):
        # Board 인스턴스 가져오기
        board = self.get_object()
        community = board.community

        # Board 인스턴스의 Community 필드를 가져오기
        response_data = {
            'community_id': community.id,
            'board_id': board.id,
            'title': board.community.title,
            'content': board.community.content,
            'created_at': board.community.created_at,
            'deadline': board.community.deadline,
            'comment': board.comment
        }

        return Response(response_data)
