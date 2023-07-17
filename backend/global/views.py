
# Framework
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import (
    api_view, renderer_classes
)
from rest_framework.renderers import JSONRenderer
from django.conf import settings


@api_view(['GET'])
@renderer_classes([JSONRenderer])
def global_config(request):

    mobile_app_verison = request.GET.get('version', '0.0.0')

    languages = [
        {
            'lang': 'es',
            'label': 'Spanish',
            'flag': settings.SITE_DOMAIN + '/media/flags/spanish_flag.png'
        },
        {
            'lang': 'zh-Hans',
            'label': 'Chinese',
            'flag': settings.SITE_DOMAIN + '/media/flags/chinese_flag.png'
        },
        {
            'lang': 'pt',
            'label': 'Portuguese',
            'flag': settings.SITE_DOMAIN + '/media/flags/portuguese_flag.png'
        },
        {
            'lang': 'ar',
            'label': 'Arabic',
            'flag': settings.SITE_DOMAIN + '/media/flags/arabic_flag.png'
        },
        {
            'lang': 'hi',
            'label': 'Hindi',
            'flag': settings.SITE_DOMAIN + '/media/flags/hindi_flag.png'
        },
    ]

    # langues = ['es', 'zh-Hans', 'pt', 'ar', 'hi']

    intro = [
        {
            "start": 0,
            "value": "Hey there! Let's do this fun quiz, okay?"
        },
        {
            "start": 2600,
            "value": "You can answer it any way you like, and there's no wrong answer!"
        },
        {
            "start": 6000,
            "value": "Use your imagination and come up with super cool words!"
        },
        {
            "start": 9300,
            "value": "And, umm, you have to talk and talk without stopping"
        },
        {
            "start": 12400,
            "value": "Just keep going!"
        },
        {
            "start": 13700,
            "value": "It's gonna be so much fun, you'll see!"
        }
    ]

    current_version = '1.0.2'

    data = {
        'mobile_app_verison': mobile_app_verison,
        'api_version': 'v1',
        'update_required': mobile_app_verison != current_version,
        'languages': languages,
        'intro': intro
    }

    return Response(data, status=status.HTTP_200_OK)
