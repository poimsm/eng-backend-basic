# Python
import math
import re
import copy
import random
import traceback
from datetime import date
import uuid
from itertools import groupby


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
from api.data.common_words import common_words_list
from api.data.phrasal_verbs import phrasal_verbs
from api.data.slangs import slangs
from api.data.expresions import expresions
from api.constants import AppMsg

# Models & serializers
from users.models import User
from api.models import (
    Word, Question, QuestionTypes,
    UserSentence, Example, Style, ShortVideo,
    InfoCard, FavoriteResource, SourceTypes,
    SentenceTypes, SentenceOrigin, ResourceSentence,
    Status, Difficulty, Collocation, UserProfile,
    ScreenFlow, Device,
)
from api.serializers import (
    QuestionModelSerializer,
    UserModelSerializer,
    UserSentenceModelSerializer,
    ExampleModelSerializer,
    StyleModelSerializer,
    WordModelSerializer,
    ShortVideoModelSerializer,
    InfoCardModelSerializer,
    FavoriteResourceModelSerializer,
    QuestionFullSerializer,
    CollocationModelSerializer,
    ResourceSentenceModelSerializer,
    ResourceSentenceDetailSerializer,
    ScreenFlowModelSerializer,
    UserProfileModelSerializer,
    DeviceModelSerializer,
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

        add_screen_flow(None, profile.user.id, 'user_sign_in')
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

def synonym_antonym_extractor(phrase):
    # from nltk.corpus import wordnet
    synonyms = []
    antonyms = []

    for syn in wn.synsets(phrase):
        for l in syn.lemmas():
            synonyms.append(l.name())
            if l.antonyms():
                antonyms.append(l.antonyms()[0].name())
    return synonyms + antonyms

    # print(set(synonyms))
    # print(set(antonyms))

def pluralize(word):
    if re.search('[sxz]$', word):
         return re.sub('$', 'es', word)
    elif re.search('[^aeioudgkprt]h$', word):
        return re.sub('$', 'es', word)
    elif re.search('[aeiou]y$', word):
        return re.sub('y$', 'ies', word)
    else:
        return word + 's'


def check_singular2(word):
    if re.search('[sxz]$', word):
         return 'True 1'
    elif re.search('[^aeioudgkprt]h$', word):
        return 'True 2'
    elif re.search('[aeiou]y$', word):
        return 'True 3'
    elif re.search('[s]$', word):
        return 'False 1'
    else:
        return 'False 2'

def check_singular(word):
    p = inflect.engine()
    return p.singular_noun(word) == False

# library(wordnet)
# inWordnet <- function(w, pos =  c("ADJECTIVE", "ADVERB", "NOUN", "VERB")) {
#   for (x in pos) {
#      filter= getTermFilter("ExactMatchFilter", w, TRUE)
#      terms= getIndexTerms(x, 5, filter)
#      if (!is.null(terms)) return(True)
#   }
#   return(FALSE)
# }
# inWordnet("car")


def inWordnet(word):
    wn_lemmas = set(wn.all_lemma_names())
    return word in wn_lemmas

def isplural(word):
    wnl = WordNetLemmatizer()
    lemma = wnl.lemmatize(word)
    if len(lemma) == 0:
        return False, None
    plural = True if word is not lemma else False
    return True, plural


def check_plural(word):

    exist, asd = isplural(word)

    if exist:
        return asd

    # if inWordnet(word):
    #     return isplural(word)

    if re.search('es$', word):
        return 'True 1'
    if re.search('ies$', word):
        return 'True 2'
    if re.search('s$', word):
        return 'True 3'
    else:
        return 'False 0'


def asdasd(word):
    stemmer = SnowballStemmer(language="english")
    return stemmer.stem(word)


@api_view(['GET'])
@renderer_classes([JSONRenderer])
def hola(request):

    word = request.GET.get('word', 'fast')

    # syn = wn.synsets(word)[0].hypernyms()[0].lemma_names()
    # return Response({'hola': syn}, status=status.HTTP_200_OK)


    # syn = synonym_antonym_extractor(word)
    # return Response({'hola': syn}, status=status.HTTP_200_OK)


    # forms = get_word_forms(word)
    # all_forms = forms['n'] | forms['a'] | forms['v'] | forms['r']
    # return Response({'all_forms': all_forms}, status=status.HTTP_200_OK)



   
    return Response({'asd':  asdasd(word)}, status=status.HTTP_200_OK)




    # return Response({'plural_form': pluralize(word), 
    # 'check_plural': check_plural(word), 
    # 'inWordnet': inWordnet(word),
    # 'inflect': inflect.engine().plural_noun(word),
    # 'check_singular': check_singular(word),
    # 'exist': True if wn.synsets(word) else False,
    # 'exist2': True if len(wn.lemmas(word)) > 0 else False,
    # 'asdsd': [str(lemma.name()) for lemma in wn.lemmas(word)]
    # }, status=status.HTTP_200_OK)
    


    # return Response({'hola': 'hooola'}, status=status.HTTP_200_OK)

    # favorites = FavoriteResource.objects.filter(
    #     Q(info_card__isnull=False) | Q(short_video__isnull=False))

    # # designation_key_func = lambda member: member.designation
    # # queryset = Members.objects.all().select_related("designation")

    # def designation_key_func(
    #     member): return member.info_card or member.short_video
    # queryset = favorites
    # maap = []
    # for designation, member_group in groupby(queryset, designation_key_func):
    #     maap.append({
    #         'designation': None if not designation else InfoCardModelSerializer(designation).data if designation.info_card else ShortVideoModelSerializer(designation).data,
    #         'member_group': [] if not member_group else FavoriteResourceModelSerializer(list(member_group), many=True).data
    #     })
    # logger.debug(maap)
    # return Response(maap, status=status.HTTP_200_OK)

    # favorite = FavoriteResource.objects.get(
    #     id=1,
    #     status=Status.ACTIVE
    # )
    # serializer = FavoriteResourceModelSerializer(favorite)
    # return Response(serializer.data, status=status.HTTP_200_OK)

    # uuid = request.META.get('HTTP_UUID', None)
    # return Response({'uuid': uuid}, status=status.HTTP_200_OK)

    # uuid = '0d14fbaa-8cd6-11e7-b2ed-28d244cd6e76'
    # valid = is_valid_uuid(uuid)
    # add_screen_flow(uuid, 14, 'hello-world')
    # return Response({'valid': valid}, status=status.HTTP_200_OK)

    # profile = UserProfile.objects.get(user__id=11)
    # profile.email = 'heeey@gmail.com'
    # profile.save()

    # id = request.GET['id']
    # return Response({'id': id}, status=status.HTTP_200_OK)

    # data = get_random_questions([12], 3)

    # sentence = UserSentence(
    #     id=1,
    #     sentence='asdasd',
    #     meaning='asdad',
    #     origin=1,
    #     type=1,
    #     sourceType=1,
    #     info_card=1,
    #     short_video=1,
    # )

    # sentence = UserSentence(
    #     id=1,
    #     sentence='asdasd',
    #     meaning='asdad',
    #     origin=1,
    #     type=1,
    #     source_type=1,
    #     # info_card=1,
    # )

    # sentence.info_card = 1

    # ser = UserSentenceModelSerializer(sentence)

    # return Response(ser.data, status=status.HTTP_200_OK)

    # username = uuid.uuid4().hex[:10]
    # email = username + '@fake.com'
    # password = username

    # data = {
    #     'username': username,
    #     'email': email,
    #     'password': password,
    # }

    # return Response(data, status=status.HTTP_200_OK)

    # sentence='go up';
    # sentence='went out';
    # sentence='I hang you out';
    # sentence='hold on!';
    # sentence='hold me on!';
    # sentence='I hold realy you do me on!';
    # sentence='OK! I catch you up later!!';
    # sentence='I want to broken up!';
    # sentence='I gave up, I want to broken up!';

    # sentence = 'I will motherfucker you!'
    # phrasal_verbs = extract_phrasal_verbs(sentence)

    # hasSlang = check_for_slangs(sentence)
    # return Response({'len': hasSlang}, status=status.HTTP_200_OK)



@api_view(['GET'])
@renderer_classes([JSONRenderer])
def library_short_video(request):
    id = request.GET.get('id', None)

    if id:
        videos = ShortVideo.objects.filter(id=id)
    else:
        videos = ShortVideo.objects.all().order_by('-created')

    result = []
    for video in videos:
        sentences = ResourceSentence.objects.filter(
            short_video=video.id,
            status=Status.ACTIVE
        )

        collocations = Collocation.objects.filter(
            short_video=video.id,
            status=Status.ACTIVE
        )

        collocationStringList = [col.text for col in collocations]

        result.append({
            'id': video.id,
            'cover': video.cover,
            'url': video.url,
            'is_favorite': False,
            'sentences': ResourceSentenceDetailSerializer(
                sentences, many=True).data,
            'collocations': collocationStringList
        })

    uuid = request.META.get('HTTP_UUID', None)
    add_screen_flow(uuid, None, 'library_short_video->GET')

    if len(result) == 1:
        data = result[0]
    else:
        data = result

    return Response(data, status=status.HTTP_200_OK)


@api_view(['GET'])
@renderer_classes([JSONRenderer])
def library_info_card(request):
    id = request.GET.get('id', None)

    if id:
        card = InfoCard.objects.get(id=id)
        sentences = get_sentences_by_card_id(card.id)
        collocations = get_collocations_by_card_id(card.id)

        return Response({
            'id': card.id,
            'image_url': card.image_url,
            'voice_url': card.voice_url,
            'is_favorite': False,
            'sentences': ResourceSentenceDetailSerializer(
                sentences, many=True).data,
            'collocations': collocations
        }, status=status.HTTP_200_OK)

    existing_groups = [1, 2]
    group = random.choice(existing_groups)

    cards = InfoCard.objects.filter(
        group=group
    ).order_by('-created')

    result = []
    for card in cards:
        sentences = get_sentences_by_card_id(card.id)
        collocations = get_collocations_by_card_id(card.id)
        result.append({
            'id': card.id,
            'image_url': card.image_url,
            'voice_url': card.voice_url,
            'is_favorite': False,
            'sentences': ResourceSentenceDetailSerializer(
                sentences, many=True).data,
            'collocations': collocations
        })

    random.shuffle(result)

    uuid = request.META.get('HTTP_UUID', None)
    add_screen_flow(uuid, None, 'library_info_card->GET')

    return Response(result, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@renderer_classes([JSONRenderer])
def user_short_video(request):
    try:
        id = request.GET.get('id', None)

        if id:
            videos = ShortVideo.objects.filter(id=id)
        else:
            videos = ShortVideo.objects.all().order_by('-created')

        user_videos = FavoriteResource.objects.filter(
            source_type=SourceTypes.SHORT_VIDEO,
            user=request.user.id,
            status=Status.ACTIVE,
        )

        result = []
        for video in videos:
            is_favorite = False
            for user_vid in user_videos:
                if video.id == user_vid.short_video.id:
                    is_favorite = True

            sentences = get_sentences_by_video_id(video.id)
            collocations = get_collocations_by_video_id(video.id)

            result.append({
                'id': video.id,
                'cover': video.cover,
                'url': video.url,
                'is_favorite': is_favorite,
                'sentences': ResourceSentenceDetailSerializer(
                    sentences, many=True).data,
                'collocations': collocations
            })

        uuid = request.META.get('HTTP_UUID', None)
        add_screen_flow(uuid, None, 'user_short_video->GET')

        if len(result) == 1:
            data = result[0]
        else:
            data = result

        return Response(data, status=status.HTTP_200_OK)
    except:
        logger.error(traceback.format_exc())
        return Response({}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@renderer_classes([JSONRenderer])
def user_info_card(request):
    try:
        id = request.GET.get('id', None)

        if id:
            card = InfoCard.objects.get(id=id)
            sentences = get_sentences_by_card_id(card.id)
            collocations = get_collocations_by_card_id(card.id)

            return Response({
                'id': card.id,
                'image_url': card.image_url,
                'voice_url': card.voice_url,
                'is_favorite': False,
                'sentences': ResourceSentenceDetailSerializer(
                    sentences, many=True).data,
                'collocations': collocations
            }, status=status.HTTP_200_OK)

        existing_groups = [1, 2]
        group = random.choice(existing_groups)

        cards = InfoCard.objects.filter(
            group=group
        ).order_by('-created')

        user_cards = FavoriteResource.objects.filter(
            source_type=SourceTypes.INFO_CARD,
            user=request.user.id,
            status=Status.ACTIVE
        )

        result = []
        for card in cards:
            is_favorite = False

            for user_card in user_cards:
                if card.id == user_card.info_card.id:
                    is_favorite = True
                    break

            sentences = get_sentences_by_card_id(card.id)
            collocations = get_collocations_by_card_id(card.id)

            result.append({
                'id': card.id,
                'image_url': card.image_url,
                'voice_url': card.voice_url,
                'is_favorite': is_favorite,
                'sentences': ResourceSentenceDetailSerializer(
                    sentences, many=True).data,
                'collocations': collocations
            })

        random.shuffle(result)

        uuid = request.META.get('HTTP_UUID', None)
        add_screen_flow(uuid, None, 'library_info_card->GET')

        return Response(result, status=status.HTTP_200_OK)
    except:
        logger.error(traceback.format_exc())
        return Response({}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET', 'POST', 'DELETE'])
@renderer_classes([JSONRenderer])
@permission_classes([IsAuthenticated])
def user_favorites(request):
    if request.method == 'GET':
        try:
            id = request.GET.get('id', None)

            if not id:
                favorites = FavoriteResource.objects.filter(
                    user__id=request.user.id,
                    status=Status.ACTIVE
                ).order_by('-created')

                result = []
                for fav in favorites:
                    if fav.info_card:
                        result.append({
                            'id': fav.id,
                            'source_type': SourceTypes.INFO_CARD,
                            'info_card': fav.info_card.id,
                            'image_url': fav.info_card.image_url,
                        })
                    elif fav.short_video:
                        result.append({
                            'id': fav.id,
                            'source_type': SourceTypes.SHORT_VIDEO,
                            'short_video': fav.short_video.id,
                            'image_url': fav.short_video.cover,
                        })

                return Response(result, status=status.HTTP_200_OK)

            favorite = FavoriteResource.objects.get(
                id=id,
                user__id=request.user.id,
                status=Status.ACTIVE
            )

            if favorite.info_card:
                card = favorite.info_card
                sentences = ResourceSentence.objects.filter(
                    info_card=card.id,
                    status=Status.ACTIVE
                )

                collocations = Collocation.objects.filter(
                    info_card=card.id,
                    status=Status.ACTIVE
                )

                collocationStringList = [col.text for col in collocations]

                add_screen_flow(None, request.user.id, 'user_favorites->card')

                return Response({
                    'type': SourceTypes.INFO_CARD,
                    'card': {
                        'id': card.id,
                        'image_url': card.image_url,
                        'voice_url': card.voice_url,
                        'is_favorite': True,
                        'sentences': ResourceSentenceDetailSerializer(
                            sentences, many=True).data,
                        'collocations': collocationStringList
                    }
                }, status=status.HTTP_200_OK)

            if favorite.short_video:
                id = request.GET.get('id', -1)
                video = favorite.short_video
                sentences = ResourceSentence.objects.filter(
                    short_video=video.id,
                    status=Status.ACTIVE
                )

                collocations = Collocation.objects.filter(
                    short_video=video.id,
                    status=Status.ACTIVE
                )

                collocationStringList = [col.text for col in collocations]

                add_screen_flow(None, request.user.id, 'user_favorites->video')

                return Response({
                    'type': SourceTypes.SHORT_VIDEO,
                    'video': {
                        'id': video.id,
                        'cover': video.cover,
                        'url': video.url,
                        'is_favorite': True,
                        'sentences': ResourceSentenceDetailSerializer(
                            sentences, many=True).data,
                        'collocations': collocationStringList
                    }
                }, status=status.HTTP_200_OK)

        except:
            logger.error(traceback.format_exc())
            return Response({}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'POST':
        try:
            is_video = request.data['source_type'] == SourceTypes.SHORT_VIDEO
            source_key = 'short_video' if is_video else 'info_card'

            new_data = {
                source_key: request.data['id'],
                'source_type': request.data['source_type'],
                'user': request.user.id,
            }

            fav_serializer = FavoriteResourceModelSerializer(data=new_data)
            fav_serializer.is_valid(raise_exception=True)
            fav_serializer.save()

            if is_video:
                sentences = ResourceSentence.objects.filter(
                    short_video=new_data[source_key],
                    status=Status.ACTIVE
                )
            else:
                sentences = ResourceSentence.objects.filter(
                    info_card=new_data[source_key],
                    status=Status.ACTIVE
                )

            ids = []
            for sen in sentences:
                sen_data = {
                    'sentence': sen.sentence,
                    'meaning': sen.meaning,
                    'extras': sen.extras,
                    'type': sen.type,
                    'origin': SentenceOrigin.RESOURCE,
                    'user': request.user.id,
                    'source_type': new_data['source_type'],
                    source_key: new_data[source_key]
                }

                sen_serializer = UserSentenceModelSerializer(data=sen_data)
                sen_serializer.is_valid(raise_exception=True)
                sen_serializer.save()
                ids.append(sen_serializer.data['id'])

            uuid = request.META.get('HTTP_UUID', None)
            add_screen_flow(uuid, None, 'short_video->POST')

            return Response({'sentences_ids': ids}, status=status.HTTP_200_OK)
        except:
            logger.error(traceback.format_exc())
            return Response({}, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        try:
            data = request.data.copy()
            if data['source_type'] == SourceTypes.INFO_CARD:
                FavoriteResource.objects.filter(
                    user=request.user.id,
                    info_card=data['id']
                ).update(status=Status.DELETED)

                UserSentence.objects.filter(
                    user=request.user.id,
                    info_card=data['id'],
                ).update(status=Status.DELETED)

            if data['source_type'] == SourceTypes.SHORT_VIDEO:
                FavoriteResource.objects.filter(
                    user=request.user.id,
                    short_video=data['id']
                ).update(status=Status.DELETED)

                UserSentence.objects.filter(
                    user=request.user.id,
                    short_video=data['id'],
                ).update(status=Status.DELETED)

            uuid = request.META.get('HTTP_UUID', None)
            add_screen_flow(uuid, None, 'user_favorites->DELETE')

            return Response({
                'sentences_ids': [data['id']]
            }, status=status.HTTP_200_OK)

        except:
            logger.error(traceback.format_exc())
            return Response({}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@renderer_classes([JSONRenderer])
@permission_classes([IsAuthenticated])
def user_stats(request):
    videos = UserSentence.objects.filter(
        user__id=request.user.id,
        short_video__isnull=False,
        status=Status.ACTIVE
    ).distinct('short_video__id')

    cards = UserSentence.objects.filter(
        user__id=request.user.id,
        info_card__isnull=False,
        status=Status.ACTIVE
    ).distinct('info_card__id')

    sentences = UserSentence.objects.filter(
        user__id=request.user.id,
        status=Status.ACTIVE
    )

    add_screen_flow(None, request.user.id, 'user_stats')

    return Response({
        'id': request.user.id,
        'total_videos': len(videos),
        'total_cards': len(cards),
        'total_sentences': len(sentences),
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@renderer_classes([JSONRenderer])
@permission_classes([IsAuthenticated])
def user_profile_data(request):
    favorites = FavoriteResource(
        user__id=request.user.id,
        status=Status.ACTIVE
    )

    fav_serializer = FavoriteResourceModelSerializer(favorites, many=True)
    profile = UserProfile(user__id=request.user.id)

    profile_serializer = UserProfileModelSerializer(profile)

    add_screen_flow(None, request.user.id, 'user_profile_data')

    return Response({
        'profile': profile_serializer.data,
        'favorites': fav_serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@renderer_classes([JSONRenderer])
@permission_classes([IsAuthenticated])
def save_local_sens(request):
    try:
        local_sentences = request.data['local_sentences']

        if isinstance(local_sentences, dict) and len(local_sentences) > 12:
            return Response(appMsg.TOO_MANY_ITEMS, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(id=request.user.id).first()

        local_sentences_reduced = []
        card_memory = []
        video_memory = []
        for local in local_sentences:
            if local['info_card']:
                if local['info_card'] in card_memory:
                    continue
                else:
                    local_sentences_reduced.append(local)
                    card_memory.append(local['info_card'])
            elif local['short_video']:
                if local['short_video'] in video_memory:
                    continue
                else:
                    local_sentences_reduced.append(local)
                    video_memory.append(local['short_video'])
            else:
                local_sentences_reduced.append(local)

        for local in local_sentences_reduced:
            if local['info_card']:
                with transaction.atomic():
                    card_obj = InfoCard.objects.get(id=local['info_card'])
                    sentence_obj = ResourceSentence.objects.filter(
                        info_card=card_obj.id)

                    for sen in sentence_obj:
                        UserSentence(
                            sentence=sen.sentence,
                            meaning=sen.meaning,
                            extras=sen.extras,
                            last_time_used=date.today(),
                            type=sen.type,
                            origin=SentenceOrigin.RESOURCE,
                            source_type=SourceTypes.INFO_CARD,
                            info_card=card_obj,
                            user=user
                        ).save()

                    FavoriteResource(
                        info_card=card_obj,
                        source_type=SourceTypes.INFO_CARD,
                        user=user
                    ).save()

            elif local['short_video']:
                with transaction.atomic():
                    video_obj = ShortVideo.objects.get(id=local['short_video'])
                    sentence_obj = ResourceSentence.objects.filter(
                        short_video=video_obj.id)

                    for sen in sentence_obj:
                        UserSentence(
                            sentence=sen.sentence,
                            meaning=sen.meaning,
                            extras=sen.extras,
                            last_time_used=date.today(),
                            type=sen.type,
                            origin=SentenceOrigin.RESOURCE,
                            source_type=SourceTypes.SHORT_VIDEO,
                            short_video=video_obj,
                            user=user
                        ).save()

                    FavoriteResource(
                        short_video=video_obj,
                        source_type=SourceTypes.SHORT_VIDEO,
                        user=user
                    ).save()
            else:
                UserSentence(
                    type=SentenceTypes.NORMAL,
                    origin=SentenceOrigin.USER,
                    sentence=local['sentence'],
                    meaning=local['meaning'],
                    last_time_used=date.today(),
                    user=user
                ).save()

        add_screen_flow(None, request.user.id, 'save_local_sentences')
        return Response({}, status=status.HTTP_201_CREATED)

    except:
        logger.error(traceback.format_exc())
        return Response({}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@renderer_classes([JSONRenderer])
@permission_classes([IsAuthenticated])
def screen_flow(request):
    add_screen_flow(request.data['uuid'], None, request.data['type'])
    return Response({}, status=status.HTTP_200_OK)


@api_view(['POST'])
@renderer_classes([JSONRenderer])
def local_sens_to_sentences(request):
    data = request.data.copy()
    local_sentences = data['local_sentences']

    result = []
    for local in local_sentences:
        sentence = local
        if local.get('info_card', False):
            card = InfoCard.objects.get(id=local['info_card'])
            sentences = ResourceSentence.objects.filter(
                info_card=card.id,
                status=Status.ACTIVE
            )

            sentence['info_card'] = InfoCardModelSerializer(
                card).data
            sentence['info_card']['sentences'] = ResourceSentenceDetailSerializer(
                sentences, many=True).data

            collocations = Collocation.objects.filter(
                info_card=card.id,
                status=Status.ACTIVE
            )

            collocationList = [col.text for col in collocations]
            sentence['info_card']['collocations'] = collocationList

        if local.get('short_video', False):
            video = ShortVideo.objects.get(id=local['short_video'])
            sentences = ResourceSentence.objects.filter(
                short_video=video.id,
                status=Status.ACTIVE
            )
            sentence['short_video'] = ShortVideoModelSerializer(
                video).data
            sentence['short_video']['sentences'] = ResourceSentenceDetailSerializer(
                sentences, many=True).data

            collocations = Collocation.objects.filter(
                short_video=video.id,
                status=Status.ACTIVE
            )

            collocationList = [col.text for col in collocations]
            sentence['short_video']['collocations'] = collocationList

        result.append(sentence)

    uuid = request.META.get('HTTP_UUID', None)
    add_screen_flow(uuid, None, 'local_sentences_to_sentences')

    return Response(result, status=status.HTTP_200_OK)


@api_view(['POST'])
@renderer_classes([JSONRenderer])
def local_sens_to_favorites(request):
    try:
        local_sentences = request.data['local_sentences']
        result = []

        for local in local_sentences:
            if local['source_type'] == SourceTypes.INFO_CARD:
                card = InfoCard.objects.get(id=local['info_card'])
                result.append({
                    'id': -1,
                    'source_type': SourceTypes.INFO_CARD,
                    'info_card': card.id,
                    'image_url': card.image_url
                })

            if local['source_type'] == SourceTypes.SHORT_VIDEO:
                video = ShortVideo.objects.get(id=local['short_video'])
                result.append({
                    'id': -1,
                    'source_type': SourceTypes.SHORT_VIDEO,
                    'short_video': video.id,
                    'image_url': video.cover
                })

        uuid = request.META.get('HTTP_UUID', None)
        add_screen_flow(uuid, None, 'local_sentences_to_favorites')

        return Response(result, status=status.HTTP_200_OK)

    except Exception as e:
        logger.exception(e)
        return Response({}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST', 'PUT', 'DELETE'])
@renderer_classes([JSONRenderer])
@permission_classes([IsAuthenticated])
def user_sentences(request):
    if request.method == 'GET':
        page = int(request.GET.get('page', 1))
        per_page = 200

        sentences = UserSentence.objects.filter(
            user__id=request.user.id,
            status=Status.ACTIVE
        ).order_by('-created')

        total = sentences.count()
        start = (page - 1)*per_page
        end = page*per_page

        serializer = UserSentenceModelSerializer(
            sentences[start:end], many=True)

        sentences = serializer.data
        sentences = add_videos_and_cards_into_sentences(sentences)

        add_screen_flow(None, request.user.id, 'user_sentences->GET')

        return Response({
            'data': sentences,
            'total_items': total,
            'current_page': page,
            'total_pages': math.ceil(total / per_page)
        }, status=status.HTTP_200_OK)

    if request.method == 'POST':
        data = request.data.copy()

        if check_for_slangs(data['sentence']):
            add_screen_flow(None, request.user.id,
                            'user_sentences->POST->ofensive')
            return Response(appMsg.OFENSIVE_STATEMENT, status=status.HTTP_400_BAD_REQUEST)

        sentence = {
            'user': request.user.id,
            'sentence': data['sentence'],
            'meaning': data['meaning'] if data['meaning'] else '',
            'type': SentenceTypes.NORMAL,
            'origin': SentenceOrigin.USER
        }

        serializer = UserSentenceModelSerializer(data=sentence)
        if serializer.is_valid():
            serializer.save()
            add_screen_flow(None, request.user.id,
                            'user_sentences->POST->valid')
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        add_screen_flow(None, request.user.id, 'user_sentences->POST->error')
        return Response(appMsg.INVALID_DATA, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'PUT':
        try:
            data = request.data.copy()

            if check_for_slangs(data['sentence']):
                add_screen_flow(None, request.user.id,
                                'user_sentences->PUT->ofensive')
                return Response(appMsg.OFENSIVE_STATEMENT, status=status.HTTP_400_BAD_REQUEST)

            sentence = UserSentence.objects.get(
                id=data.get('id', None), user__id=request.user.id)
            serializer = UserSentenceModelSerializer(
                sentence, data=data, partial=True)

            if serializer.is_valid(raise_exception=True):
                serializer.save()
                add_screen_flow(None, request.user.id,
                                'user_sentences->PUT->valid')
                return Response(serializer.data, status=status.HTTP_200_OK)

            add_screen_flow(None, request.user.id,
                            'user_sentences->PUT->error')
            return Response(appMsg.INVALID_DATA, status=status.HTTP_400_BAD_REQUEST)

        except UserSentence.DoesNotExist:
            return Response({}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception(e)
            return Response(appMsg.UNKNOWN_ERROR, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    if request.method == 'DELETE':
        try:
            sentence = UserSentence.objects.get(id=request.data['id'])
            sentence.status = Status.DELETED
            sentence.save()
            return Response({}, status=status.HTTP_200_OK)
        except UserSentence.DoesNotExist:
            return Response(appMsg.ID_NOT_FOUND, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception(e)
            return Response(appMsg.UNKNOWN_ERROR, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@renderer_classes([JSONRenderer])
def activity_pack(request):

    data = request.data.copy()
    local_sentences = data.get('local_sentences', [])

    all_sentences_ok = True
    for sen in local_sentences:
        if not (isinstance(sen['sentence'], str) and len(sen['sentence']) <= 20):
            all_sentences_ok = False
            break

    if len(local_sentences) > 12:
        all_sentences_ok = False

    if not all_sentences_ok:
        return Response({}, status=status.HTTP_400_BAD_REQUEST)

    sentences = convert_local_sentences_to_sentences(local_sentences)
    questions = get_questions_per_sentence(sentences)
    activities = create_activity_package(questions)
    activities = add_examples(activities)
    activities = add_styles(activities)
    activities = add_videos_and_cards(activities)

    uuid = request.META.get('HTTP_UUID', None)
    add_screen_flow(uuid, None, 'daily_activities_limited')

    return Response(activities, status=status.HTTP_200_OK)


@api_view(['GET'])
@renderer_classes([JSONRenderer])
@permission_classes([IsAuthenticated])
def user_activity_pack(request):

    sentences = get_sentences(request.user.id)
    questions = get_questions_per_sentence(sentences)
    activities = create_activity_package(questions)
    activities = add_examples(activities)
    activities = add_styles(activities)
    activities = add_videos_and_cards(activities)

    add_screen_flow(None, request.user.id, 'daily_activities')

    return Response(activities, status=status.HTTP_200_OK)


def get_sentences(id):
    all_sentences = list(UserSentence.objects.filter(
        user__id=id, status=Status.ACTIVE))
    random.shuffle(all_sentences)
    range_total = 10 if len(all_sentences) > 10 else len(all_sentences)
    sentences_obj = [all_sentences[i] for i in range(range_total)]

    return sentences_obj


def get_questions_per_sentence(sentences):
    questions_sentence = []
    for sen in sentences:
        questions_sentence.append({
            'questions': get_questions(sen.sentence),
            'sentence': UserSentenceModelSerializer(sen).data
        })

    memory = []
    result = []
    for q_s in questions_sentence:
        for q in q_s['questions']:
            if q_s['sentence'] in memory:
                continue

            if len(result) > 6:
                break

            result.append({
                'question': q['question'],
                'sentence': q_s['sentence']
            })
            memory.append(q_s['sentence'])

    return result


def get_questions(sentence):
    sentences = tokenize_sentences(str(sentence))
    literal_questions = literal_search(sentences)

    sentence_blob = TextBlob(sentence)
    sentence_blob = sentence_blob.correct()
    sentences = tokenize_sentences(str(sentence_blob))
    refined_questions = refined_search(sentences)

    phrasal_verbs = extract_phrasal_verbs(sentence)
    phrasal_verbs_questions = literal_search(phrasal_verbs)

    found_questions = combine_unique2(
        [literal_questions, refined_questions, phrasal_verbs_questions])

    if len(found_questions) == 0:
        questions = Question.objects.filter(type=QuestionTypes.NORMAL)
        q = random.choice(questions)

        found_questions.append({
            'question': QuestionModelSerializer(q).data,
            'sentence': None
        })
    return found_questions


def create_activity_package(found_questions):
    found_questions = copy.deepcopy(found_questions)

    result = []

    if len(found_questions) == 0:
        easy_questions, ids = get_easy_questions_with_examples(2)
        random_questions = get_random_questions(ids, 4)
        gap_questions = random_questions + found_questions
        random.shuffle(gap_questions)
        result = easy_questions + gap_questions
    elif len(found_questions) < 6:
        ids = [q['question']['id'] for q in found_questions]
        total = 6 - len(found_questions)
        result = found_questions + get_random_questions(ids, total)
        random.shuffle(result)
    else:
        found_questions = random.sample(found_questions, 6)
        # ids = [q['question']['id'] for q in found_questions]
        # result = found_questions + get_random_questions(ids, 2)
        result = found_questions
        random.shuffle(result)

    hasDescribeImg = False
    for r in result:
        if r['question']['type'] == QuestionTypes.DESCRIBE_IMAGE:
            hasDescribeImg = True
            break

    if not hasDescribeImg:
        questions = Question.objects.filter(type=QuestionTypes.DESCRIBE_IMAGE)
        q = random.choice(questions)

        result[4] = {
            'question': QuestionModelSerializer(q).data,
            'sentence': None
        }

    return result


def extract_phrasal_verbs(sentence):
    sentences_raw = re.findall(r"\w+", sentence.strip())

    sentences = []
    for w in sentences_raw:
        sentences.append(WordNetLemmatizer().lemmatize(w, 'v'))

    possible_match = []
    for v in phrasal_verbs:
        verb = v.split('_')[0]
        for sentence in sentences:
            if sentence == verb:
                if sentence not in possible_match:
                    possible_match.append({
                        'sentence': sentence,
                        'phrasal_verb': v,
                        'end': v.split('_')[1]
                    })

    matches = []
    for m in possible_match:
        for w in sentences:
            if w == m['end']:
                if m['phrasal_verb'] not in matches:
                    matches.append(m['phrasal_verb'])
    return matches


def check_for_slangs(sentence):
    sentences = re.findall(r"\w+", sentence.strip())
    sentences = filter(lambda w: w.lower() in slangs, sentences)
    return len(list(sentences)) != 0


def tokenize_sentences(sentence):
    sentences = re.findall(r"\w+", sentence.strip())
    sentences = filter(lambda w: len(w) > 2, sentences)
    sentences = filter(lambda w: not w.lower() in common_words_list, sentences)
    return list(sentences)


def literal_search(sentences):
    questions = []
    for sentence in sentences:
        try:
            word_obj = Word.objects.get(word=sentence)
            questions_list = Question.objects.filter(
                words__id=word_obj.id)
            for q in questions_list:
                questions.append({
                    'question': QuestionModelSerializer(q).data,
                    'sentence': WordModelSerializer(word_obj).data
                })

        except Word.DoesNotExist:
            pass
        except Exception as e:
            logger.exception(e)

    return questions


def refined_search(sentences):
    all_forms = set()
    for sentence in sentences:
        forms = get_word_forms(sentence)
        all_forms = all_forms | forms['n'] | forms['a'] | forms['v'] | forms['r']

    questions = []
    for sentence in all_forms:
        try:
            word_obj = Word.objects.get(word=sentence)
            questions_list = Question.objects.filter(
                words__id=word_obj.id)
            for q in questions_list:
                questions.append({
                    'question': QuestionModelSerializer(q).data,
                    'sentence': WordModelSerializer(word_obj).data
                })

        except Word.DoesNotExist:
            pass
        except Exception as e:
            logger.exception(e)

    return questions


def combine_unique2(list_to_combine):
    list_to_combine = copy.deepcopy(list_to_combine)

    questions = []
    for l in list_to_combine:
        questions += l

    memory = []
    unique = []

    for item in questions:
        q_id = item['question']['id']
        if q_id not in memory:
            memory.append(q_id)
            unique.append(item)

    new_questions = []
    for q_unique in unique:
        all_questions = list(
            filter(lambda q: q['question']['id'] == q_unique['question']['id'], questions))
        sentences = []
        for q in all_questions:
            sentences.append(q['sentence'])

        sentences = combine_unique_sentences([sentences])
        random.shuffle(sentences)
        new_questions.append({
            'question': q_unique['question'],
            'sentence': sentences[0]
        })

    return new_questions


def combine_unique_sentences(list_to_combine):
    list = []

    for l in list_to_combine:
        list += l

    memory = []
    unique = []

    for item in list:
        id = item['id']
        if id not in memory:
            memory.append(id)
            unique.append(item)

    return unique


def combine_unique(list_to_combine):
    list_to_combine = copy.deepcopy(list_to_combine)

    list = []
    for l in list_to_combine:
        list += l

    random.shuffle(list)

    memory = []
    unique = []

    for item in list:
        q_id = item['question']['id']
        if q_id not in memory:
            memory.append(q_id)
            unique.append(item)

    return unique


def add_examples(activities):
    new_activities = []
    for act in activities:
        new_act = copy.deepcopy(act)
        if act['sentence']:
            try:
                example_obj = Example.objects.get(
                    question=act['question']['id'],
                    sentence_text=act['sentence']['sentence']
                )

                serializer = ExampleModelSerializer(example_obj)
                new_act['example'] = serializer.data
                new_activities.append(new_act)

            except Example.DoesNotExist:
                new_activities.append(new_act)
            except Exception as e:
                logger.exception(e)
                new_activities.append(new_act)
        else:
            new_activities.append(new_act)

    return new_activities


def add_styles(activities):
    new_activities = []
    for act in activities:
        new_act = act
        try:
            style_obj = Style.objects.get(
                question=act['question']['id']
            )

            serializer = StyleModelSerializer(style_obj)
            new_act['style'] = serializer.data
            new_activities.append(new_act)

        except Style.DoesNotExist:
            new_activities.append(act)
        except Exception as e:
            logger.exception(e)
            new_activities.append(act)
    return new_activities


def add_videos_and_cards(activities):
    new_activities = []
    for act in activities:
        new_act = act
        try:
            if act['sentence'] and act['sentence']['info_card']:
                card = InfoCard.objects.get(id=act['sentence']['info_card'])
                sentences = ResourceSentence.objects.filter(
                    info_card=card.id,
                    status=Status.ACTIVE
                )

                new_act['sentence']['info_card'] = InfoCardModelSerializer(
                    card).data
                new_act['sentence']['info_card']['sentences'] = ResourceSentenceDetailSerializer(
                    sentences, many=True).data

                collocations = Collocation.objects.filter(
                    info_card=card.id,
                    status=Status.ACTIVE
                )

                collocationList = [col.text for col in collocations]
                new_act['sentence']['info_card']['collocations'] = collocationList

            if act['sentence'] and act['sentence']['short_video']:
                video = ShortVideo.objects.get(
                    id=act['sentence']['short_video'])
                sentences = ResourceSentence.objects.filter(
                    short_video=video.id,
                    status=Status.ACTIVE
                )
                new_act['sentence']['short_video'] = ShortVideoModelSerializer(
                    video).data
                new_act['sentence']['short_video']['sentences'] = ResourceSentenceDetailSerializer(
                    sentences, many=True).data

                collocations = Collocation.objects.filter(
                    short_video=video.id,
                    status=Status.ACTIVE
                )

                collocationList = [col.text for col in collocations]
                new_act['sentence']['short_video']['collocations'] = collocationList

            new_activities.append(new_act)

        except Exception as e:
            logger.exception(e)
            new_activities.append(act)
    return new_activities


def add_videos_and_cards_into_sentences(sentences):
    result = []
    for sen in sentences:
        new_sen = sen
        try:
            if sen['info_card']:
                card = InfoCard.objects.get(id=sen['info_card'])
                sentences = ResourceSentence.objects.filter(
                    info_card=card.id,
                    status=Status.ACTIVE
                )

                new_sen['info_card'] = InfoCardModelSerializer(
                    card).data
                new_sen['info_card']['sentences'] = ResourceSentenceDetailSerializer(
                    sentences, many=True).data

                collocations = Collocation.objects.filter(
                    info_card=card.id,
                    status=Status.ACTIVE
                )

                collocationList = [col.text for col in collocations]
                new_sen['info_card']['collocations'] = collocationList

            if sen['short_video']:
                video = ShortVideo.objects.get(id=sen['short_video'])
                sentences = ResourceSentence.objects.filter(
                    short_video=video.id,
                    status=Status.ACTIVE
                )
                new_sen['short_video'] = ShortVideoModelSerializer(
                    video).data
                new_sen['short_video']['sentences'] = ResourceSentenceDetailSerializer(
                    sentences, many=True).data

                collocations = Collocation.objects.filter(
                    short_video=video.id,
                    status=Status.ACTIVE
                )

                collocationList = [col.text for col in collocations]
                new_sen['short_video']['collocations'] = collocationList

            result.append(new_sen)

        except Exception as e:
            logger.exception(e)
            result.append(sen)
    return result


def get_easy_questions_with_examples(total):
    questions = list(Question.objects.filter(
        status=Status.ACTIVE,
        difficulty=Difficulty.EASY
    ))

    random.shuffle(questions)

    result = []
    ids = []
    counter = 0

    for q in questions:
        word_ids = q.words.all().values_list('id', flat=True)

        words = list(Word.objects.filter(
            status=Status.ACTIVE,
            difficulty=Difficulty.EASY,
            id__in=word_ids
        ))

        if len(words) == 0:
            continue

        random.shuffle(words)
        sentence = None

        for w in words:
            example = Example.objects.filter(
                status=Status.ACTIVE,
                question=q.id,
                sentence_text=w.word
            ).first()

            if example:
                counter += 1
                sentence = {
                    'id': -1,
                    'origin': SentenceOrigin.RANDOM,
                    'type': SentenceTypes.NORMAL,
                    'sentence': w.word,
                    'meaning': w.meaning
                }
                result.append({
                    'question': QuestionModelSerializer(q).data,
                    'sentence': sentence
                })
                ids.append(q.id)
                if counter == total:
                    break

        if counter == total:
            break

    return result, ids


def get_easy_questions(total):
    questions = Question.objects.filter(
        status=Status.ACTIVE,
        difficulty=Difficulty.EASY
    )
    questions = random.sample(list(questions), total)

    result = []
    ids = []

    for q in questions:
        ids.append(q.id)
        ids = q.words.all().values_list('id', flat=True)

        sentences = Word.objects.filter(
            status=Status.ACTIVE,
            difficulty=Difficulty.EASY,
            id__in=ids
        )

        sentence = None

        if len(sentences) > 0:
            sentence = random.choice(sentences)
            sentence = {
                'id': -1,
                'origin': SentenceOrigin.RANDOM,
                'type': SentenceTypes.NORMAL,
                'sentence': sentence.sentence,
                'meaning': sentence.meaning
            }

        result.append({
            'question': QuestionModelSerializer(q).data,
            'sentence': sentence
        })

    return result, ids


def get_random_questions(excluded_ids, total):
    questions = Question.objects.filter(
        status=Status.ACTIVE).exclude(id__in=excluded_ids)
    questions = random.sample(list(questions), total)

    result = []

    for q in questions:
        ids = q.words.all().values_list('id', flat=True)

        words = Word.objects.filter(
            status=Status.ACTIVE,
            difficulty=Difficulty.EASY,
            id__in=ids
        )

        sentence = None

        if len(words) > 0:
            word = random.choice(words)
            sentence = {
                'id': -1,
                'origin': SentenceOrigin.RANDOM,
                'type': SentenceTypes.NORMAL,
                'sentence': word.word,
                'meaning': word.meaning
            }

        result.append({
            'question': QuestionModelSerializer(q).data,
            'sentence': sentence
        })

    return result


def convert_local_sentences_to_sentences(local_sentences):
    result = []
    for local in local_sentences:
        sentence = None

        if local.get('info_card', False):
            card = InfoCard.objects.get(id=local['info_card'])

            sentence = UserSentence(
                id=local['id'],
                sentence=local['sentence'],
                meaning=local['meaning'],
                origin=local['origin'],
                type=local['type'],
                source_type=local['source_type'],
                info_card=card
            )

        elif local.get('short_video', False):
            video = ShortVideo.objects.get(id=local['short_video'])

            sentence = UserSentence(
                id=local['id'],
                sentence=local['sentence'],
                meaning=local['meaning'],
                origin=local['origin'],
                type=local['type'],
                source_type=local['source_type'],
                short_video=video
            )

        else:
            sentence = UserSentence(
                id=local['id'],
                sentence=local['sentence'],
                meaning=local['meaning'],
                origin=local['origin'],
                type=local['type'],
                source_type=local['source_type']
            )

        if sentence:
            result.append(sentence)
    return result


def add_screen_flow(uuid, user_id, type):
    try:
        if uuid and not user_id:
            if(not is_valid_uuid(uuid)):
                return
            device, created = Device.objects.get_or_create(uuid=uuid)
            ScreenFlow(
                type=type,
                device=device
            ).save()

        if not uuid and not user_id:
            return

        if not uuid and user_id:
            devices = Device.objects.filter(
                user__id=user_id).order_by('-created')

            ScreenFlow(
                type=type,
                device=devices[0]
            ).save()

        if uuid and user_id:
            if(not is_valid_uuid(uuid)):
                return
            try:
                device = Device.objects.get(uuid=uuid, user__id=user_id)
            except Device.DoesNotExist:
                device = Device(
                    uuid=uuid,
                    user=User.objects.get(id=user_id)
                )
                device.save()
            ScreenFlow(
                type=type,
                device=device
            ).save()
    except:
        logger.error(traceback.format_exc())


def is_valid_uuid(value):
    try:
        uuid.UUID(str(value))

        return True
    except ValueError:
        return False


def get_sentences_by_card_id(id):
    sentences = ResourceSentence.objects.filter(
        info_card=id,
        status=Status.ACTIVE
    )
    return sentences


def get_collocations_by_card_id(id):
    collocations = Collocation.objects.filter(
        info_card=id,
        status=Status.ACTIVE
    )
    return [col.text for col in collocations]


def get_sentences_by_video_id(id):
    sentences = ResourceSentence.objects.filter(
        short_video=id,
        status=Status.ACTIVE
    )
    return sentences


def get_collocations_by_video_id(id):
    collocations = Collocation.objects.filter(
        short_video=id,
        status=Status.ACTIVE
    )
    return [col.text for col in collocations]
