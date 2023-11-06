from rest_framework import serializers
#from .models import *
from main.models import Community, Board

class CommunitySerializer(serializers.ModelSerializer):

    class Meta:
        model = Community
        #fields = '__all__'
        fields = ('title', 'content', 'created_at','deadline')


class BoardSerializer(serializers.ModelSerializer):

    class Meta:
        model = Board
        fields = '__all__'
        #fields = ('title', 'content', 'created_at','deadline')