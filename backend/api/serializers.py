from rest_framework import serializers

from users.models import User
from api.models import (
    Word, Question, UserProfile, Style, Device
)


class UserModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class UserProfileModelSerializer(serializers.ModelSerializer):
    # chao = serializers.SerializerMethodField('id')
    id = serializers.PrimaryKeyRelatedField(source='user', read_only=True)

    class Meta:
        model = UserProfile
        fields = '__all__'

        # fields = ['total_sentences', 'user', 'verified', 'screen_flow', 'email', 'id']


class WordModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Word
        fields = '__all__'


class QuestionModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Question
        fields = ['id', 'question', 'image_url', 'voice_url', 'type']


class QuestionFullSerializer(serializers.ModelSerializer):

    class Meta:
        model = Question
        fields = '__all__'


class StyleModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Style
        fields = '__all__'

class StylePresentationSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Style
        fields = ['background_screen', 'background_challenge', 'question_opacity']


class DeviceModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Device
        fields = '__all__'
