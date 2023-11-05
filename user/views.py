from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import User
from .serializers import *
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.renderers import JSONRenderer
import jwt, datetime
from datetime import datetime, timedelta, timezone

# 회원가입
class UserRegisterView(APIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    def post(self, req):
        serializer = UserRegisterSerializer(data=req.data)
        
        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# 로그인
class UserLoginView(APIView):
    queryset = User.objects.all()
    serializer_class = UserLoginSerializer
    def post(self,req):
        serializer = UserLoginSerializer(data=req.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user_id']

        if user is None :
            raise AuthenticationFailed('User does not found!')
        
        current_time = datetime.now(timezone.utc)
        expiration_time = current_time + timedelta(minutes=60)

        ## JWT 구현 부분
        payload = {
            'id' : user,
            'exp' : expiration_time,
            'iat' : current_time
        }

        token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256") # .decode("utf-8")

        res = Response()
        res.set_cookie(key='jwt', value=token, httponly=True)
        res.data = {
            'jwt' : token
        }
        return res
    
# 로그아웃
class UserLogoutView(APIView):
    # permission_classes = [IsAuthenticated]
    def post(self,req):
        token = req.COOKIES.get('jwt')

        if not token :
            raise AuthenticationFailed('UnAuthenticated!')

        try :
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])

        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('UnAuthenticated!')

        res = Response()
        res.delete_cookie('jwt')
        res.data = {
            "message" : 'success'
        }
        return res
    
class UserDetailView(APIView):
    # permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = UserDetailSerializer

    def get(self,req):
        token = req.COOKIES.get('jwt')

        if not token :
            raise AuthenticationFailed('UnAuthenticated!')

        try :
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])

        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('UnAuthenticated!')

        user = User.objects.get(user_id=payload['id'])
        
        serializer = UserDetailSerializer(user)

        return Response(serializer.data)