from rest_framework import serializers
#from .models import *
from politician.models import Community, Board, Quiz

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


class QuizSerializer(serializers.ModelSerializer):

    class Meta:
        model = Quiz
        fields = '__all__'
        #fields = ('title', 'content', 'created_at','deadline')
