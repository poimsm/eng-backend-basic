# Python
import math
import re
import copy
import random
import traceback
from datetime import date
import uuid
from itertools import groupby
import os

# Framework
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import (
    api_view, renderer_classes, permission_classes
)
from django.contrib.auth.hashers import make_password
from rest_framework.renderers import JSONRenderer
from rest_framework.serializers import ValidationError
from django.db import transaction, IntegrityError
from rest_framework.exceptions import AuthenticationFailed
from django.db.models import Q


# Data
from api.constants import AppMsg

# Models
from users.models import User
from api.models import (
    Word, Question, UserProfile, Style,
    QuestionType, Difficulty, Device
)

# Serializers
from api.serializers import (
    QuestionModelSerializer,
    UserModelSerializer,
    UserProfileModelSerializer,
    DeviceModelSerializer,
    WordModelSerializer,
    StylePresentationSerializer,
    ScreenFlowSerializer,
)
from users.serializers import CustomTokenObtainPairSerializer

# Libraries
import uuid
from textblob import TextBlob
import nltk
from nltk.corpus import wordnet as wn
from word_forms.word_forms import get_word_forms
import logging
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import inflect
from nltk.stem.snowball import SnowballStemmer


logger = logging.getLogger('api_v1')
test_user_id = 1
appMsg = AppMsg()


langues = ['es', 'zh-Hans', 'pt', 'ar', 'hi']


@api_view(['GET'])
@renderer_classes([JSONRenderer])
@permission_classes([IsAuthenticated])
def user_data(request):
    try:
        user = UserProfile.objects.get(user=request.user.id)
        serializer = UserProfileModelSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as err:
        logger.error(traceback.format_exc())
        return Response({}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@renderer_classes([JSONRenderer])
def user_sign_in(request):
    try:
        tokens = CustomTokenObtainPairSerializer(request.data).validate(
            request.data,
        )

        profile = UserProfile.objects.filter(
            email=request.data['email']).first()
        serializer = UserProfileModelSerializer(profile)

        return Response({
            'user': serializer.data,
            'refresh': str(tokens['refresh']),
            'access': str(tokens['access']),
        }, status=status.HTTP_200_OK)

    except AuthenticationFailed:
        return Response(appMsg.EMAIL_OR_PASS_INCORRECT, status=status.HTTP_401_UNAUTHORIZED)

    except:
        logger.error(traceback.format_exc())
        return Response(appMsg.UNKNOWN_ERROR, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@renderer_classes([JSONRenderer])
def user_sign_up(request):
    try:
        data = request.data.copy()

        found_user = User.objects.filter(email=data['email']).first()
        if found_user:
            return Response(appMsg.EMAIL_EXISTS, status=status.HTTP_409_CONFLICT)
        with transaction.atomic():
            user_serializer = UserModelSerializer(data={
                'email': data['email'],
                'password': make_password(
                    data['password'], salt=None, hasher='default'),
            })
            user_serializer.is_valid(raise_exception=True)
            user_serializer.save()

            profile_serializer = UserProfileModelSerializer(data={
                'email': data['email'],
                'user': user_serializer.data['id'],
                'english_level': data['english_level'],
                'verified': False,
                'screen_flow': True,
            })
            profile_serializer.is_valid(raise_exception=True)
            profile_serializer.save()

            device_serializer = DeviceModelSerializer(data={
                'uuid': data['uuid'],
                'user': user_serializer.data['id']
            })
            device_serializer.is_valid(raise_exception=True)
            device_serializer.save()

        class UserPayload:
            id = user_serializer.data['id']

        refresh = CustomTokenObtainPairSerializer().get_token(UserPayload)

        return Response({
            'user': profile_serializer.data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)

    except Exception as err:
        logger.error(traceback.format_exc())
        return Response(appMsg.UNKNOWN_ERROR, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def hola(request):

    DEBUG = os.getenv('DEBUG', False) == 'False'
    return Response({'DEBUG': DEBUG}, status=status.HTTP_200_OK)


@api_view(['POST'])
def screen_flow(request):
    serializer = ScreenFlowSerializer(data={
        'device': request.data['device'],
        'value': request.data['value'],
        'time': request.data['time']
    })
    serializer.is_valid(raise_exception=True)
    serializer.save()

    return Response([], status=status.HTTP_201_CREATED)


@api_view(['GET', 'POST'])
def device(request):
    if request.method == 'GET':
        uuid = request.GET.get('uuid', None)

        if not uuid:
            return Response([], status=status.HTTP_400_BAD_REQUEST)

        try:
            device = Device.objects.get(uuid=uuid)
            return Response({'device_id': device.id}, status=status.HTTP_200_OK)
        except:
            return Response({}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'POST':
        uuid = request.data.get('uuid', None)

        if not uuid:
            return Response([], status=status.HTTP_400_BAD_REQUEST)

        try:
            device = Device.objects.get(uuid=uuid)
            if device:
                return Response({
                    'message': 'Device already exists.'
                }, status=status.HTTP_409_CONFLICT)
        except:
            pass

        serializer = DeviceModelSerializer(data={
            'uuid': uuid,
        })

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({'device_id': serializer.data['id']}, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def questions(request):
    questions = list(Question.objects.all())
    questions = random.sample(questions, 3)
    easy_questions = Question.objects.filter(
        type=QuestionType.DESCRIBE,
        difficulty=Difficulty.EASY,
    )
    questions.insert(0, random.choice(easy_questions))

    # questions = Question.objects.filter(
    #     # id__in=[11, 12, 13, 14, 15]
    #     # id__in=[16, 17, 18, 19, 20]
    #     # id__in=[21, 22, 23, 24, 25]
    #     # id__in=[26, 27, 28, 29, 30]
    #     # id__in=[1, 2, 3, 4, 5]
    #     # id__in=[6, 7, 8, 9, 10]

    #     id__in=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    #     # id__in=[11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
    # )

    lang = request.GET.get('lang', None)

    result = []
    for q in questions:
        words = []
        for w in q.words.all():
            examples = []
            for ex in w.examples:
                examples.append({
                    'value': ex['value'],
                    'voice_url': ex['voice_url'],
                    'translation': get_translation(ex['translations'], lang),
                })

            explanations = [{
                'image': w.explanations[0]['image'],
                'value': w.explanations[0]['value'],
                'translation': get_translation(w.explanations[0]['translations'], lang),
                # 'translation': w.explanations[0]['translations']
            }]

            words.append({
                'id': w.id,
                'word': w.word,
                'definition': w.definition,
                'translation': get_translation(w.translations, lang),
                'has_info': w.has_info,
                'examples': examples,
                'explanations': explanations,
                'story': w.story,
                'miniature': w.miniature
            })

        style = Style.objects.get(question=q.id)

        result.append({
            'id': q.id,
            'question': q.question,
            'image_url': q.image_url,
            'voice_url': q.voice_url,
            'example': q.example,
            'words': words,
            'style': StylePresentationSerializer(style).data
        })

    return Response(result)


def get_translation(items, lang):
    lang = 'es' if lang is None else lang
    result = ''
    for item in items:
        if item['lang'] == lang:
            result = item['text']
    return result
