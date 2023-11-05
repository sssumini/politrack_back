from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class UserManager(BaseUserManager):
    def create_user(self, user_id, password, **kwargs):
        if not user_id:
            raise ValueError('Users must have an user_id')
        
        user = self.model(
            user_id=user_id,
            **kwargs # 추가
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, user_id=None, password=None, **extra_fields):
        superuser = self.create_user(
            user_id=user_id,
            password=password,
        )
        
        superuser.is_staff = True
        superuser.is_superuser = True
        superuser.is_active = True
        
        superuser.save(using=self._db)
        return superuser

class User(AbstractBaseUser, PermissionsMixin):
    # user_id -> serialize=False가 문제가 되는 부분일수도 있음
    user_id = models.CharField(max_length=45, unique=True, null=False, blank=False)
    
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

	# 헬퍼 클래스 사용
    objects = UserManager()

	# 핸드폰 번호로 로그인
    USERNAME_FIELD = 'user_id'