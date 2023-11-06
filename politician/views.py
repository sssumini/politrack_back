from django.shortcuts import get_object_or_404, get_list_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
import requests, json

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