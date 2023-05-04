from rest_framework import serializers

from users.models import User
from api.models import (
    UserSentence, Word, Question,
    Example, Style, ShortVideo,
    InfoCard, FavoriteResource,
    Collocation, ResourceSentence,
    ScreenFlow, UserProfile, Device,
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


class UserSentenceModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSentence
        fields = '__all__'


class ExampleModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Example
        fields = '__all__'


class StyleModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Style
        fields = '__all__'


class ShortVideoModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShortVideo
        fields = '__all__'


class InfoCardModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = InfoCard
        fields = '__all__'


class FavoriteResourceModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = FavoriteResource
        fields = '__all__'


class CollocationModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Collocation
        fields = '__all__'


class ResourceSentenceModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = ResourceSentence
        fields = '__all__'


class ResourceSentenceDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = ResourceSentence
        fields = ['id', 'sentence', 'meaning', 'extras', 'type', 'origin']


class ScreenFlowModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = ScreenFlow
        fields = '__all__'


class DeviceModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Device
        fields = '__all__'
