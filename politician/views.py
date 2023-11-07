#from rest_framework.decorators import api_view
from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework.decorators import action, api_view
from .models import Community, Board
from .serializers import CommunitySerializer, BoardSerializer
from django.shortcuts import get_object_or_404, render, get_list_or_404
from rest_framework import status
from django.conf import settings
import requests, json

# Create your views here.

PERSONAL_DATA_API_KEY = settings.PERSONAL_DATA_API_KEY

@api_view(['GET'])
def politician_list(request, poly_nm):
    url = 'https://open.assembly.go.kr/portal/openapi/nwvrqwxyaytdsfvhu'
    params = {
        'KEY': PERSONAL_DATA_API_KEY,
        'Type': 'json',
        'pIndex': 1,
        'pSize': 100,
        'POLY_NM': poly_nm
    }
    response = requests.get(url, params=params)
    data = response.json()['nwvrqwxyaytdsfvhu'][1]
    
    result = []
    for i in range(params['pSize']):
        if poly_nm == data['row'][i]['POLY_NM']:
            result.append({'POLY_NM': data['row'][i]['POLY_NM'], 'HG_NM': data['row'][i]['HG_NM'], 'ENG_NM': data['row'][i]['ENG_NM'], 'ORIG_NM': data['row'][i]['ORIG_NM'], 'HOMEPAGE': data['row'][i]['HOMEPAGE']})
    
    return Response(result)



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

    @action(detail=False, methods=['GET'])
    def result(self, request):
        total_count = Board.objects.count()
        option1_count = Board.objects.filter(pick='option1').count()
        option2_count = Board.objects.filter(pick='option2').count()
        option3_count = Board.objects.filter(pick='option3').count()

        option1_percentage = (option1_count / total_count) * 100
        option2_percentage = (option2_count / total_count) * 100
        option3_percentage = (option3_count / total_count) * 100

        data = {
            'option1_count': option1_percentage,
            'option2_count': option2_percentage,
            'option3_count': option3_percentage,
        }

        return Response(data)



