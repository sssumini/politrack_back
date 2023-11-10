#from rest_framework.decorators import api_view
from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework.decorators import action, api_view
from .models import Community, Board, Quiz, Opinion
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
        'pSize': 10, # 다시 100으로 수정하면 jpg_link 가져오는데 에러 뜸 # 10개가 최대인 듯
        'POLY_NM': poly_nm
    }
    response = requests.get(personal_data_url, params=params)
    data = response.json()['nwvrqwxyaytdsfvhu'][1]
    
    result = []
    for i in range(len(data['row'])):
        params = { # 불러온 데이터에 한해서 이름이 동일한 정치인별 프로필 이미지 가져오기
            'serviceKey': PROFILE_IMAGE_API_KEY,
            'numOfRows': 10,
            'pageNo': 1,
            'hgnm': data['row'][i]['HG_NM'] # '홍익표'
        }
        response = requests.get(profile_image_url, params=params)
        data_dict = {}
        data_dict = xmltodict.parse(response.content)

        # Convert dictionary to JSON
        json_result = json.dumps(data_dict, indent=2, ensure_ascii=False)

        # print(json_result)
        jpg_link = data_dict['response']['body']['items']['item']['jpgLink']
        
        save_image(jpg_link, data['row'][i]['MONA_CD'])

        result.append({'POLY_NM': data['row'][i]['POLY_NM'], 'HG_NM': data['row'][i]['HG_NM'], 'ENG_NM': data['row'][i]['ENG_NM'], 'ORIG_NM': data['row'][i]['ORIG_NM'], 'HOMEPAGE': data['row'][i]['HOMEPAGE'], 'MONA_CD': data['row'][i]['MONA_CD'], 'jpg_link': 'media/' + data['row'][i]['MONA_CD'] + '.jpg'})
    return Response(result)

@api_view(['GET'])
def politician_list_by_orig(request, orig_nm):
    # --- 투표구 수 및 선거인수 조회 관련 API 사용 ---
    # 값이 강서구 데이터밖에 없는 것 같음
    # params = {
    #     'serviceKey': ELECTORS_NUMBER_API_KEY,
    #     'pageNo': '1',
    #     'numOfRows': '5',
    #     'resultType': 'json',
    #     'sgId': '20231011',
    #     'sgTypecode': '4',
    #     'sdName': '서울특별시',
    #     'wiwName': '강동구'
    # }
    # params ={'serviceKey' : ELECTORS_NUMBER_API_KEY, 'pageNo' : '1', 'numOfRows' : '10', 'resultType' : 'json', 'sgId' : '20231011', 'sgTypecode' : '4', 'sdName' : '서울특별시', 'wiwName' : '강동구' }
    # response = requests.get(electors_number_url, params=params)
    # response = json.loads(response)
    # data = response.json() # 계속해서 JSONDecodeError 발생
    # return Response(response)
    
    # --- 선거구별 정치인 조회 API 사용 ---
    params = {
        'KEY': PERSONAL_DATA_API_KEY,
        'Type': 'json',
        'pIndex': 1,
        'pSize': 100,
        'ORIG_NM': orig_nm
    }
    response = requests.get(personal_data_url, params=params)
    data = response.json()['nwvrqwxyaytdsfvhu'][1]
    
    result = []
    count = 0
    for i in range(len(data['row'])):
        result.append({'POLY_NM': data['row'][i]['POLY_NM'], 'HG_NM': data['row'][i]['HG_NM'], 'ENG_NM': data['row'][i]['ENG_NM'], 'ORIG_NM': data['row'][i]['ORIG_NM'], 'HOMEPAGE': data['row'][i]['HOMEPAGE'], 'MONA_CD': data['row'][i]['MONA_CD']})
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
        'pSize': 100,
        'HG_NM': hg_nm
    }
    response = requests.get(personal_data_url, params=params)
    data = response.json()['nwvrqwxyaytdsfvhu'][1]
    
    result = []
    for i in range(len(data['row'])):
        result.append({'POLY_NM': data['row'][i]['POLY_NM'], 'HG_NM': data['row'][i]['HG_NM'], 'ENG_NM': data['row'][i]['ENG_NM'], 'ORIG_NM': data['row'][i]['ORIG_NM'], 'HOMEPAGE': data['row'][i]['HOMEPAGE'], 'MONA_CD': data['row'][i]['MONA_CD']})
    
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
                       'MEM_TITLE': data['row'][i]['MEM_TITLE']})
        for j in range(len(bill_data['row'])):
            result.append({'BILL_NAME': bill_data['row'][j]['BILL_NAME'], 'DETAIL_LINK': bill_data['row'][j]['DETAIL_LINK']})
    return Response(result)

def save_image(image_url, mona_cd):
    image_url = image_url
    
    filename = default_storage.get_available_name(mona_cd + ".jpg")
    
    # Check if the file already exists
    if default_storage.exists(filename):
        # File already exists, use the existing file
        media_url = default_storage.url(filename)
        # return JsonResponse({"media_url": media_url})
    
    response = requests.get(image_url)
    
    if response.status_code == 200:
        with default_storage.open(filename, "wb") as f:
            f.write(response.content)
        
        media_url = default_storage.url(filename)


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



class CommunityBoardViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer

    def list(self, request, community_id=None):
        community = get_object_or_404(Community, community_id=community_id)
        queryset = self.filter_queryset(self.get_queryset().filter(community=community))
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def create(self, request, community_id=None):
        community = get_object_or_404(Community, community_id=community_id)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(community=community)
        return Response(serializer.data)
    
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
    

class OpinionViewSet(viewsets.ModelViewSet):
    queryset = Opinion.objects.all()
    serializer_class = OpinionSerializer


class CommunityBoardViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer

    def list(self, request, community_id=None):
        community = get_object_or_404(Community, community_id=community_id)
        queryset = self.filter_queryset(self.get_queryset().filter(community=community))
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def create(self, request, community_id=None):
        community = get_object_or_404(Community, id=community_id)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(community=community)
        return Response(serializer.data)


      
def generate_wordcloud(request, community_id):
    community = Community.objects.get(pk=community_id)
    comment_messages = Opinion.objects.filter(community=community)
    
    word_frequencies = {} 
    # Create a WordCloud object
    excluded_words = ['ㅅㅂ', '시발' ,'존나', '개']  

    for message in comment_messages:
        words = message.comment.split()  # 공백을 기준으로 단어 분리
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
        max_font_size=200, 
        background_color='white', 
        font_path=font_path, 
        prefer_horizontal = False,
        collocations=False, 
        colormap='binary'
    ).generate_from_frequencies(word_frequencies)

    image_file_path = os.path.join(settings.MEDIA_ROOT, f'wordcloud_{community_id}.png')
    wordcloud.to_file(image_file_path)

    community.wordcloud_image_path = f'wordcloud_{community_id}.png'
    community.save()

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

