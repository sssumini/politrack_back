from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import AllowAny, IsAuthenticated
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

from django.shortcuts import render
from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics

# 회원가입
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer
    
class LoginView(APIView):
    permission_classes = [ AllowAny ]

    def post(self, request):
        user = authenticate(
            user_id = request.data.get("user_id"),
            password = request.data.get("password"),
        )
        if user:
            login_serializer = UserLoginSerializer(user)
            token = TokenObtainPairSerializer.get_token(user)
            refresh_token = str(token)
            access_token = str(token.access_token)

            response = Response(
                {
                    "user_id": login_serializer.data['user_id'],
                    "token": {
                        "access": access_token,
                        "refresh": refresh_token,
                    },
                },
                status=status.HTTP_200_OK,
            )
            return response
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
# 로그아웃
class LogoutView(APIView):
    # # permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": "Invalid refresh token or token has already been used."}, status=status.HTTP_400_BAD_REQUEST)
    # permission_classes = [ IsAuthenticated ]

    # def post(self, request, *args):
    #     user = RefreshTokenSerializer(data=request.data)
    #     user.is_valid(raise_exception=True)
    #     user.save()
    #     return Response(
    #             {
    #                "message": "logout success" 
    #             }, status=status.HTTP_204_NO_CONTENT)