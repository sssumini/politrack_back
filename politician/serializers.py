from rest_framework import serializers
#from .models import *
from politician.models import Community, Board, Quiz

class CommunitySerializer(serializers.ModelSerializer):
    formatted_created_at = serializers.DateTimeField(source='created_at', format='%Y.%m.%d, %H:%M:%S', read_only=True)
    formatted_deadline = serializers.DateTimeField(source='deadline', format='%Y.%m.%d, %H:%M:%S', read_only=True)


    class Meta:
        model = Community
        #fields = '__all__'
        fields = ('title', 'content', 'formatted_created_at', 'formatted_deadline')


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
