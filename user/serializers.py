from .models import User
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from rest_framework_simplejwt.tokens import RefreshToken

# 회원가입용 시리얼라이저
class UserRegisterSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ['user_id', 'password', 'confirm_password']

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        
        if validated_data['password'] != self.initial_data['confirm_password']:
            raise serializers.ValidationError("잘못된 비밀번호입니다.")
        
        user = User.objects.create_user(
            user_id = validated_data['user_id'],
            password = validated_data['password'],
        )
        user.save()
        return user

# 로그인용 시리얼라이저
class UserLoginSerializer(serializers.ModelSerializer):
    user_id = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['user_id', 'password']

    def validate(self, attrs):
        user_id = attrs.get('user_id')
        password = attrs.get('password')

        if user_id.isdigit() and len(user_id) >= 11:
            user = User.objects.filter(phonenumber=user_id).first()
        else:
            # user_id = int(user_id) - 1000 # 1001과 같은 값으로 로그인할 수 있도록
            user = User.objects.filter(user_id=user_id).first()

        if user is None:
            raise serializers.ValidationError('잘못된 아이디입니다.')

        if not user.check_password(password):
            raise serializers.ValidationError('잘못된 비밀번호입니다.')

        attrs['user'] = user
        return attrs

    def create(self, validated_data):
        user = validated_data['user']
        return user

# 계정 확인용 시리얼라이저
class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_id']