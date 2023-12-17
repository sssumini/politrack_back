from .models import User
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.validators import UniqueValidator
# import TokenError

# 회원가입용 시리얼라이저
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['user_id'] = user.user_id
        return token

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('user_id', 'password', 'confirm_password')

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."})

        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            user_id=validated_data['user_id']
        )

        user.set_password(validated_data['password'])
        user.save()
        return user

# 로그인용 시리얼라이저
class UserLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('user_id', 'password')
        
class RefreshTokenSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    class Meta:
        model = User
        fields = ('refresh')
    # default_error_messages = {
    #     'bad_token': 'Token is invalid or expired'
    # }

    # def validate(self, attrs):
    #     self.token = attrs['refresh']
    #     return attrs

    # def save(self, **kwargs):
    #     try:
    #         RefreshToken(self.token).blacklist()
    #     except TokenError:
    #         self.fail('bad_token')

# 계정 확인용 시리얼라이저
class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_id']