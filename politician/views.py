#from rest_framework.decorators import api_view
from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework.decorators import action, api_view
from .models import Community, Board, Quiz, Opinion, OrigDetail
from .serializers import CommunitySerializer, BoardSerializer, QuizSerializer, OpinionSerializer
from django.shortcuts import get_object_or_404, render, get_list_or_404
from rest_framework import status
from django.conf import settings
import requests, json
import xmltodict

from wordcloud import WordCloud
from wordcloud import STOPWORDS
import matplotlib.pyplot as plt
from django.http import HttpResponse
import io, os, matplotlib, PIL

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.http import JsonResponse
from http import HTTPStatus

from konlpy.tag import Okt
from collections import Counter
import re

# Create your views here.

PERSONAL_DATA_API_KEY = settings.PERSONAL_DATA_API_KEY
# ELECTORS_NUMBER_API_KEY = settings.ELECTORS_NUMBER_API_KEY
PROFILE_IMAGE_API_KEY = settings.PROFILE_IMAGE_API_KEY

personal_data_url = 'https://open.assembly.go.kr/portal/openapi/nwvrqwxyaytdsfvhu'
# electors_number_url = 'http://apis.data.go.kr/9760000/ElcntInfoInqireService/getElpcElcntInfoInqire'
profile_image_url = 'http://apis.data.go.kr/9710000/NationalAssemblyInfoService/getMemberNameInfoList'
bill_data_url = 'https://open.assembly.go.kr/portal/openapi/nzmimeepazxkubdpn'

@api_view(['GET'])
def politician_list_by_poly(request, poly_nm):
    params = {
        'KEY': PERSONAL_DATA_API_KEY,
        'Type': 'json',
        'pIndex': 1,
        'pSize': 50,
        'POLY_NM': poly_nm,
        'ORIG_NM': '서울'
    }
    response = requests.get(personal_data_url, params=params)
    data = response.json()['nwvrqwxyaytdsfvhu'][1]
    
    result = []
    for i in range(len(data['row'])):
        result.append({'POLY_NM': data['row'][i]['POLY_NM'], 'HG_NM': data['row'][i]['HG_NM'], 
        'ENG_NM': data['row'][i]['ENG_NM'], 'ORIG_NM': data['row'][i]['ORIG_NM'], 'HOMEPAGE': data['row'][i]['HOMEPAGE'], 
        'MONA_CD': data['row'][i]['MONA_CD'], 'jpg_link': 'media/' + data['row'][i]['MONA_CD'] + '.jpg'})
    return Response(result)

@api_view(['GET'])
def politician_list_by_orig(request, orig_nm):
    # --- 선거구별 정치인 조회 API 사용 ---
    params = {
        'KEY': PERSONAL_DATA_API_KEY,
        'Type': 'json',
        'pIndex': 1,
        'pSize': 5,
        'ORIG_NM': orig_nm
    }
    response = requests.get(personal_data_url, params=params)
    data = response.json()['nwvrqwxyaytdsfvhu'][1]

    result = []
    try:
        orig_detail = OrigDetail.objects.get(orig_nm=orig_nm)
        # 선거구별 투표구수, 선거인수 return
        result.append({'tpgCount': orig_detail.tpgCount, 'cfmtnElcnt': orig_detail.cfmtnElcnt})
    except OrigDetail.DoesNotExist:
        pass

    count = 0
    for i in range(len(data['row'])):
        result.append({'POLY_NM': data['row'][i]['POLY_NM'], 'HG_NM': data['row'][i]['HG_NM'], 
        'ENG_NM': data['row'][i]['ENG_NM'], 'ORIG_NM': data['row'][i]['ORIG_NM'], 'HOMEPAGE': data['row'][i]['HOMEPAGE'], 
        'MONA_CD': data['row'][i]['MONA_CD'], 'jpg_link': 'media/' + data['row'][i]['MONA_CD'] + '.jpg'})
        if data['row'][i]['POLY_NM'] == '더불어민주당':
            count += 1
        elif data['row'][i]['POLY_NM'] == '국민의힘':
            count -= 1
    
    if count == len(data['row']):
        result.append({'vict_poly': 1}) # 더불어민주당 승리구일 경우
    elif count == -len(data['row']):
        result.append({'vict_poly': 2}) # 국민의힘 승리구일 경우
    else:
        result.append({'vict_poly': 3}) # 두 정당이 섞여 있는 구일 경우
    
    return Response(result)

@api_view(['GET'])
def politician_list_by_hgnm(request, hg_nm):
    params = {
        'KEY': PERSONAL_DATA_API_KEY,
        'Type': 'json',
        'pIndex': 1,
        'pSize': 5,
        'HG_NM': hg_nm,
        'ORIG_NM': '서울'
    }
    response = requests.get(personal_data_url, params=params)
    data = response.json()['nwvrqwxyaytdsfvhu'][1]
    
    result = []
    for i in range(len(data['row'])):
        result.append({'POLY_NM': data['row'][i]['POLY_NM'], 'HG_NM': data['row'][i]['HG_NM'], 
        'ENG_NM': data['row'][i]['ENG_NM'], 'ORIG_NM': data['row'][i]['ORIG_NM'], 'HOMEPAGE': data['row'][i]['HOMEPAGE'], 
        'MONA_CD': data['row'][i]['MONA_CD'], 'jpg_link': 'media/' + data['row'][i]['MONA_CD'] + '.jpg'})
    
    return Response(result)

@api_view(['GET'])
def politician_list_by_mona(request, mona_cd):
    params = {
        'KEY': PERSONAL_DATA_API_KEY,
        'Type': 'json',
        'pIndex': 1,
        'pSize': 100,
        'MONA_CD': mona_cd
    }
    response = requests.get(personal_data_url, params=params)
    data = response.json()['nwvrqwxyaytdsfvhu'][1]
    
    result = []
    for i in range(len(data['row'])):
        # 국회의원별 발의법률안
        params = {
            'KEY': PERSONAL_DATA_API_KEY,
            'Type': 'json',
            'pIndex': 1,
            'pSize': 100,
            'AGE': '21',
            'PROPOSER': data['row'][i]['HG_NM']
        }
        response = requests.get(bill_data_url, params=params)
        bill_data = response.json()['nzmimeepazxkubdpn'][1]
        result.append({'POLY_NM': data['row'][i]['POLY_NM'], 'HG_NM': data['row'][i]['HG_NM'], 
                       'ENG_NM': data['row'][i]['ENG_NM'], 'ORIG_NM': data['row'][i]['ORIG_NM'], 
                       'HOMEPAGE': data['row'][i]['HOMEPAGE'], 'MONA_CD': data['row'][i]['MONA_CD'], 
                       'UNITS': data['row'][i]['UNITS'], 'CMITS': data['row'][i]['CMITS'], 
                       'MEM_TITLE': data['row'][i]['MEM_TITLE'], 'jpg_link': 'media/' + data['row'][i]['MONA_CD'] + '.jpg'})
        for j in range(len(bill_data['row'])):
            result.append({'BILL_NAME': bill_data['row'][j]['BILL_NAME'], 'DETAIL_LINK': bill_data['row'][j]['DETAIL_LINK']})
    return Response(result)

class CommunityViewSet(viewsets.ModelViewSet):
    queryset = Community.objects.all()
    serializer_class = CommunitySerializer

    def list(self, request, *args, **kwargs):
        category = request.query_params.get('category')
        
        if category:
            communities = self.queryset.filter(category=category)
        else:
            communities = self.queryset.all()
        
        serializer = self.get_serializer(communities, many=True)
        return Response(serializer.data)


def create(self, request):
    serializer = self.get_serailizer(data=request.data)
    serializer.is_valid(raise_exception=True)
    self.perform_create(serializer)
    #community = serializer.instance

    return Response(serializer.data)



class BoardViewSet(viewsets.ModelViewSet):

    queryset = Board.objects.all()
    serializer_class = BoardSerializer



class CommunityBoardViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer

    @action(detail=False, methods=['GET'])
    def result(self, request, community_id=None):
        total_count = Board.objects.filter(community_id=community_id).count()
        option1_count = Board.objects.filter(community_id=community_id, pick='option1').count()
        option2_count = Board.objects.filter(community_id=community_id,pick='option2').count()
        option3_count = Board.objects.filter(community_id=community_id,pick='option3').count()
        
        pick_title = Board.objects.filter(community_id=community_id).values('pick_title').first()

        option1_percentage = round((option1_count / total_count) * 100,1)
        option2_percentage = round((option2_count / total_count) * 100,1)
        option3_percentage = round((option3_count / total_count) * 100,1)
        
        data = {
            'option1_count': option1_percentage,
            'option2_count': option2_percentage,
            'option3_count': option3_percentage,
            'pick_title': pick_title['pick_title'] if pick_title else None,
        }

        return Response(data)

    def list(self, request, community_id=None):
        community_id = get_object_or_404(Community, community_id=community_id)
        queryset = self.filter_queryset(self.get_queryset().filter(community_id=community_id))
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def create(self, request, community_id=None):
        community_id = get_object_or_404(Community, community_id=community_id)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(community_id=community_id)
        return Response(serializer.data)
    
    

class OpinionViewSet(viewsets.ModelViewSet):
    queryset = Opinion.objects.all()
    serializer_class = OpinionSerializer

def apply_regular_expression(text):
    hangul = re.compile('[^ ㄱ-ㅣ 가-힣]')
    result = hangul.sub('', text) # 불필요한 .^ 등의 표현 제거
    return result
      
def generate_wordcloud_good(request, community_id, pick_value='option1'):
    community_id = Community.objects.get(pk=community_id)
    comment_messages = Board.objects.filter(community_id=community_id, pick=pick_value)
    
    word_frequencies = {} 
    # Create a WordCloud object
    excluded_words = ['ㅅㅂ', '시발' ,'존나', '개']  

    for message in comment_messages:
        # words = message.comment.split()  # 공백을 기준으로 단어 분리
        okt = Okt()  # 명사 형태소 추출 함수
        words = okt.nouns(apply_regular_expression(message.comment))
        for word in words:
            if word not in excluded_words:
                if word in word_frequencies:
                    word_frequencies[word] += 1
                else:
                    word_frequencies[word] = 1

    project_root = os.path.dirname(os.path.abspath(__file__))
    font_path = os.path.join(project_root, 'NotoSansKR-SemiBold.ttf')
    wordcloud = WordCloud(
        width=400, height=400, 
        max_font_size=150, 
        background_color='white', 
        font_path=font_path, 
        prefer_horizontal = False,
        collocations=False, 
        colormap='binary'
    ).generate_from_frequencies(word_frequencies)

    wordcloud_folder = os.path.join(settings.MEDIA_ROOT, 'wordcloud')
    os.makedirs(wordcloud_folder, exist_ok=True)

    image_file_path = os.path.join(wordcloud_folder, f'wordcloud_good{community_id}.png')
    wordcloud.to_file(image_file_path)

    community_id.wordcloud_image_path = f'wordcloud/wordcloud_good{community_id}.png'
    community_id.save()

    buf = io.BytesIO()
    plt.figure(figsize=(6, 6))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.tight_layout(pad=0)
    plt.savefig(buf, format='png')
    buf.seek(0)

    return HttpResponse(buf.getvalue(), content_type='image/png')




def generate_wordcloud_soso(request, community_id, pick_value='option2'):
    community_id = Community.objects.get(pk=community_id)
    comment_messages = Board.objects.filter(community_id=community_id, pick=pick_value)
    
    word_frequencies = {} 
    # Create a WordCloud object
    excluded_words = ['ㅅㅂ', '시발' ,'존나', '개']  

    for message in comment_messages:
        # words = message.comment.split()  # 공백을 기준으로 단어 분리
        okt = Okt()  # 명사 형태소 추출 함수
        words = okt.nouns(apply_regular_expression(message.comment))
        for word in words:
            if word not in excluded_words:
                if word in word_frequencies:
                    word_frequencies[word] += 1
                else:
                    word_frequencies[word] = 1
    project_root = os.path.dirname(os.path.abspath(__file__))
    font_path = os.path.join(project_root, 'NotoSansKR-SemiBold.ttf')
    wordcloud = WordCloud(
        width=400, height=400, 
        max_font_size=150, 
        background_color='white', 
        font_path=font_path, 
        prefer_horizontal = False,
        collocations=False, 
        colormap='binary'
    ).generate_from_frequencies(word_frequencies)

    wordcloud_folder = os.path.join(settings.MEDIA_ROOT, 'wordcloud')
    os.makedirs(wordcloud_folder, exist_ok=True)


    image_file_path = os.path.join(wordcloud_folder, f'wordcloud_soso{community_id}.png')
    wordcloud.to_file(image_file_path)

    community_id.wordcloud_image_path = f'wordcloud/wordcloud_soso{community_id}.png'
    community_id.save()
    buf = io.BytesIO()
    plt.figure(figsize=(6, 6))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.tight_layout(pad=0)
    plt.savefig(buf, format='png')
    buf.seek(0)

    return HttpResponse(buf.getvalue(), content_type='image/png')






def generate_wordcloud_bad(request, community_id, pick_value='option3'):
    community_id = Community.objects.get(pk=community_id)
    comment_messages = Board.objects.filter(community_id=community_id, pick=pick_value)
    
    word_frequencies = {} 
    # Create a WordCloud object
    excluded_words = ['ㅅㅂ', '시발' ,'존나', '개']  

    for message in comment_messages:
        # words = message.comment.split()  # 공백을 기준으로 단어 분리
        okt = Okt()  # 명사 형태소 추출 함수
        words = okt.nouns(apply_regular_expression(message.comment))
        for word in words:
            if word not in excluded_words:
                if word in word_frequencies:
                    word_frequencies[word] += 1
                else:
                    word_frequencies[word] = 1
    project_root = os.path.dirname(os.path.abspath(__file__))
    font_path = os.path.join(project_root, 'NotoSansKR-SemiBold.ttf')
    wordcloud = WordCloud(
        width=400, height=400, 
        max_font_size=150, 
        background_color='white', 
        font_path=font_path, 
        prefer_horizontal = False,
        collocations=False, 
        colormap='binary'
    ).generate_from_frequencies(word_frequencies)

    wordcloud_folder = os.path.join(settings.MEDIA_ROOT, 'wordcloud')
    os.makedirs(wordcloud_folder, exist_ok=True)


    image_file_path = os.path.join(wordcloud_folder, f'wordcloud_bad{community_id}.png')
    wordcloud.to_file(image_file_path)

    community_id.wordcloud_image_path = f'wordcloud/wordcloud_bad{community_id}.png'
    community_id.save()
    buf = io.BytesIO()
    plt.figure(figsize=(6, 6))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.tight_layout(pad=0)
    plt.savefig(buf, format='png')
    buf.seek(0)

    return HttpResponse(buf.getvalue(), content_type='image/png')



class QuizViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer